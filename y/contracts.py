import asyncio
import logging
import threading
from collections import defaultdict
from functools import lru_cache
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Literal,
    NewType,
    Optional,
    Set,
    Tuple,
    Union,
)
from urllib.parse import urlparse

import a_sync
import aiohttp
import dank_mids
import eth_retry
from brownie import ZERO_ADDRESS, chain, web3
from brownie.exceptions import CompilerError, ContractNotFound
from brownie.network.contract import (
    ContractEvents,
    _add_deployment,
    _ContractBase,
    _DeployedContractBase,
    _fetch_from_explorer,
    _resolve_address,
)
from brownie.network.state import _get_deployment
from brownie.typing import AccountsType
from brownie.utils import color
from checksum_dict import ChecksumAddressDict, ChecksumAddressSingletonMeta
from hexbytes import HexBytes
from msgspec.json import decode
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

_brownie_deployments_db_lock = threading.Lock()
_contract_locks = defaultdict(asyncio.Lock)

# These tokens have trouble when resolving the implementation via the chain.
FORCE_IMPLEMENTATION = {
    Network.Mainnet: {
        "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48": "0xa2327a938Febf5FEC13baCFb16Ae10EcBc4cbDCF",  # USDC as of 2022-08-10
        "0x3d1E5Cf16077F349e999d6b21A4f646e83Cd90c5": "0xf51fC5ae556F5B8c6dCf50f70167B81ceb02a2b2",  # dETH as of 2024-02-15
    },
}.get(chain.id, {})


def Contract_erc20(address: AnyAddressType) -> "Contract":
    """
    Create a Contract instance for an ERC20 token.

    This function uses the standard ERC20 ABI instead of fetching the contract ABI from the block explorer.

    Args:
        address: The address of the ERC20 token.

    Returns:
        A Contract instance for the ERC20 token.
    """
    address = convert.to_address(address)
    return Contract.from_abi("ERC20", address, ERC20ABI)


def Contract_with_erc20_fallback(address: AnyAddressType) -> "Contract":
    """
    Create a Contract instance for an address, falling back to an ERC20 token if the contract is not verified.

    Args:
        address: The address of the contract or ERC20 token.

    Returns:
        A Contract instance for the contract address.
    """
    if isinstance(address, Contract):
        return address
    address = convert.to_address(address)
    try:
        return Contract(address)
    except exceptions.ContractNotVerified:
        return Contract_erc20(address)


@memory.cache()
# yLazyLogger(logger)
@eth_retry.auto_retry
def contract_creation_block(
    address: AnyAddressType, when_no_history_return_0: bool = False
) -> int:
    """
    Determine the block when a contract was created using binary search.
    NOTE Requires access to historical state. Doesn't account for CREATE2 or SELFDESTRUCT.

    Args:
        address: The address of the contract.
        when_no_history_return_0: If True, return 0 when no history is found instead of raising a :class:`~exceptions.NodeNotSynced` exception. Default False.

    Returns:
        The block number at which the contract was created.

    Raises:
        exceptions.NodeNotSynced: If the node is not fully synced.
        ValueError: If the contract creation block cannot be determined.
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
            if _get_code(address, mid):
                hi = mid
            else:
                lo = mid
        except ValueError as e:
            if "missing trie node" in str(e) and not warned:
                logger.warning(
                    "missing trie node, `contract_creation_block` may output a higher block than actual. Please try again using an archive node."
                )
            elif "Server error: account aurora does not exist while viewing" in str(e):
                if not warned:
                    logger.warning(str(e))
            elif "No state available for block" in str(e):
                if not warned:
                    logger.warning(str(e))
            else:
                raise
            warned = True
            barrier = mid
            lo = mid
    if hi == lo + 1 == barrier + 1 and when_no_history_return_0:
        logger.warning(
            "could not determine creation block for %s on %s (deployed prior to barrier)",
            address,
            Network.name(),
        )
        logger.debug("contract creation block %s -> 0", address)
        return 0
    if hi != height:
        logger.debug("contract creation block %s -> %s", address, hi)
        return hi
    raise ValueError(f"Unable to find deploy block for {address} on {Network.name()}")


get_code = eth_retry.auto_retry(dank_mids.eth.get_code)


@memory.cache
@eth_retry.auto_retry
def _get_code(address: str, block: int) -> HexBytes:
    return web3.eth.get_code(address, block)


creation_block_semaphore = a_sync.ThreadsafeSemaphore(10)


@a_sync.a_sync(cache_type="memory")
@stuck_coro_debugger
@eth_retry.auto_retry
async def contract_creation_block_async(
    address: AnyAddressType, when_no_history_return_0: bool = False
) -> int:
    """
    Determine the block when a contract was created using binary search.
    NOTE Requires access to historical state. Doesn't account for CREATE2 or SELFDESTRUCT.

    Args:
        address: The address of the contract.
        when_no_history_return_0: If True, return 0 when no history is found instead of raising a :class:`~exceptions.NodeNotSynced` exception. Default False.

    Returns:
        The block number at which the contract was created.

    Raises:
        exceptions.NodeNotSynced: If the node is not fully synced.
        ValueError: If the contract creation block cannot be determined.
    """
    from y._db.utils import contract as db

    address = await convert.to_address_async(address)
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
            if "missing trie node" in str(e):
                if not warned:
                    logger.warning(
                        "missing trie node, `contract_creation_block` may output a higher block than actual. Please try again using an archive node."
                    )
            elif "Server error: account aurora does not exist while viewing" in str(e):
                if not warned:
                    logger.warning(str(e))
            elif "No state available for block" in str(e):
                if not warned:
                    logger.warning(str(e))
            else:
                raise
            warned = True
            barrier = mid
            lo = mid
    if hi == lo + 1 == barrier + 1 and when_no_history_return_0:
        logger.warning(
            f"could not determine creation block for {address} on {Network.name()} (deployed prior to barrier)"
        )
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


class CompilerError(Exception):
    def __init__(self):
        super().__init__(
            "y.Contract objects work best when we bypass compilers.\n"
            "In this case, it will *only* work when we bypass.\n"
            "Please ensure autofetch_sources=False in your brownie-config.yaml and rerun your script."
        )


class Contract(dank_mids.Contract, metaclass=ChecksumAddressSingletonMeta):
    """
    Though it may look complicated, a ypricemagic Contract object is simply a brownie Contract object with a few modifications:

        1. Contracts will not be compiled. This allows you to more quickly fetch contracts from the block explorer and prevents you from having to download and install compilers.
            NOTE: You must set `autofetch_sources=false` in your project's brownie-config.yaml for this to work correctly.

        2. To each contract method, a `coroutine` property has been defined which allows you to make asynchronous calls which are intelligently batched in the background by :mod:`dank_mids` to reduce overhead.
            Example:
                >>> contract = Contract("0xAddress")
                >>> contract.methodName(*args, block_identifier=12345678)
                1000000000000000000
                >>> coro = contract.methodName.coroutine(*args, block_identifier=12345678)
                >>> coro
                <coroutine coroutine object at 0x12345678>
                >>> contract.methodName(*args, block_identifier=12345678) == await coro
                True

        3. New methods:
            - :meth:`~has_method`
            - :meth:`~has_methods`
            - :meth:`~build_name`
            - :meth:`~get_code`

        4. A few attributes were removed in order to minimize the size of a Contract object in memory:
            - :attr:`~ast`
            - :attr:`~bytecode`
            - :attr:`~coverageMap`
            - :attr:`~deployedBytecode`
            - :attr:`~deployedSourceMap`
            - :attr:`~natspec`
            - :attr:`~opcodes`
            - :attr:`~pcMap`
    """

    # the default state for Contract objects
    verified = True
    """True if the contract is verified on this network's block explorer. False otherwise."""

    events: ContractEvents
    """
    A container for various event types associated with this contract.
    
    Provides a convenient way to query contract events with minimal code.
    """

    _ttl_cache_popper: Union[Literal["disabled"], int, asyncio.TimerHandle]

    @eth_retry.auto_retry
    def __init__(
        self,
        address: AnyAddressType,
        owner: Optional[AccountsType] = None,
        require_success: bool = True,
        cache_ttl: Optional[int] = ENVS.CONTRACT_CACHE_TTL,  # units: seconds
    ) -> None:
        """
        Note:
            autofetch-sources: false
        """

        address = str(address)
        if address.lower() in [
            "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
            ZERO_ADDRESS,
        ]:
            raise ContractNotFound(f"{address} is not a contract.")
        if require_success and address in _unverified:
            raise exceptions.ContractNotVerified(address)

        try:
            # Try to fetch the contract from the local sqlite db.
            with _brownie_deployments_db_lock:
                super().__init__(address, owner=owner)
        except (AssertionError, IndexError) as e:
            if str(e) == "pop from an empty deque" or isinstance(e, AssertionError):
                raise CompilerError from None
            raise
        except ValueError as e:
            logger.debug(f"{e}")
            if not str(e).startswith("Unknown contract address: "):
                raise
        else:  # Nice, we got it from the db.
            if not isinstance(self.verified, bool) and self.verified is not None:
                logger.warning(
                    f'`Contract("{address}").verified` property will not be usable due to the contract having a `verified` method in its ABI.'
                )
            # schedule call to pop from cache
            self._schedule_cache_pop(cache_ttl)
            return

        # The contract does not exist in your local brownie deployments.db
        try:
            name, abi = _resolve_proxy(address)
            build = {
                "abi": abi,
                "address": address,
                "contractName": name,
                "type": "contract",
            }
            self.__init_from_abi__(build, owner=owner, persist=True)
            self.__post_init__(cache_ttl)
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
                logger.warning(
                    f'`Contract("{address}").verified` property will not be usable due to the contract having a `verified` method in its ABI.'
                )

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
        """
        Create a Contract instance from an ABI.

        Args:
            name: The name of the contract.
            address: The address of the contract.
            abi: The ABI of the contract.
            owner (optional): The owner of the contract. Default None.
            persist (optional): If True, persist the contract in brownie's local contract database. Default True.
            cache_ttl (optional): The time-to-live for the contract cache in seconds. Default set in :mod:`~y.ENVIRONMENT_VARIABLES`.

        Returns:
            A Contract instance for the given ABI.
        """
        self = cls.__new__(cls)
        build = {
            "abi": abi,
            "address": _resolve_address(address),
            "contractName": name,
            "type": "contract",
        }
        self.__init_from_abi__(build, owner, persist)
        self.__post_init__(cache_ttl)
        return self

    @classmethod
    @stuck_coro_debugger
    async def coroutine(
        cls,
        address: AnyAddressType,
        owner: Optional[AccountsType] = None,
        persist: bool = True,
        require_success: bool = True,
        cache_ttl: Optional[int] = ENVS.CONTRACT_CACHE_TTL,  # units: seconds
    ) -> Self:

        address = str(address)
        if contract := cls.get_instance(address):
            return contract

        # dict lookups faster than string comparisons, keep this behind the singleton check
        if address.lower() in [
            "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
            ZERO_ADDRESS,
        ]:
            raise ContractNotFound(f"{address} is not a contract.") from None

        contract = cls.__new__(cls)
        build, _ = await _get_deployment_from_db(address)

        if build:
            async with _contract_locks[address]:
                # now that we're inside the lock, check and see if another coro populated the cache
                if cache_value := cls.get_instance(address):
                    return cache_value

                # nope, continue
                contract.__init_from_abi__(build, owner=owner, persist=False)
                contract.__post_init__(cache_ttl)

        elif not CONFIG.active_network.get("explorer"):
            raise ValueError(f"Unknown contract address: '{address}'")

        else:
            try:
                # The contract does not exist in your local brownie deployments.db
                name, abi = await _resolve_proxy_async(address)
            except (ContractNotFound, exceptions.ContractNotVerified) as e:
                if not_verified := isinstance(e, exceptions.ContractNotVerified):
                    _unverified.add(address)
                if require_success:
                    raise
                try:
                    contract.verified = False if not_verified else None
                except AttributeError:
                    logger.warning(
                        '`Contract("%s").verified` property will not be usable due to the contract having a `verified` method in its ABI.',
                        address,
                    )
                contract._build = {
                    "contractName": (
                        "Non-Verified Contract" if not_verified else "Broken Contract"
                    )
                }

            else:
                async with _contract_locks[address]:
                    # now that we're inside the lock, check and see if another coro populated the cache
                    if cache_value := cls.get_instance(address):
                        return cache_value

                    # nope, continue
                    build = {
                        "abi": abi,
                        "address": address,
                        "contractName": name,
                        "type": "contract",
                    }
                    contract.__init_from_abi__(build, owner=owner, persist=persist)
                    contract.__post_init__(cache_ttl)

        # Cache manually since we aren't calling init
        cls[address] = contract

        # keep the dict small, we cache Contract instances so we won't need these in the future
        _contract_locks.pop(address, None)

        if not contract.verified or contract._ttl_cache_popper == "disabled":
            pass

        elif cache_ttl is None:
            if isinstance(contract._ttl_cache_popper, asyncio.TimerHandle):
                contract._ttl_cache_popper.cancel()
            contract._ttl_cache_popper = "disabled"

        elif isinstance(contract._ttl_cache_popper, int):
            cache_ttl = max(contract._ttl_cache_popper, cache_ttl)
            contract._ttl_cache_popper = asyncio.get_running_loop().call_later(
                cache_ttl,
                cls.delete_instance,
                contract.address,
                None,
            )

        elif (
            loop := asyncio.get_running_loop()
        ).time() + cache_ttl > contract._ttl_cache_popper.when():
            contract._ttl_cache_popper.cancel()
            contract._ttl_cache_popper = loop.call_later(
                cache_ttl,
                cls.delete_instance,
                contract.address,
                None,
            )
        return contract

    def __init_from_abi__(
        self, build: Dict, owner: Optional[AccountsType] = None, persist: bool = True
    ) -> None:
        """
        Initialize a Contract instance from an ABI.

        Args:
            build: The build information for the contract.
            owner (optional): The owner of the contract. Default None.
            persist (optional): If True, persist the contract in the local database. Default True.

        Returns:
            The initialized Contract instance.
        """
        _ContractBase.__init__(self, None, build, {})  # type: ignore
        _DeployedContractBase.__init__(self, build["address"], owner, None)
        if persist:
            _add_deployment(self)
        try:
            self.verified = True
        except AttributeError:
            logger.warning(
                f'`Contract("{self.address}").verified` property will not be usable due to the contract having a `verified` method in its ABI.'
            )
        return self

    def has_method(
        self, method: str, return_response: bool = False
    ) -> Union[bool, Any]:
        """
        Check if the contract has a specific method.

        Args:
            method: The name of the method to check for.
            return_response (optional): If True, return the response of the method call instead of a boolean. Default False.

        Returns:
            A boolean indicating whether the contract has the method, or the response of the method call if return_response is True.
        """
        return has_method(
            self.address, method, return_response=return_response, sync=False
        )

    async def has_methods(
        self, methods: List[str], _func: Union[any, all] = all
    ) -> bool:
        """
        Check if the contract has all the specified methods.

        Args:
            methods: A list of method names to check for.
            _func (optional): The function to use for combining the results (either :func:`all` or :func:`any`). Default :func:`all`.

        Returns:
            A boolean indicating whether the contract has all the specified methods.
        """
        return await has_methods(self.address, methods, _func, sync=False)

    async def build_name(self, return_None_on_failure: bool = False) -> Optional[str]:
        """
        Get the build name of the contract.

        Args:
            return_None_on_failure (optional): If True, return None if the build name cannot be determined instead of raising an Exception. Default False.

        Returns:
            The build name of the contract, or None if the build name cannot be determined and return_None_on_failure is True.
        """
        return await build_name(
            self.address, return_None_on_failure=return_None_on_failure, sync=False
        )

    async def get_code(self, block: Optional[Block] = None) -> HexBytes:
        """
        Get the bytecode of the contract at a specific block.

        Args:
            block (optional): The block number at which to get the bytecode. Defaults to latest block.

        Returns:
            The bytecode of the contract at the specified block.
        """
        return await get_code(self.address, block=block)

    def _schedule_cache_pop(self, cache_ttl: Optional[int]) -> None:
        if cache_ttl is None:
            self._ttl_cache_popper = "disabled"
            return

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # If the event loop isn't running yet we can just specify the cache_ttl for later use
            self._ttl_cache_popper = cache_ttl
            return

        self._ttl_cache_popper = loop.call_later(
            cache_ttl,
            type(self).delete_instance,
            self.address,
            None,
        )

    def __post_init__(self, cache_ttl: Optional[int] = None) -> None:
        super().__post_init__()

        # Init an event container for each topic
        _setup_events(self)

        # Get rid of unnecessary memory-hog properties
        _squeeze(self)

        # schedule call to pop from cache
        self._schedule_cache_pop(cache_ttl)


@memory.cache()
# TODO: async this and put it into ydb for quicker startups
# yLazyLogger(logger)
def is_contract(address: AnyAddressType) -> bool:
    """
    Checks to see if the input address is a contract. Returns `False` if:
    - The address is not and has never been a contract
    - The address used to be a contract but has self-destructed

    Args:
        address: The address to check.

    Returns:
        True if the address is a contract, False otherwise.
    """
    address = convert.to_address(address)
    return web3.eth.get_code(address) not in ["0x", b""]


@a_sync.a_sync(default="sync", cache_type="memory")
async def has_method(
    address: Address, method: str, return_response: bool = False
) -> Union[bool, Any]:
    """
    Checks to see if a contract has a `method` view method with no inputs.
    `return_response=True` will return `response` in bytes if `response` else `False`

    Args:
        address: The address of the contract.
        method: The name of the method to check for.
        return_response: If True, return the response of the method call instead of a boolean. Default False.

    Returns:
        A boolean indicating whether the contract has the method, or the response of the method call if return_response is True.
    """
    address = await convert.to_address_async(address)
    try:
        response = await Call(address, [method])
        return False if response is None else response if return_response else True
    except Exception as e:
        if (
            isinstance(e, ContractLogicError)
            or exceptions.call_reverted(e)
            or "invalid jump destination" in str(e)
        ):
            return False
        raise


@stuck_coro_debugger
@a_sync.a_sync(default="sync", cache_type="memory", ram_cache_ttl=15 * 60)
async def has_methods(
    address: AnyAddressType,
    methods: Tuple[str],
    _func: Callable = all,  # Union[any, all]
) -> bool:
    """
    Checks to see if a contract has each view method (with no inputs) in `methods`.
    Pass `at_least_one=True` to only verify a contract has at least one of the methods.

    Args:
        address: The address of the contract.
        methods: A tuple of method names to check for.
        _func: The function to use for combining the results (either :func:`all` or :func:`any`).

    Returns:
        A boolean indicating whether the contract has all the specified methods.
    """
    assert _func in [all, any], "`_func` must be either `any` or `all`"

    address = await convert.to_address_async(address)
    try:
        return _func(
            [result is not None for result in await gather_methods(address, methods)]
        )
    except Exception as e:
        if not isinstance(e, ContractLogicError) and not exceptions.call_reverted(e):
            raise  # and not out_of_gas(e): raise
        # Out of gas error implies one or more method is state-changing.
        # If `_func == all` we return False because `has_methods` is only supposed to work for public view methods with no inputs
        # If `_func == any` maybe one of the methods will work without "out of gas" error
        return (
            False
            if _func == all
            else any(
                await asyncio.gather(
                    *[has_method(address, method, sync=False) for method in methods]
                )
            )
        )


# yLazyLogger(logger)
@stuck_coro_debugger
async def probe(
    address: AnyAddressType,
    methods: List[str],
    block: Optional[Block] = None,
    return_method: bool = False,
) -> Any:
    address = await convert.to_address_async(address)
    results = await gather_methods(
        address, methods, block=block, return_exceptions=True
    )
    logger.debug("probe results: %s", results)
    results = [
        (method, result)
        for method, result in zip(methods, results)
        if not isinstance(result, Exception) and result is not None
    ]
    if len(results) not in [1, 0]:
        logger.debug("multiple results: %s", results)
        if len(results) != 2 or results[0][1] != results[1][1]:
            raise AssertionError(
                f"`probe` returned multiple results for {address}: {results}. Must debug"
            )
        method = results[0][0], results[1][0]
        result = results[0][1]
        results = [(method, result)]
        logger.debug("final results: %s", results)
    method, result = results[0] if len(results) == 1 else (None, None)
    if method:
        assert result is not None
    return (method, result) if return_method else result


@a_sync.a_sync(default="sync")
@stuck_coro_debugger
async def build_name(
    address: AnyAddressType, return_None_on_failure: bool = False
) -> str:
    """
    Get the build name of a contract.

    Args:
        address: The address of the contract.
        return_None_on_failure (optional): If True, return None if the build name cannot be determined instead of raising an Exception. Default False.

    Returns:
        The build name of the contract, or None if the build name cannot be determined and return_None_on_failure is True.
    """
    try:
        contract = await Contract.coroutine(address)
        return contract.__dict__["_build"]["contractName"]
    except exceptions.ContractNotVerified:
        if not return_None_on_failure:
            raise
        return None


async def proxy_implementation(
    address: AnyAddressType, block: Optional[Block]
) -> Address:
    """
    Get the implementation address for a proxy contract.

    Args:
        address: The address of the proxy contract.
        block: The block number at which to get the implementation address. Defaults to latest block.

    Returns:
        The address of the implementation contract.
    """
    return await probe(
        address, ["implementation()(address)", "target()(address)"], block
    )


_get_deployment_from_db = a_sync.SmartProcessingQueue(
    lambda address: ENVS.CONTRACT_THREADS.run(_get_deployment, address),
    num_workers=8,
)


def _squeeze(contract: Contract) -> Contract:
    """
    Reduce the contract size in RAM by removing large data structures from the build.

    Args:
        contract: The contract object to squeeze.

    Returns:
        The squeezed contract object.
    """
    for k in [
        "ast",
        "bytecode",
        "coverageMap",
        "deployedBytecode",
        "deployedSourceMap",
        "natspec",
        "opcodes",
        "pcMap",
    ]:
        if contract._build and k in contract._build.keys():
            contract._build[k] = {}
    return contract


@eth_retry.auto_retry
def _extract_abi_data(address: Address):
    """
    Extract ABI data for a contract from the blockchain explorer.

    Args:
        address: The address of the contract.

    Returns:
        A tuple containing the contract name, ABI, and implementation address (if applicable).

    Raises:
        Various exceptions based on the API response and contract status.
    """
    try:
        data = _fetch_from_explorer(address, "getsourcecode", False)["result"][0]
    except ConnectionError as e:
        if '{"message":"Something went wrong.","result":null,"status":"0"}' in str(e):
            if chain.id == Network.xDai:
                raise ValueError("Rate limited by Blockscout. Please try again.") from e
            if web3.eth.get_code(address):
                raise exceptions.ContractNotVerified(address) from e
            else:
                raise ContractNotFound(address) from e
        raise
    except ValueError as e:
        if (
            str(e).startswith("Failed to retrieve data from API")
            and "invalid api key" in str(e).lower()
        ):
            raise exceptions.InvalidAPIKeyError from e
        if exceptions.contract_not_verified(e):
            raise exceptions.ContractNotVerified(
                f"{address} on {Network.printable()}"
            ) from e
        elif "Unknown contract address:" in str(e):
            exc_type = (
                exceptions.ContractNotVerified
                if is_contract(address)
                else ContractNotFound
            )
            raise exc_type(str(e)) from e
        else:
            raise

    is_verified = bool(data.get("SourceCode"))
    if not is_verified:
        raise exceptions.ContractNotVerified(
            f"Contract source code not verified: {address}"
        ) from None
    name = data["ContractName"]
    abi = decode(data["ABI"])
    implementation = data.get("Implementation")
    return name, abi, implementation


def _resolve_proxy(address) -> Tuple[str, List]:
    """
    Resolve the implementation address for a proxy contract.

    Args:
        address: The address of the proxy contract.

    Returns:
        A tuple containing the contract name and ABI.
    """
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
    implementation_eip1822 = web3.eth.get_storage_at(
        address, web3.keccak(text="PROXIABLE")
    )

    # Just leave this code where it is for a helpful debugger as needed.
    if address == "":
        raise Exception(
            f"""implementation: {implementation}
            implementation_eip1967: {len(implementation_eip1967)} {implementation_eip1967}
            implementation_eip1822: {len(implementation_eip1822)} {implementation_eip1822}"""
        )

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


async def _extract_abi_data_async(address: Address):
    """
    Extract ABI data for a contract from the blockchain explorer.

    Args:
        address: The address of the contract.

    Returns:
        A tuple containing the contract name, ABI, and implementation address (if applicable).

    Raises:
        Various exceptions based on the API response and contract status.
    """
    try:
        response = await _fetch_from_explorer_async(address, "getsourcecode", False)
    except ConnectionError as e:
        if '{"message":"Something went wrong.","result":null,"status":"0"}' in str(e):
            if chain.id == Network.xDai:
                raise ValueError("Rate limited by Blockscout. Please try again.") from e
            if await dank_mids.eth.get_code(address):
                raise exceptions.ContractNotVerified(address) from e
            else:
                raise ContractNotFound(address) from e
        raise
    except ValueError as e:
        if (
            str(e).startswith("Failed to retrieve data from API")
            and "invalid api key" in str(e).lower()
        ):
            raise exceptions.InvalidAPIKeyError from e
        if exceptions.contract_not_verified(e):
            raise exceptions.ContractNotVerified(
                f"{address} on {Network.printable()}"
            ) from e
        elif "Unknown contract address:" in str(e):
            exc_type = (
                exceptions.ContractNotVerified
                if await dank_mids.eth.get_code(address) not in ["0x", b""]
                else ContractNotFound
            )
            raise exc_type(str(e)) from e
        else:
            raise

    data = response["result"][0]
    is_verified = bool(data.get("SourceCode"))
    if not is_verified:
        raise exceptions.ContractNotVerified(
            f"Contract source code not verified: {address}"
        ) from None
    name = data["ContractName"]
    abi = decode(data["ABI"])
    implementation = data.get("Implementation")
    return name, abi, implementation


@eth_retry.auto_retry
async def _fetch_from_explorer_async(address: str, action: str, silent: bool) -> Dict:
    url = CONFIG.active_network.get("explorer")
    if url is None:
        raise ValueError("Explorer API not set for this network")

    if address in _unverified_addresses:
        raise ValueError(f"Source for {address} has not been verified")

    code = (await dank_mids.eth.get_code(address)).hex()[2:]
    # EIP-1167: Minimal Proxy Contract
    if (
        code[:20] == "363d3d373d3d3d363d73"
        and code[60:] == "5af43d82803e903d91602b57fd5bf3"
    ):
        address = _resolve_address(code[20:60])
    # Vyper <0.2.9 `create_forwarder_to`
    elif (
        code[:30] == "366000600037611000600036600073"
        and code[70:] == "5af4602c57600080fd5b6110006000f3"
    ):
        address = _resolve_address(code[30:70])
    # 0xSplits Clones
    elif (
        code[:120]
        == "36603057343d52307f830d2d700a97af574b186c80d40429385d24241565b08a7c559ba283a964d9b160203da23d3df35b3d3d3d3d363d3d37363d73"  # noqa e501
        and code[160:] == "5af43d3d93803e605b57fd5bf3"
    ):
        address = _resolve_address(code[120:160])

    return await _fetch_explorer_data(
        url, silent=silent, module="contract", action=action, address=address
    )


@lru_cache(maxsize=None)
def _get_explorer_api_key(url) -> Tuple[str, str]:
    explorer, env_key = next(
        ((k, v) for k, v in _explorer_tokens.items() if k in url), (None, None)
    )
    if env_key is None:
        return None
    if api_key := os.getenv(env_key):
        return api_key
    if not silent:
        warnings.warn(
            f"No {explorer} API token set. You may experience issues with rate limiting. "
            f"Visit https://{explorer}.io/register to obtain a token, and then store it "
            f"as the environment variable ${env_key}",
            BrownieEnvironmentWarning,
        )
    return None


@eth_retry.auto_retry
async def _fetch_explorer_data(url, silent, params):
    api_key = _get_explorer_api_key(url)
    if api_key is not None:
        params["apiKey"] = api_key

    async with aiohttp.ClientSession() as session:
        if not silent:
            print(
                f"Fetching source of {color('bright blue')}{address}{color} "
                f"from {color('bright blue')}{urlparse(url).netloc}{color}..."
            )

        async with session.get(url, params=params, headers=request_headers) as response:
            # Check the status code of the response
            if response.status != 200:
                raise ConnectionError(
                    f"Status {response.status} when querying {url}: {await response.text()}"
                )
            data = await response.json()
            if int(data["status"]) != 1:
                raise ValueError(f"Failed to retrieve data from API: {data}")
            return data


async def _resolve_proxy_async(address) -> Tuple[str, List]:
    """
    Resolve the implementation address for a proxy contract.

    Args:
        address: The address of the proxy contract.

    Returns:
        A tuple containing the contract name and ABI.
    """
    address = convert.to_address(address)
    name, abi, implementation = await _extract_abi_data_async(address)
    as_proxy_for = None

    if address in FORCE_IMPLEMENTATION:
        implementation = FORCE_IMPLEMENTATION[address]
        name, implementation_abi, _ = await _extract_abi_data_async(implementation)
        # Here we merge the proxy ABI with the implementation ABI
        # without doing this, we'd only get the implementation
        # and would lack any valid methods/events from the proxy itself.
        # Credit: Wavey@Yearn
        abi += implementation_abi
        return name, abi

    # always check for an EIP1967 proxy - https://eips.ethereum.org/EIPS/eip-1967
    # always check for an EIP1822 proxy - https://eips.ethereum.org/EIPS/eip-1822
    implementation_eip1967, implementation_eip1822 = await asyncio.gather(
        dank_mids.eth.get_storage_at(
            address, int(web3.keccak(text="eip1967.proxy.implementation").hex(), 16) - 1
        ),
        dank_mids.eth.get_storage_at(address, web3.keccak(text="PROXIABLE")),
    )

    # Just leave this code where it is for a helpful debugger as needed.
    if address == "":
        raise Exception(
            f"""implementation: {implementation}
            implementation_eip1967: {len(implementation_eip1967)} {implementation_eip1967}
            implementation_eip1822: {len(implementation_eip1822)} {implementation_eip1822}"""
        )

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
            as_proxy_for = await c.implementation
        except Exception:
            # if that fails, fall back to the address provided by etherscan
            as_proxy_for = _resolve_address(implementation)

    if as_proxy_for:
        name, abi, _ = await _extract_abi_data_async(as_proxy_for)
    return name, abi


_resolve_proxy_async = a_sync.SmartProcessingQueue(_resolve_proxy_async, num_workers=8)


def _setup_events(contract: Contract) -> None:
    """
    Helper function used to init contract event containers on a newly created `y.Contract` object.

    Args:
        contract: The contract object to set up events for.
    """
    if not hasattr(contract, "events"):
        contract.events = ContractEvents(contract)
    for k, v in contract.topics.items():
        setattr(contract.events, k, Events(addresses=[contract.address], topics=[[v]]))


_Address = NewType("_Address", str)
_unverified: Set[_Address] = set()
"""A collection of unverified addresses that is used to prevent repetitive etherscan api calls"""


_NOT_SYNCED = "`chain.height` returns 0 on your node, which means it is not fully synced.\nYou can only use this function on a fully synced node."
