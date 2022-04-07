import logging
import threading
from functools import lru_cache
from typing import Any, Callable, List, Optional, Union

import brownie
from brownie import chain, web3
from brownie.exceptions import CompilerError, ContractNotFound
from brownie.typing import AccountsType
from hexbytes import HexBytes
from multicall import Call, Multicall

from y import convert
from y.decorators import auto_retry, log
from y.exceptions import (ContractNotVerified, MessedUpBrownieContract,
                          NodeNotSynced, call_reverted, contract_not_verified)
from y.interfaces.ERC20 import ERC20ABI
from y.networks import Network
from y.typing import Address, AnyAddressType, Block
from y.utils.cache import memory

logger = logging.getLogger(__name__)


def Contract_erc20(address: AnyAddressType) -> brownie.Contract:
    address = convert.to_address(address)
    return Contract.from_abi('ERC20',address,ERC20ABI)


def Contract_with_erc20_fallback(address: AnyAddressType) -> brownie.Contract:
    if type(address) is brownie.Contract:
        return address
    address = convert.to_address(address)
    try:
        return Contract(address)
    except (ContractNotVerified,MessedUpBrownieContract):
        return Contract_erc20(address)


@log(logger)
@memory.cache()
def contract_creation_block(address: AnyAddressType, when_no_history_return_0: bool = False) -> int:
    """
    Determine the block when a contract was created using binary search.
    NOTE Requires access to historical state. Doesn't account for CREATE2 or SELFDESTRUCT.
    """
    address = convert.to_address(address)
    logger.info("contract creation block %s", address)
    height = chain.height

    if height == 0:
        raise NodeNotSynced(f'''
            `chain.height` returns 0 on your node, which means it is not fully synced.
            You can only use this function on a fully synced node.''')

    lo, hi = 0, height
    while hi - lo > 1:
        mid = lo + (hi - lo) // 2
        try:
            if get_code(address, mid):
                hi = mid
            else:
                lo = mid
        except ValueError as e:
            if 'missing trie node' in str(e):
                logger.critical('missing trie node, `contract_creation_block` may output a higher block than actual. Please try again using an archive node.')
                if when_no_history_return_0:
                    return 0
            elif 'Server error: account aurora does not exist while viewing' in str(e):
                logger.critical(str(e))
                if when_no_history_return_0:
                    return 0
            elif 'No state available for block' in str(e):
                logger.critical(str(e))
                if when_no_history_return_0:
                    return 0
            else:
                raise
            lo = mid
    return hi if hi != height else None

# cached Contract instance, saves about 20ms of init time
_contract_lock = threading.Lock()

@lru_cache
class Contract(brownie.Contract):
    @auto_retry
    def __init__(
        self, 
        address: AnyAddressType, 
        *args: Any, 
        owner: Optional[AccountsType] = None, 
        require_success: bool = True, 
        **kwargs: Any
        ) -> None:
        
        address = convert.to_address(address)
        
        with _contract_lock:
            try:
                try:
                    super().__init__(address, *args, owner=owner, **kwargs)
                    self._verified = True
                except AttributeError as e:
                    if "'UsingForDirective' object has no attribute 'typeName'" in str(e):
                        raise MessedUpBrownieContract(address, str(e))
                    raise
                except CompilerError as e:
                    raise MessedUpBrownieContract(address, str(e))
                except ConnectionError as e:
                    if '{"message":"Something went wrong.","result":null,"status":"0"}' in str(e):
                        if chain.id == Network.xDai:
                            raise ValueError(f'Rate limited by Blockscout. Please try again.')
                        if web3.eth.get_code(address):
                            raise ContractNotVerified(address)
                        else:
                            raise ContractNotFound(address)
                    raise
                except IndexError as e:
                    if 'list index out of range' in str(e):
                        raise MessedUpBrownieContract(address, str(e))
                    elif "pop from an empty deque" in str(e):
                        raise MessedUpBrownieContract(address, str(e))
                    else:
                        raise
                except ValueError as e:
                    if contract_not_verified(e):
                        raise ContractNotVerified(f'{address} on {Network.printable()}')
                    elif "Unknown contract address:" in str(e):
                        raise ContractNotVerified(str(e)) # avax snowtrace
                    elif "invalid literal for int() with base 16" in str(e):
                        raise MessedUpBrownieContract(address, str(e))
                    else:
                        raise
            except (ContractNotFound, ContractNotVerified, MessedUpBrownieContract) as e:
                if require_success:
                    raise
                if type(e) == ContractNotVerified:
                    self._verified = False
                else:
                    self._verified = None

    def has_method(self, method: str, return_response: bool = False) -> Union[bool,Any]:
        return has_method(self.address, method, return_response=return_response)

    def has_methods(
        self, 
        methods: List[str],
        func: Union[any, all] = all
    ) -> bool:
        return has_methods(self.address, methods, func)

    def build_name(self, return_None_on_failure: bool = False) -> Optional[str]:
        return build_name(self.address, return_None_on_failure=return_None_on_failure)
    
    def get_code(self, block: Optional[Block] = None) -> HexBytes:
        return get_code(self.address, block=block)


@log(logger)
@memory.cache()
def is_contract(address: AnyAddressType) -> bool:
    '''
    Checks to see if the input address is a contract. Returns `True` if:
    - The address is not and has never been a contract
    - The address used to be a contract but has self-destructed
    '''
    address = convert.to_address(address)
    return web3.eth.get_code(address) != '0x'

@log(logger)
@memory.cache()
def has_method(address: Address, method: str, return_response: bool = False) -> Union[bool,Any]:
    '''
    Checks to see if a contract has a `method` view method with no inputs.
    `return_response=True` will return `response` in bytes if `response` else `False`
    '''
    address = convert.to_address(address)
    try:
        response = Call(address, [method], [['key', None]])()['key']
    except Exception as e:
        if call_reverted(e):
            return False
        raise
    
    if response is None:
        return False
    if return_response:
        return response
    return True

@log(logger)
@memory.cache()
def has_methods(
    address: AnyAddressType, 
    methods: List[str],
    func: Callable = all # Union[any, all]
) -> bool:
    '''
    Checks to see if a contract has each view method (with no inputs) in `methods`.
    Pass `at_least_one=True` to only verify a contract has at least one of the methods.
    '''

    assert func in [all, any], '`func` must be either `any` or `all`'

    address = convert.to_address(address)
    calls = [Call(address, [method], [[method, None]]) for method in methods]
    try:
        response = Multicall(calls, require_success=False)().values()
        return func([False if call is None else True for call in response])
    except Exception as e:
        if not call_reverted(e): raise # and not out_of_gas(e): raise
        # Out of gas error implies one or more method is state-changing.
        # If `func == all` we return False because `has_methods` is only supposed to work for public view methods with no inputs
        # If `func == any` maybe one of the methods will work without "out of gas" error
        return False if func == all else any(has_method(address, method) for method in methods)


@log(logger)
def probe(
    address: AnyAddressType, 
    methods: List[str],
    block: Optional[Block] = None,
    return_method: bool = False
) -> Any:
    address = convert.to_address(address)
    calls = [Call(address, [method], [[method, None]]) for method in methods]
    results = Multicall(calls, block_id=block, require_success=False)()
    results = [(method, result) for method, result in results.items() if result is not None]
    assert len(results) in [1,0], '`probe` returned multiple results. Must debug'
    if len(results) == 1:
        method, result = results[0]
    else:
        method, result = None, None
    
    if method:
        assert result is not None

    if not return_method:
        return result
    else:
        return method, result
    


@log(logger)
@memory.cache()
def build_name(address: AnyAddressType, return_None_on_failure: bool = False) -> str:
    try:
        contract = Contract(address)
        return contract.__dict__['_build']['contractName']
    except ContractNotVerified:
        if not return_None_on_failure:
            raise
        return None

@auto_retry
def get_code(address: AnyAddressType, block: Optional[Block]) -> HexBytes:
    '''
    A simple wrapper on web3.eth.get_code that helps prevent issues with rate limiting on certain RPCs.
    '''
    return web3.eth.get_code(convert.to_address(address), block_identifier=block)

@auto_retry
def proxy_implementation(address: AnyAddressType, block: Optional[Block]) -> Address:
    return probe(address, ['implementation()(address)','target()(address)'], block)
