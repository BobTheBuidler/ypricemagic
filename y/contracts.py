import logging
import threading
from functools import lru_cache
from typing import Any, List, Optional, Union

from brownie import Contract as _Contract
from brownie import chain, web3
from brownie.exceptions import CompilerError, ContractNotFound
from brownie.typing import AccountsType
from multicall import Call, Multicall
from y.interfaces.ERC20 import ERC20ABI

from y.decorators import log
from y.exceptions import (ContractNotVerified, MessedUpBrownieContract,
                          call_reverted, contract_not_verified, out_of_gas)
from y.networks import Network
from y.utils.cache import memory

logger = logging.getLogger(__name__)


def Contract_erc20(address):
    return _Contract.from_abi('ERC20',address,ERC20ABI)


def Contract_with_erc20_fallback(address):
    try:
        contract = _Contract(address)
    except (AttributeError, CompilerError, IndexError, ValueError):
        contract = Contract_erc20(address)
    return contract


@log(logger)
@memory.cache()
def contract_creation_block(address) -> int:
    """
    Determine the block when a contract was created using binary search.
    NOTE Requires access to historical state. Doesn't account for CREATE2 or SELFDESTRUCT.
    """
    logger.info("contract creation block %s", address)
    height = chain.height
    lo, hi = 0, height
    while hi - lo > 1:
        mid = lo + (hi - lo) // 2
        try:
            if web3.eth.get_code(address, block_identifier=mid): hi = mid
            else: lo = mid
        except ValueError as e:
            if 'missing trie node' in str(e):
                logger.critical('missing trie node, `contract_creation_block` may output a higher block than actual. Please try again using an archive node.')
            elif 'Server error: account aurora does not exist while viewing' in str(e):
                logger.critical(str(e))
            else: raise
            lo = mid
    return hi if hi != height else None

# cached Contract instance, saves about 20ms of init time
_contract_lock = threading.Lock()

@lru_cache
class Contract(_Contract):
    def __init__(self, address: str, *args: Any, owner: Optional[AccountsType] = None, require_success: bool = True, **kwargs: Any) -> None:
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
                        if web3.eth.get_code(address): raise ContractNotVerified(address)
                        else: raise ContractNotFound(address)
                    raise
                except IndexError as e:
                    if 'list index out of range' in str(e): raise MessedUpBrownieContract(address, str(e))
                    elif "pop from an empty deque" in str(e): raise MessedUpBrownieContract(address, str(e))
                    else: raise
                except ValueError as e:
                    if contract_not_verified(e): raise ContractNotVerified(f'{address} on {Network.printable()}')
                    elif "Unknown contract address:" in str(e): raise ContractNotVerified(str(e)) # avax snowtrace
                    elif "invalid literal for int() with base 16" in str(e): raise MessedUpBrownieContract(address, str(e))
                    else: raise
            except (ContractNotFound, ContractNotVerified, MessedUpBrownieContract) as e:
                if require_success: raise
                if type(e) == ContractNotVerified: self._verified = False
                else: self._verified = None

    def has_method(self, method: str, return_response: bool = False) -> bool:
        return has_method(self.address, method, return_response=return_response)

    def has_methods(
        self, 
        methods: List[str],
        func: Union[any, all] = all
    ) -> bool:
        return has_methods(self.address, methods, func)

    def build_name(self, return_None_on_failure: bool = False) -> str:
        return build_name(self.address, return_None_on_failure=return_None_on_failure)

@log(logger)
@memory.cache()
def is_contract(address: str) -> bool:
    '''
    Checks to see if the input address is a contract. Returns `True` if:
    - The address is not and has never been a contract
    - The address used to be a contract but has self-destructed
    '''
    return web3.eth.get_code(address) != '0x'

@log(logger)
@memory.cache()
def has_method(address: str, method: str, return_response: bool = False) -> bool:
    '''
    Checks to see if a contract has a `method` view method with no inputs.
    `return_response=True` will return `response` in bytes if `response` else `False`
    '''
    try: response = Call(address, [method], [['key', None]], _w3=web3)()['key']
    except Exception as e:
        if call_reverted(e): return False
        # We return False here because `has_method` is only supposed to work for public view methods with no inputs
        # Out of gas error implies method is state-changing. Therefore the contract does not have a public view method called `method`
        if out_of_gas(e): return False
        raise
    
    if response is None: return False
    if return_response: return response
    return True

@log(logger)
@memory.cache()
def has_methods(
    address: str, 
    methods: List[str],
    func: Union[any, all] = all
) -> bool:
    '''
    Checks to see if a contract has each view method (with no inputs) in `methods`.
    Pass `at_least_one=True` to only verify a contract has at least one of the methods.
    '''

    assert func in [all, any], '`func` must be either `any` or `all`'

    calls = [Call(address, [method], [[method, None]]) for method in methods]
    try:
        response = Multicall(calls, _w3=web3, require_success=False)().values()
        return func([False if call is None else True for call in response])
    except Exception as e:
        if not call_reverted(e) and not out_of_gas(e): raise
        # Out of gas error implies one or more method is state-changing.
        # If `func == all` we return False because `has_methods` is only supposed to work for public view methods with no inputs
        # If `func == any` maybe one of the methods will work without "out of gas" error
        return False if func == all else any(has_method(address, method) for method in methods)


@log(logger)
def probe(
    address: str, 
    methods: List[str],
    block: int = None,
    return_method: bool = False
) -> Any:
    calls = [Call(address, [method], [[method, None]]) for method in methods]
    results = Multicall(calls, block_id=block, _w3=web3, require_success=False)()
    results = [(method, result) for method, result in results.items() if result is not None]
    assert len(results) in [1,0], '`probe` returned multiple results. Must debug'
    if len(results) == 1:
        method, result = results[0]
        if not return_method: return result
        else: return method, result


@log(logger)
@memory.cache()
def build_name(address: str, return_None_on_failure: bool = False) -> str:
    try:
        contract = Contract(address)
        return contract.__dict__['_build']['contractName']
    except ContractNotVerified:
        if return_None_on_failure: return None
        else: raise
