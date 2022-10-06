
import asyncio
import json
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import brownie
import eth_retry
from async_lru import alru_cache
from brownie import chain, web3
from brownie.exceptions import ContractNotFound
from brownie.network.contract import (_add_deployment, _ContractBase,
                                      _DeployedContractBase,
                                      _fetch_from_explorer, _resolve_address)
from brownie.typing import AccountsType
from checksum_dict import ChecksumAddressDict, ChecksumAddressSingletonMeta
from dank_mids.brownie_patch import patch_contract
from hexbytes import HexBytes
from multicall import Call
from multicall.utils import await_awaitable, gather

from y import convert
from y.datatypes import Address, AnyAddressType, Block
from y.exceptions import (ContractNotVerified, NodeNotSynced, call_reverted,
                          contract_not_verified)
from y.interfaces.ERC20 import ERC20ABI
from y.networks import Network
from y.utils.cache import memory
from y.utils.dank_mids import dank_w3
from y.utils.logging import yLazyLogger

logger = logging.getLogger(__name__)

contract_threads = ThreadPoolExecutor(16)


# cached Contract instance, saves about 20ms of init time
_contract_lock = threading.Lock()

# These tokens have trouble when resolving the implementation via the chain.
FORCE_IMPLEMENTATION = {
    Network.Mainnet: {
        "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48": "0xa2327a938Febf5FEC13baCFb16Ae10EcBc4cbDCF", # USDC as of 2022-08-10
    },
}.get(chain.id, {})


def Contract_erc20(address: AnyAddressType) -> "Contract":
    address = convert.to_address(address)
    return Contract.from_abi('ERC20',address,ERC20ABI)


def Contract_with_erc20_fallback(address: AnyAddressType) -> "Contract":
    if isinstance(address, Contract):
        return address
    address = convert.to_address(address)
    try:
        return Contract(address)
    except ContractNotVerified:
        return Contract_erc20(address)


@memory.cache()
#yLazyLogger(logger)
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
            if web3.eth.get_code(address, mid):
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


class Contract(brownie.Contract, metaclass=ChecksumAddressSingletonMeta):
    _ChecksumAddressSingletonMeta__instances: ChecksumAddressDict["Contract"]

    @eth_retry.auto_retry
    def __init__(
        self, 
        address: AnyAddressType, 
        owner: Optional[AccountsType] = None, 
        require_success: bool = True, 
        ) -> None:
        
        address = str(address)
        if address.lower() == "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee":
            raise ContractNotFound(f"{address} is not a contract.")

        with _contract_lock:
            # autofetch-sources: false
            # Try to fetch the contract from the local sqlite db.
            try:
                super().__init__(address, owner=owner)
                self.verified = True
            # If we don't already have the contract in the db, we'll try to fetch it from the explorer.
            except ValueError as e:
                try:                  
                    name, abi = _resolve_proxy(address)
                    build = {"abi": abi, "address": address, "contractName": name, "type": "contract"}
                    self.__init_from_abi__(build, owner=owner, persist=True)
                except (ContractNotFound, ContractNotVerified) as e:
                    if require_success:
                        raise
                    if type(e) == ContractNotVerified:
                        self._verified = False
                    else:
                        self._verified = None
        
        patch_contract(self, dank_w3)   # Patch the Contract with coroutines for each method.
        _squeeze(self)                  # Get rid of unnecessary memory-hog properties

    @classmethod
    def from_abi(
        cls,
        name: str,
        address: str,
        abi: List,
        owner: Optional[AccountsType] = None,
        persist: bool = True,
        ) -> "Contract":
        self = cls.__new__(cls)
        build = {"abi": abi, "address": _resolve_address(address), "contractName": name, "type": "contract"}
        self.__init_from_abi__(build, owner, persist)
        patch_contract(self, dank_w3)   # Patch the Contract with coroutines for each method.
        _squeeze(self)                  # Get rid of unnecessary memory-hog properties
        return self
    
    @classmethod
    async def coroutine(
        cls, 
        address: AnyAddressType, 
        ) -> "Contract":
        try:
            return Contract._ChecksumAddressSingletonMeta__instances[address]
        except KeyError:
            return await asyncio.get_event_loop().run_in_executor(contract_threads, Contract, address)
    
    def __init_from_abi__(self, build: Dict, owner: Optional[AccountsType] = None, persist: bool = True) -> None:
        _ContractBase.__init__(self, None, build, {})  # type: ignore
        _DeployedContractBase.__init__(self, build['address'], owner, None)
        if persist:
            _add_deployment(self)
        self.verified = True
        return self

    def has_method(self, method: str, return_response: bool = False) -> Union[bool,Any]:
        return has_method(self.address, method, return_response=return_response)

    def has_methods(
        self, 
        methods: List[str],
        _func: Union[any, all] = all
    ) -> bool:
        return await_awaitable(self.has_methods_async(methods, _func))

    async def has_methods_async(
        self, 
        methods: List[str],
        _func: Union[any, all] = all
    ) -> bool:
        return await has_methods_async(self.address, methods, _func)

    def build_name(self, return_None_on_failure: bool = False) -> Optional[str]:
        return await_awaitable(self.build_name_async(return_None_on_failure=return_None_on_failure))

    async def build_name_async(self, return_None_on_failure: bool = False) -> Optional[str]:
        return await build_name_async(self.address, return_None_on_failure=return_None_on_failure)
    
    def get_code(self, block: Optional[Block] = None) -> HexBytes:
        return web3.eth.get_code(self.address, block=block)


@memory.cache()
#yLazyLogger(logger)
def is_contract(address: AnyAddressType) -> bool:
    '''
    Checks to see if the input address is a contract. Returns `True` if:
    - The address is not and has never been a contract
    - The address used to be a contract but has self-destructed
    '''
    address = convert.to_address(address)
    return web3.eth.get_code(address) not in ['0x',b'']

def has_method(address: Address, method: str, return_response: bool = False) -> Union[bool,Any]:
    return await_awaitable(has_method_async(address, method, return_response=return_response))

#yLazyLogger(logger)
@alru_cache(maxsize=None)
#@memory.cache()
async def has_method_async(address: Address, method: str, return_response: bool = False) -> Union[bool,Any]:
    '''
    Checks to see if a contract has a `method` view method with no inputs.
    `return_response=True` will return `response` in bytes if `response` else `False`
    '''
    address = convert.to_address(address)
    try:
        response = await Call(address, [method], [['key', None]]).coroutine()
        response = response['key']
    except Exception as e:
        if call_reverted(e):
            return False
        raise
    
    if response is None:
        return False
    if return_response:
        return response
    return True

def has_methods(
    address: AnyAddressType, 
    methods: Tuple[str],
    _func: Callable = all # Union[any, all]
) -> bool:
    return await_awaitable(has_methods_async(address,methods,_func=_func))

#yLazyLogger(logger)
@alru_cache(maxsize=None)
async def has_methods_async(
    address: AnyAddressType, 
    methods: Tuple[str],
    _func: Callable = all # Union[any, all]
) -> bool:
    '''
    Checks to see if a contract has each view method (with no inputs) in `methods`.
    Pass `at_least_one=True` to only verify a contract has at least one of the methods.
    '''

    assert _func in [all, any], '`_func` must be either `any` or `all`'

    address = convert.to_address(address)
    try:
        return _func([
            False if call is None else True
            for call
            in await gather([Call(address, [method]).coroutine() for method in methods])
        ])
    except Exception as e:
        if not call_reverted(e): raise # and not out_of_gas(e): raise
        # Out of gas error implies one or more method is state-changing.
        # If `_func == all` we return False because `has_methods` is only supposed to work for public view methods with no inputs
        # If `_func == any` maybe one of the methods will work without "out of gas" error
        return False if _func == all else any(await gather([has_method_async(address, method) for method in methods]))


#yLazyLogger(logger)
async def probe(
    address: AnyAddressType, 
    methods: List[str],
    block: Optional[Block] = None,
    return_method: bool = False
) -> Any:
    address = convert.to_address(address)
    results = await asyncio.gather(*[Call(address, [method], block_id=block).coroutine() for method in methods], return_exceptions=True)
    results = [(method, result) for method, result in zip(methods, results) if not isinstance(result, Exception) and result is not None]
    if len(results) not in [1,0]:
        if len(results) == 2 and results[0][1] == results[1][1]:
            method = results[0][0], results[1][0]
            result = results[0][1]
        else:
            raise AssertionError(f'`probe` returned multiple results for {address}: {results}. Must debug')
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
    


@memory.cache()
#yLazyLogger(logger)
def build_name(address: AnyAddressType, return_None_on_failure: bool = False) -> str:
    return await_awaitable(build_name_async(address, return_None_on_failure=return_None_on_failure))

async def build_name_async(address: AnyAddressType, return_None_on_failure: bool = False) -> str:
    try:
        contract = await Contract.coroutine(address)
        return contract.__dict__['_build']['contractName']
    except ContractNotVerified:
        if not return_None_on_failure:
            raise
        return None

async def proxy_implementation(address: AnyAddressType, block: Optional[Block]) -> Address:
    return await probe(address, ['implementation()(address)','target()(address)'], block)

def _squeeze(it):
    """ Reduce the contract size in RAM significantly. """
    for k in ["ast", "bytecode", "coverageMap", "deployedBytecode", "deployedSourceMap", "natspec", "opcodes", "pcMap"]:
        if it._build and k in it._build.keys():
            it._build[k] = {}
    return it


def _extract_abi_data(address):
    try:
        data = _fetch_from_explorer(address, "getsourcecode", False)
    except ConnectionError as e:
        if '{"message":"Something went wrong.","result":null,"status":"0"}' in str(e):
            if chain.id == Network.xDai:
                raise ValueError(f'Rate limited by Blockscout. Please try again.')
            if web3.eth.get_code(address):
                raise ContractNotVerified(address)
            else:
                raise ContractNotFound(address)
        raise
    except ValueError as e:
        if contract_not_verified(e):
            raise ContractNotVerified(f'{address} on {Network.printable()}')
        elif "Unknown contract address:" in str(e):
            if not is_contract(address):
                raise ContractNotFound(str(e))
            raise ContractNotVerified(str(e)) # avax snowtrace
        else:
            raise
    
    is_verified = bool(data["result"][0].get("SourceCode"))
    if not is_verified:
        raise ContractNotVerified(f"Contract source code not verified: {address}")
    name = data["result"][0]["ContractName"]
    abi = json.loads(data["result"][0]["ABI"])
    implementation = data["result"][0]["Implementation"]
    return name, abi, implementation

@eth_retry.auto_retry
def _resolve_proxy(address) -> Tuple[str, List]:
    address = convert.to_address(address)
    name, abi, implementation = _extract_abi_data(address)
    as_proxy_for = None

    if address in FORCE_IMPLEMENTATION:
        implementation = FORCE_IMPLEMENTATION[address]
        name, abi, _ = _extract_abi_data(implementation)
        return name, abi

    # always check for an EIP1967 proxy - https://eips.ethereum.org/EIPS/eip-1967
    implementation_eip1967 = web3.eth.get_storage_at(
        address, int(web3.keccak(text="eip1967.proxy.implementation").hex(), 16) - 1
    )
    # always check for an EIP1822 proxy - https://eips.ethereum.org/EIPS/eip-1822
    implementation_eip1822 = web3.eth.get_storage_at(address, web3.keccak(text="PROXIABLE"))

    # Just leave this code where it is for a helpful debugger as needed.
    if address == "":
        raise Exception(
            f"""implementation: {implementation}
            implementation_eip1967: {len(implementation_eip1967)} {implementation_eip1967}
            implementation_eip1822: {len(implementation_eip1822)} {implementation_eip1822}""")

    if len(implementation_eip1967) > 0 and int(implementation_eip1967.hex(), 16):
        as_proxy_for = _resolve_address(implementation_eip1967[-20:])
    elif len(implementation_eip1822) > 0 and int(implementation_eip1822.hex(), 16):
        as_proxy_for = _resolve_address(implementation_eip1822[-20:])
    elif implementation:
        # for other proxy patterns, we only check if etherscan indicates
        # the contract is a proxy. otherwise we could have a false positive
        # if there is an `implementation` method on a regular contract.
        try:
            # first try to call `implementation` per EIP897
            # https://eips.ethereum.org/EIPS/eip-897
            c = Contract.from_abi(name, address, abi)
            as_proxy_for = c.implementation.call()
        except Exception:
            # if that fails, fall back to the address provided by etherscan
            as_proxy_for = _resolve_address(implementation)

    if as_proxy_for:
        name, abi, _ = _extract_abi_data(as_proxy_for)
    return name, abi
