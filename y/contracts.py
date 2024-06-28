
import asyncio
import json
import logging
import threading
from collections import defaultdict
from contextlib import suppress
from typing import Any, Callable, Dict, List, Literal, NewType, Optional, Set, Tuple, Union

import a_sync
import dank_mids
import eth_retry
from brownie import ZERO_ADDRESS, chain, web3
from brownie.exceptions import CompilerError, ContractNotFound
from brownie.network.contract import (ContractEvents, _add_deployment,
                                      _ContractBase, _DeployedContractBase,
                                      _fetch_from_explorer, _resolve_address)
from brownie.typing import AccountsType
from checksum_dict import ChecksumAddressDict, ChecksumAddressSingletonMeta
from hexbytes import HexBytes
from multicall import Call
from typing_extensions import Self
from web3.exceptions import ContractLogicError

from y import ENVIRONMENT_VARIABLES as ENVS
from y import convert, exceptions
from y._decorators import stuck_coro_debugger
from y.datatypes import Address, AnyAddressType, Block
from y.interfaces.ERC20 import ERC20ABI
from y.networks import Network
from y.time import check_node, check_node_async
from y.utils.cache import memory
from y.utils.events import Events
from y.utils.gather import gather_methods

logger = logging.getLogger(__name__)

contract_threads = a_sync.PruningThreadPoolExecutor(16)

# cached Contract instance, saves about 20ms of init time
_contract_lock = threading.Lock()

# These tokens have trouble when resolving the implementation via the chain.
FORCE_IMPLEMENTATION = {
    Network.Mainnet: {
        "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48": "0xa2327a938Febf5FEC13baCFb16Ae10EcBc4cbDCF", # USDC as of 2022-08-10
        "0x3d1E5Cf16077F349e999d6b21A4f646e83Cd90c5": "0xf51fC5ae556F5B8c6dCf50f70167B81ceb02a2b2", # dETH as of 2024-02-15
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
    except exceptions.ContractNotVerified:
        return Contract_erc20(address)


@memory.cache()
#yLazyLogger(logger)
def contract_creation_block(address: AnyAddressType, when_no_history_return_0: bool = False) -> int:
    """
    Determine the block when a contract was created using binary search.
    NOTE Requires access to historical state. Doesn't account for CREATE2 or SELFDESTRUCT.
    """
    address = convert.to_address(address)
    logger.debug("contract creation block %s", address)
    height = chain.height

    if height == 0:
        raise exceptions.NodeNotSynced(_NOT_SYNCED)
    
    check_node()

    lo, hi = 0, height
    barrier = 0
    warned = False
    while hi - lo > 1:
        mid = lo + (hi - lo) // 2
        # TODO rewrite this so we can get deploy blocks for some contracts deployed on correct side of barrier
        try:
            if eth_retry.auto_retry(web3.eth.get_code)(address, mid):
                hi = mid
            else:
                lo = mid
        except ValueError as e:
            if 'missing trie node' in str(e) and not warned:
                logger.warning('missing trie node, `contract_creation_block` may output a higher block than actual. Please try again using an archive node.')
            elif 'Server error: account aurora does not exist while viewing' in str(e):
                if not warned:
                    logger.warning(str(e))
            elif 'No state available for block' in str(e):
                if not warned:
                    logger.warning(str(e))
            else:
                raise
            warned = True
            barrier = mid
            lo = mid
    if hi == lo + 1 == barrier + 1 and when_no_history_return_0:
        logger.warning('could not determine creation block for %s on %s (deployed prior to barrier)', address, Network.name())
        logger.debug("contract creation block %s -> 0", address)
        return 0
    if hi != height:
        logger.debug("contract creation block %s -> %s", address, hi)
        return hi
    raise ValueError(f"Unable to find deploy block for {address} on {Network.name()}")

get_code = eth_retry.auto_retry(dank_mids.eth.get_code)
creation_block_semaphore = a_sync.ThreadsafeSemaphore(10)

@a_sync.a_sync(cache_type='memory')
@stuck_coro_debugger
@eth_retry.auto_retry
async def contract_creation_block_async(address: AnyAddressType, when_no_history_return_0: bool = False) -> int:
    """
    Determine the block when a contract was created using binary search.
    NOTE Requires access to historical state. Doesn't account for CREATE2 or SELFDESTRUCT.
    """
    from y._db.utils import contract as db

    address = convert.to_address(address)
    if deploy_block := await db.get_deploy_block(address):
        return deploy_block
    
    logger.debug(f"contract creation block {address}")
    height = await dank_mids.eth.block_number

    if height == 0:
        raise exceptions.NodeNotSynced(_NOT_SYNCED)
    
    await check_node_async()

    lo, hi = 0, height
    barrier = 0
    warned = False
    while hi - lo > 1:
        mid = lo + (hi - lo) // 2
        # TODO rewrite this so we can get deploy blocks for some contracts deployed on correct side of barrier
        try:
            if await get_code(address, mid):
                hi = mid
            else:
                lo = mid
        except ValueError as e:
            if 'missing trie node' in str(e):
                if not warned:
                    logger.warning('missing trie node, `contract_creation_block` may output a higher block than actual. Please try again using an archive node.')
            elif 'Server error: account aurora does not exist while viewing' in str(e):
                if not warned:
                    logger.warning(str(e))
            elif 'No state available for block' in str(e):
                if not warned:
                    logger.warning(str(e))
            else:
                raise
            warned = True
            barrier = mid
            lo = mid
    if hi == lo + 1 == barrier + 1 and when_no_history_return_0:
        logger.warning(f'could not determine creation block for {address} on {Network.name()} (deployed prior to barrier)')
        logger.debug(f"contract creation block {address} -> 0")
        return 0
    if hi != height:
        logger.debug(f"contract creation block {address} -> {hi}")
        db.set_deploy_block(address, hi)
        return hi
    raise ValueError(f"Unable to find deploy block for {address} on {Network.name()}")


# this defaultdict prevents congestion in the contracts thread pool
address_semaphores = defaultdict(lambda: a_sync.ThreadsafeSemaphore(1))

class ContractEvents(ContractEvents):
    def __getattr__(self, name: str) -> Events:
        return super().__getattr__(name)
    
class Contract(dank_mids.Contract, metaclass=ChecksumAddressSingletonMeta):
    """
    Though it may look complicated, a ypricemagic Contract object is simply a brownie Contract object with a few modifications:
    1. Contracts will not be compiled. This allows you to more quickly fetch contracts from the block explorer and prevents you from having to download and install compilers.
    2. To each contract method, a `coroutine` property has been defined which allows you to make asynchronous calls using the following syntax:
    ```python
    Contract(0xAddress).methodName.coroutine(*args, block_identifier=12345678)
    ```
    3. A few attributes were removed in order to minimize the size of a Contract object in memory: 
        - ast, bytecode, coverageMap, deployedBytecode, deployedSourceMap, natspec, opcodes, pcMap
    4. There are a few new util methods but they're not officially supported yet and may change without warning:
        - has_method
        - has_methods
        - has_methods_async
        - build_name
        - build_name_async
        - get_code
    """
    # the default state for Contract objects
    verified = True

    events: ContractEvents
    _ChecksumAddressSingletonMeta__instances: ChecksumAddressDict["Contract"]

    @eth_retry.auto_retry
    def __init__(
        self, 
        address: AnyAddressType, 
        owner: Optional[AccountsType] = None, 
        require_success: bool = True, 
        cache_ttl: Optional[int] = ENVS.CONTRACT_CACHE_TTL,  # units: seconds
    ) -> None:
        
        address = str(address)
        if address.lower() in ["0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee", ZERO_ADDRESS]:
            raise ContractNotFound(f"{address} is not a contract.")
        if require_success and address in _unverified:
            raise exceptions.ContractNotVerified(address)

        with _contract_lock:
            # autofetch-sources: false
            # Try to fetch the contract from the local sqlite db.
            try:
                super().__init__(address, owner=owner)
                if not isinstance(self.verified, bool) and self.verified is not None:
                    logger.warning(f'`Contract("{address}").verified` property will not be usable due to the contract having a `verified` method in its ABI.')
            except AssertionError as e:
                raise CompilerError("y.Contract objects work best when we bypass compilers. In this case, it will *only* work when we bypass. Please ensure autofetch_sources=False in your brownie-config.yaml and rerun your script.") from None
            except IndexError as e:
                if str(e) == "pop from an empty deque":
                    raise CompilerError("y.Contract objects work best when we bypass compilers. In this case, it will *only* work when we bypass. Please ensure autofetch_sources=False in your brownie-config.yaml and rerun your script.") from None
                raise
            except ValueError as e:
                if not str(e).startswith("Unknown contract address: "):
                    raise
                logger.debug(f"{e}")
                try:                  
                    name, abi = _resolve_proxy(address)
                    build = {"abi": abi, "address": address, "contractName": name, "type": "contract"}
                    self.__init_from_abi__(build, owner=owner, persist=True)
                except exceptions.InvalidAPIKeyError:
                    # re-raise with a cleaner traceback
                    raise exceptions.InvalidAPIKeyError from None
                except (ContractNotFound, exceptions.ContractNotVerified) as e:
                    if isinstance(e, exceptions.ContractNotVerified):
                        _unverified.add(address)
                    if require_success:
                        raise
                    try:
                        if isinstance(e, exceptions.ContractNotVerified):
                            self.verified = False
                            self._build = {"contractName": "Non-Verified Contract"}
                        else:
                            self.verified = None
                            self._build = {"contractName": "Broken Contract"}
                    except AttributeError:
                        logger.warning(f'`Contract("{address}").verified` property will not be usable due to the contract having a `verified` method in its ABI.')
                # Patch the Contract with coroutines for each method.
                dank_mids.patch_contract(self)

        if self.verified:
            _setup_events(self)         # Init an event container for each topic
            _squeeze(self)              # Get rid of unnecessary memory-hog properties

            self._ttl_cache_popper: Union[Literal["disabled"], int, asyncio.TimerHandle]
            try:
                self._ttl_cache_popper = "disabled" if cache_ttl is None else asyncio.get_running_loop().call_later(cache_ttl, _pop, self._ChecksumAddressSingletonMeta__instances, self.address)
            except RuntimeError:
                self._ttl_cache_popper = cache_ttl

    @classmethod
    @a_sync.a_sync
    def from_abi(
        cls,
        name: str,
        address: str,
        abi: List,
        owner: Optional[AccountsType] = None,
        persist: bool = True,
        cache_ttl: Optional[int] = ENVS.CONTRACT_CACHE_TTL,  # units: seconds
    ) -> Self:
        self = cls.__new__(cls)
        build = {"abi": abi, "address": _resolve_address(address), "contractName": name, "type": "contract"}
        self.__init_from_abi__(build, owner, persist)
        dank_mids.patch_contract(self)  # Patch the Contract with coroutines for each method.
        _setup_events(self)             # Init an event container for each topic
        _squeeze(self)                  # Get rid of unnecessary memory-hog properties
        try:
            self._ttl_cache_popper = "disabled" if cache_ttl is None else asyncio.get_running_loop().call_later(cache_ttl, _pop, cls._ChecksumAddressSingletonMeta__instances, self.address)
        except RuntimeError:
            self._ttl_cache_popper = cache_ttl
        return self

    @classmethod
    async def coroutine(
        cls, 
        address: AnyAddressType, 
        require_success: bool = True, 
        cache_ttl: Optional[int] = ENVS.CONTRACT_CACHE_TTL,  # units: seconds
    ) -> Self:
        
        address = str(address)
        if contract := cls._ChecksumAddressSingletonMeta__instances.get(address, None):
            return contract
        # dict lookups faster than string comparisons, keep this behind the singleton check
        if address.lower() in ["0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee", ZERO_ADDRESS]:
            raise ContractNotFound(f"{address} is not a contract.") from None
        try:
            # We do this so we don't clog the threadpool with multiple jobs for the same contract.
            return await _contract_queue(address, require_success=require_success, cache_ttl=cache_ttl)
        except (ContractNotFound, exceptions.ExplorerError, CompilerError) as e:
            # re-raise with nicer traceback
            raise type(e)(*e.args) from None
    
    @classmethod
    @stuck_coro_debugger
    async def _coroutine(
        cls, 
        address: AnyAddressType, 
        require_success: bool = True, 
        cache_ttl: Optional[int] = ENVS.CONTRACT_CACHE_TTL,  # units: seconds
    ) -> Self:
        contract = await contract_threads.run(cls, address, require_success=require_success)

        if not contract.verified or contract._ttl_cache_popper == "disabled":
            pass
    
        elif cache_ttl is None:
            if isinstance(contract._ttl_cache_popper, asyncio.TimerHandle):
                contract._ttl_cache_popper.cancel()
            contract._ttl_cache_popper = "disabled"
    
        elif isinstance(contract._ttl_cache_popper, int):
            cache_ttl = max(contract._ttl_cache_popper, cache_ttl)
            contract._ttl_cache_popper = asyncio.get_running_loop().call_later(cache_ttl, _pop, cls._ChecksumAddressSingletonMeta__instances, contract.address)

        elif asyncio.get_running_loop().time() + cache_ttl > contract._ttl_cache_popper.when():
            contract._ttl_cache_popper.cancel()
            contract._ttl_cache_popper = asyncio.get_running_loop().call_later(cache_ttl, _pop, cls._ChecksumAddressSingletonMeta__instances, contract.address)
        return contract

    def __init_from_abi__(self, build: Dict, owner: Optional[AccountsType] = None, persist: bool = True) -> None:
        _ContractBase.__init__(self, None, build, {})  # type: ignore
        _DeployedContractBase.__init__(self, build['address'], owner, None)
        if persist:
            _add_deployment(self)
        try:
            self.verified = True
        except AttributeError:
            logger.warning(f'`Contract("{self.address}").verified` property will not be usable due to the contract having a `verified` method in its ABI.')
        return self

    def has_method(self, method: str, return_response: bool = False) -> Union[bool,Any]:
        return has_method(self.address, method, return_response=return_response, sync=False)

    async def has_methods(
        self, 
        methods: List[str],
        _func: Union[any, all] = all
    ) -> bool:
        return await has_methods(self.address, methods, _func, sync=False)

    async def build_name(self, return_None_on_failure: bool = False) -> Optional[str]:
        return await build_name(self.address, return_None_on_failure=return_None_on_failure, sync=False)
    
    async def get_code(self, block: Optional[Block] = None) -> HexBytes:
        return await get_code(self.address, block=block)

_contract_queue = a_sync.SmartProcessingQueue(Contract._coroutine, num_workers=32)

@memory.cache()
# TODO: async this and put it into ydb for quicker startups
#yLazyLogger(logger)
def is_contract(address: AnyAddressType) -> bool:
    '''
    Checks to see if the input address is a contract. Returns `False` if:
    - The address is not and has never been a contract
    - The address used to be a contract but has self-destructed
    '''
    address = convert.to_address(address)
    return web3.eth.get_code(address) not in ['0x',b'']

@a_sync.a_sync(default='sync', cache_type='memory')
async def has_method(address: Address, method: str, return_response: bool = False) -> Union[bool,Any]:
    '''
    Checks to see if a contract has a `method` view method with no inputs.
    `return_response=True` will return `response` in bytes if `response` else `False`
    '''
    address = convert.to_address(address)
    try:
        response = await Call(address, [method])
        return False if response is None else response if return_response else True
    except Exception as e:
        if isinstance(e, ContractLogicError) or exceptions.call_reverted(e):
            return False
        raise

@stuck_coro_debugger
@a_sync.a_sync(default='sync', cache_type='memory', ram_cache_ttl=15*60)
async def has_methods(
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
        return _func([result is not None for result in await gather_methods(address, methods)])
    except Exception as e:
        if not isinstance(e, ContractLogicError) and not exceptions.call_reverted(e): raise # and not out_of_gas(e): raise
        # Out of gas error implies one or more method is state-changing.
        # If `_func == all` we return False because `has_methods` is only supposed to work for public view methods with no inputs
        # If `_func == any` maybe one of the methods will work without "out of gas" error
        return False if _func == all else any(await asyncio.gather(*[has_method(address, method, sync=False) for method in methods]))


#yLazyLogger(logger)
@stuck_coro_debugger
async def probe(
    address: AnyAddressType, 
    methods: List[str],
    block: Optional[Block] = None,
    return_method: bool = False
) -> Any:
    address = convert.to_address(address)
    results = await gather_methods(address, methods, block=block, return_exceptions=True)
    logger.debug('probe results: %s', results)
    results = [(method, result) for method, result in zip(methods, results) if not isinstance(result, Exception) and result is not None]
    if len(results) not in [1,0]:
        logger.debug('multiple results: %s', results)
        if len(results) != 2 or results[0][1] != results[1][1]:
            raise AssertionError(f'`probe` returned multiple results for {address}: {results}. Must debug')
        method = results[0][0], results[1][0]
        result = results[0][1]
        results = [(method, result)]
        logger.debug('final results: %s', results)
    method, result = results[0] if len(results) == 1 else (None, None)
    if method:
        assert result is not None
    return (method, result) if return_method else result
    

@a_sync.a_sync(default='sync')
@stuck_coro_debugger
async def build_name(address: AnyAddressType, return_None_on_failure: bool = False) -> str:
    try:
        contract = await Contract.coroutine(address)
        return contract.__dict__['_build']['contractName']
    except exceptions.ContractNotVerified:
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

@eth_retry.auto_retry
def _extract_abi_data(address):
    try:
        data = _fetch_from_explorer(address, "getsourcecode", False)["result"][0]
    except ConnectionError as e:
        if '{"message":"Something went wrong.","result":null,"status":"0"}' in str(e):
            if chain.id == Network.xDai:
                raise ValueError('Rate limited by Blockscout. Please try again.') from e
            if web3.eth.get_code(address):
                raise exceptions.ContractNotVerified(address) from e
            else:
                raise ContractNotFound(address) from e
        raise
    except ValueError as e:
        if str(e).startswith("Failed to retrieve data from API") and "invalid api key" in str(e).lower():
            raise exceptions.InvalidAPIKeyError from e
        if exceptions.contract_not_verified(e):
            raise exceptions.ContractNotVerified(f'{address} on {Network.printable()}') from e
        elif "Unknown contract address:" in str(e):
            exc_type = exceptions.ContractNotVerified if is_contract(address) else ContractNotFound
            raise exc_type(str(e)) from e
        else:
            raise

    is_verified = bool(data.get("SourceCode"))
    if not is_verified:
        raise exceptions.ContractNotVerified(f"Contract source code not verified: {address}") from None
    name = data["ContractName"]
    abi = json.loads(data["ABI"])
    implementation = data.get("Implementation")
    return name, abi, implementation

def _resolve_proxy(address) -> Tuple[str, List]:
    address = convert.to_address(address)
    name, abi, implementation = _extract_abi_data(address)
    as_proxy_for = None

    if address in FORCE_IMPLEMENTATION:
        implementation = FORCE_IMPLEMENTATION[address]
        name, implementation_abi, _ = _extract_abi_data(implementation)
        # Here we merge the proxy ABI with the implementation ABI
        # without doing this, we'd only get the implementation
        # and would lack any valid methods/events from the proxy itself.
        # Credit: Wavey@Yearn
        abi += implementation_abi
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

def _setup_events(contract: Contract) -> None:
    """Helper function used to init contract event containers on a newly created `y.Contract` object."""
    if not hasattr(contract, 'events'):
        contract.events = ContractEvents(contract)
    for k, v in contract.topics.items():
        setattr(contract.events, k, Events(addresses=[contract.address], topics=[[v]]))

def _pop(d: dict, k: Any) -> None:
    """Pops an item from a dict if present"""
    with suppress(KeyError):
        d.pop(k)

_Address = NewType("_Address", str)
_unverified: Set[_Address] = set()
"""A collection of unverified addresses that is used to prevent repetitive etherscan api calls"""


_NOT_SYNCED = "`chain.height` returns 0 on your node, which means it is not fully synced."
_NOT_SYNCED += "\nYou can only use this function on a fully synced node."