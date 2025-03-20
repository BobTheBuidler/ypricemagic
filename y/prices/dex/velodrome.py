import logging
from typing import List, Optional, Set, Tuple

import a_sync
import dank_mids
import eth_retry
from a_sync import cgather
from a_sync.a_sync.property import HiddenMethodDescriptor
from brownie import chain
from multicall.call import Call
from typing_extensions import Self
from web3.exceptions import ContractLogicError

from y._decorators import stuck_coro_debugger
from y.contracts import Contract, contract_creation_block_async
from y.datatypes import Address, AnyAddressType, Block
from y.interfaces.uniswap.velov2 import VELO_V2_FACTORY_ABI
from y.networks import Network
from y.prices.dex.solidly import SolidlyRouterBase
from y.prices.dex.uniswap.v2 import Path, UniswapV2Pool
from y.utils import gather_methods
from y.utils.cache import a_sync_ttl_cache
from y.utils.raw_calls import raw_call

_INIT_METHODS = "token0()(address)", "token1()(address)", "stable()(bool)"

logger = logging.getLogger(__name__)


class NoReservesError(Exception):
    pass


default_factory = {
    Network.Optimism: "0xF1046053aa5682b4F9a81b5481394DA16BE5FF5a",
    Network.Base: "0x420DD381b31aEf6683db6B902084cB0FFECe40Da",
}


class VelodromePool(UniswapV2Pool):
    __slots__ = ("is_stable",)

    def __init__(
        self,
        address: AnyAddressType,
        token0: Optional[AnyAddressType] = None,
        token1: Optional[AnyAddressType] = None,
        stable: Optional[bool] = None,
        deploy_block: Optional[int] = None,
        *,
        asynchronous: bool = False,
    ):
        """
        Initialize a :class:`VelodromePool` instance.

        Args:
            address: The address of the pool.
            token0: The address of the first token in the pool.
            token1: The address of the second token in the pool.
            stable: Indicates if the pool is stable.
            deploy_block: The block number at which the pool was deployed.
            asynchronous: Whether to use asynchronous operations.

        Examples:
            >>> pool = VelodromePool("0xPoolAddress", "0xToken0", "0xToken1", True, 12345678)
            >>> print(pool.is_stable)
            True

        See Also:
            - :class:`UniswapV2Pool`
        """
        super().__init__(
            address,
            token0=token0,
            token1=token1,
            deploy_block=deploy_block,
            asynchronous=asynchronous,
        )
        self.is_stable = stable
        """Indicates if the pool is stable, as opposed to volatile."""


class VelodromeRouterV2(SolidlyRouterBase):
    _supports_uniswap_helper = False

    def __init__(self, *args, **kwargs) -> None:
        """
        Initialize a :class:`VelodromeRouterV2` instance.

        This class is a specialized router for Velodrome V2, inheriting from :class:`SolidlyRouterBase`.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Examples:
            >>> router = VelodromeRouterV2()
            >>> print(router.default_factory)
            0xF1046053aa5682b4F9a81b5481394DA16BE5FF5a

        See Also:
            - :class:`SolidlyRouterBase`
        """

        super().__init__(*args, **kwargs)

        self.default_factory = default_factory[chain.id]
        """The default factory address for the current network."""

        self._all_pools = Call(self.factory, "allPools(uint256)(address)")
        """A prepared call for fetching all pools from the factory."""

    @stuck_coro_debugger
    @a_sync_ttl_cache
    async def pool_for(
        self, input_token: Address, output_token: Address, stable: bool
    ) -> Optional[Address]:
        """
        Get the pool address for a given pair of tokens and stability preference.

        Args:
            input_token: The address of the input token.
            output_token: The address of the output token.
            stable: Indicates if a stable pool is preferred.

        Returns:
            The address of the pool if it exists, otherwise None.

        Examples:
            >>> router = VelodromeRouterV2()
            >>> pool_address = await router.pool_for("0xTokenA", "0xTokenB", True)
            >>> print(pool_address)
            0xPoolAddress

        See Also:
            - :meth:`get_pool`
        """
        pool_address = str(
            await self.contract.poolFor.coroutine(
                input_token, output_token, stable, self.default_factory
            )
        )
        if await is_contract(pool_address):
            return pool_address

    @stuck_coro_debugger
    @a_sync_ttl_cache
    @eth_retry.auto_retry
    async def get_pool(
        self, input_token: Address, output_token: Address, stable: bool, block: Block
    ) -> Optional[VelodromePool]:
        """
        Get the :class:`VelodromePool` instance for a given pair of tokens and stability preference.

        Args:
            input_token: The address of the input token.
            output_token: The address of the output token.
            stable: Indicates if a stable pool is preferred.
            block: The block number to consider.

        Returns:
            A :class:`VelodromePool` instance if the pool exists and the address is a contract, otherwise None.

        Examples:
            >>> router = VelodromeRouterV2()
            >>> pool = await router.get_pool("0xTokenA", "0xTokenB", True, 12345678)
            >>> print(pool)
            <VelodromePool instance>

        See Also:
            - :meth:`pool_for`
        """
        if pool_address := await self.pool_for(
            input_token, output_token, stable, sync=False
        ):
            if await contract_creation_block_async(pool_address) <= block:
                return VelodromePool(pool_address, asynchronous=self.asynchronous)

    @a_sync.aka.cached_property
    @stuck_coro_debugger
    async def pools(self) -> Set[VelodromePool]:
        """
        Fetch all Velodrome pools.

        This method retrieves all pools for the Velodrome protocol on the current network.

        Returns:
            A set of :class:`VelodromePool` instances.

        Examples:
            >>> router = VelodromeRouterV2()
            >>> pools = await router.pools
            >>> print(len(pools))
            42

        See Also:
            - :meth:`get_pool`
        """
        logger.info(
            "Fetching pools for %s on %s. If this is your first time using ypricemagic, this can take a while. Please wait patiently...",
            self.label,
            Network.printable(),
        )
        factory = await Contract.coroutine(self.factory)
        if "PoolCreated" not in factory.topics:
            # the etherscan proxy detection is borked here, need this to decode properly
            factory = Contract.from_abi(
                "PoolFactory", self.factory, VELO_V2_FACTORY_ABI
            )

        pools = {
            VelodromePool(
                address=event["pool"],
                token0=event["token0"],
                token1=event["token1"],
                stable=event["stable"],
                deploy_block=event.block_number,
                asynchronous=self.asynchronous,
            )
            async for event in factory.events.PoolCreated.events(
                to_block=await dank_mids.eth.block_number
            )
        }

        all_pools_len = await raw_call(
            self.factory, "allPoolsLength()", output="int", sync=False
        )

        if len(pools) > all_pools_len:
            raise ValueError("wtf", len(pools), all_pools_len)

        if len(pools) < all_pools_len:
            logger.debug(
                "Oh no! Looks like your node can't look back that far. Checking for the missing %s pools...",
                all_pools_len - len(pools),
            )
            pools_your_node_couldnt_get = a_sync.map(
                self._init_pool_from_poolid,
                range(all_pools_len - len(pools)),
                name=f"load {self} poolId",
            )
            # we want the map populated with tasks for this logger
            await pools_your_node_couldnt_get._init_loader
            logger.debug("pools: %s", pools_your_node_couldnt_get)
            pools.update(await pools_your_node_couldnt_get.values(pop=True))

        tokens = set()
        for pool in pools:
            tokens.update(await cgather(pool.__token0__, pool.__token1__))
        logger.info(
            "Loaded %s pools supporting %s tokens on %s",
            len(pools),
            len(tokens),
            self.label,
        )
        return pools

    __pools__: HiddenMethodDescriptor[Self, Set[VelodromePool]]

    @stuck_coro_debugger
    async def get_routes_from_path(
        self, path: Path, block: Block
    ) -> List[Tuple[Address, Address, bool]]:
        """
        Get the routes for a given path of tokens.

        Args:
            path: A list of token addresses representing the path.
            block: The block number to consider.

        Returns:
            A list of tuples, each containing the input token, output token, and stability preference.

        Raises:
            NoReservesError: If no route is available for the given path.

        Examples:
            >>> router = VelodromeRouterV2()
            >>> routes = await router.get_routes_from_path(["0xTokenA", "0xTokenB"], 12345678)
            >>> print(routes)
            [("0xTokenA", "0xTokenB", True)]

        See Also:
            - :meth:`get_pool`
        """
        routes = []
        for i in range(len(path) - 1):
            input_token, output_token = path[i], path[i + 1]
            # Try for a stable pool first and use that if available
            stable_pool: Optional[VelodromePool]
            unstable_pool: Optional[VelodromePool]
            stable_pool, unstable_pool = await cgather(
                self.get_pool(input_token, output_token, True, block, sync=False),
                self.get_pool(input_token, output_token, False, block, sync=False),
            )

            if stable_pool and unstable_pool:
                # We have to find out which of these pools is deepest
                stable_reserves, unstable_reserves = await cgather(
                    stable_pool.reserves(block=block, sync=False),
                    unstable_pool.reserves(block=block, sync=False),
                )
                if stable_reserves and unstable_reserves:
                    stable_reserves = tuple(stable_reserves)
                    unstable_reserves = tuple(unstable_reserves)

                    # NOTE: using `__token0__` and `__token1__` is faster than `__tokens__` since they're already cached and return instantly
                    #       it also creates 2 fewer tasks and 1 fewer future than `__tokens__` since there is no use of `asyncio.gather`.
                    if (
                        await stable_pool.__token0__ == await unstable_pool.__token0__
                        and await stable_pool.__token1__
                        == await unstable_pool.__token1__
                    ):
                        stable_reserve = stable_reserves[0]
                        unstable_reserve = unstable_reserves[0]
                    else:  # Order of tokens is flip flopped in the pools
                        stable_reserve = stable_reserves[0]
                        unstable_reserve = unstable_reserves[1]
                    if stable_reserve >= unstable_reserve:
                        is_stable = True
                    elif stable_reserve < unstable_reserve:
                        is_stable = False
                    routes.append([input_token, output_token, is_stable, self.factory])
                elif stable_reserves:
                    routes.append([input_token, output_token, True, self.factory])
                elif unstable_reserves:
                    routes.append([input_token, output_token, False, self.factory])
                else:
                    raise NoReservesError(f"No route available for path {path}")
            elif stable_pool:
                routes.append([input_token, output_token, True, self.factory])
            elif unstable_pool:
                routes.append([input_token, output_token, False, self.factory])
            else:
                raise ValueError(
                    "Not sure why this function is even running if no pool is found"
                )

        return routes

    @stuck_coro_debugger
    async def _init_pool_from_poolid(self, poolid: int) -> VelodromePool:
        """
        Initialize a :class:`VelodromePool` from a pool ID.

        Args:
            poolid: The ID of the pool to initialize.

        Returns:
            A :class:`VelodromePool` instance.

        Examples:
            >>> router = VelodromeRouterV2()
            >>> pool = await router._init_pool_from_poolid(1)
            >>> print(pool)
            <VelodromePool instance>

        See Also:
            - :meth:`pools`
        """
        logger.debug("initing poolid %s", poolid)

        try:
            pool = await self._all_pools.coroutine(poolid)
        except ContractLogicError:
            # sometimes a failure returns None above,
            # sometimes it raises ContractLogicError.
            pool = None

        if pool is None:
            # TODO: debug why this happens sometimes and why this if clause works to get back on track
            factory = await Contract.coroutine(self.factory)
            pool = await factory.allPools.coroutine(poolid)

        token0, token1, stable = await gather_methods(pool, _INIT_METHODS)
        return VelodromePool(
            address=pool,
            token0=token0,
            token1=token1,
            stable=stable,
            asynchronous=self.asynchronous,
        )


async def is_contract(pool_address: Address) -> bool:
    """
    Check if a given address is a contract.

    Args:
        pool_address: The address to check.

    Returns:
        True if the address is a contract, otherwise False.

    Examples:
        >>> result = await is_contract("0xPoolAddress")
        >>> print(result)
        True
    """
    if pool_address in __pools:
        return True
    if result := await dank_mids.eth.get_code(pool_address) not in ("0x", b""):
        __pools_append(pool_address)
    return result


__pools = []
__pools_append = __pools.append
