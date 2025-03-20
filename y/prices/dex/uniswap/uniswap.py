import logging
import threading
from contextlib import suppress
from typing import List, Optional, Tuple, Union

import a_sync
from a_sync import igather
from brownie import ZERO_ADDRESS
from web3.exceptions import ContractLogicError

from y import ENVIRONMENT_VARIABLES as ENVS
from y import convert
from y._decorators import stuck_coro_debugger
from y.classes.common import ERC20
from y.constants import CONNECTED_TO_MAINNET
from y.datatypes import Address, AnyAddressType, Block, Pool, UsdPrice
from y.exceptions import NonStandardERC20, contract_not_verified
from y.prices.dex.solidly import SolidlyRouter
from y.prices.dex.uniswap import v3
from y.prices.dex.uniswap.v1 import UniswapV1
from y.prices.dex.uniswap.v2 import NotAUniswapV2Pool, UniswapRouterV2, UniswapV2Pool
from y.prices.dex.uniswap.v2_forks import UNISWAPS
from y.prices.dex.uniswap.v3 import UniswapV3, uniswap_v3
from y.prices.dex.velodrome import VelodromeRouterV2
from y.utils.logging import _gh_issue_request, get_price_logger

logger = logging.getLogger(__name__)

# NOTE: If this is failing to pull a price for a token you need, it's likely because that token requires a special swap path.
#       Please add a viable swap path to ..protocols to fetch price data successfully.

_special_routers = {
    "solidly": SolidlyRouter,
    "velodrome v1": SolidlyRouter,
    "velodrome v2": VelodromeRouterV2,
    "aerodrome": VelodromeRouterV2,
    "ramses": SolidlyRouter,
}

Uniswap = Union[UniswapV1, UniswapRouterV2, UniswapV3]


class UniswapMultiplexer(a_sync.ASyncGenericSingleton):
    """
    A multiplexer for Uniswap routers that provides aggregated functionality across multiple Uniswap instances,
    including Uniswap V1, V2, V3, and certain protocols with similar interfaces like Solidly and Velodrome.

    This class allows for seamless interaction with various decentralized exchange protocols, enabling
    price fetching and liquidity checks across different router implementations.

    Examples:
        >>> multiplexer = UniswapMultiplexer(asynchronous=True)
        >>> price = await multiplexer.get_price("0xTokenAddress", block=12345678)
        >>> print(price)

    See Also:
        - :class:`~y.prices.dex.uniswap.v1.UniswapV1`
        - :class:`~y.prices.dex.uniswap.v2.UniswapRouterV2`
        - :class:`~y.prices.dex.uniswap.v3.UniswapV3`
        - :class:`~y.prices.dex.solidly.SolidlyRouter`
        - :class:`~y.prices.dex.velodrome.VelodromeRouterV2`
    """

    def __init__(self, *, asynchronous: bool = False) -> None:
        super().__init__()
        self.asynchronous = asynchronous
        self.v2_routers = {}
        for name in UNISWAPS:
            router_cls = _special_routers.get(name, UniswapRouterV2)
            try:
                self.v2_routers[name] = router_cls(
                    UNISWAPS[name]["router"], asynchronous=self.asynchronous
                )
            except ValueError as e:  # TODO do this better
                if not contract_not_verified(e):
                    raise
        self.v1 = (
            UniswapV1(asynchronous=self.asynchronous) if CONNECTED_TO_MAINNET else None
        )
        self.v3 = (
            UniswapV3(
                uniswap_v3._factory,
                uniswap_v3._quoter,
                uniswap_v3.fee_tiers,
                asynchronous=self.asynchronous,
            )
            if uniswap_v3
            else None
        )
        # NOTE: this only works with an async UniswapMultiplexer
        # TODO: fix that if it causes issues for somebody. For us its fine.
        self.v3_forks = v3.forks

        self.uniswaps: List[Uniswap] = []
        if self.v1:
            self.uniswaps.append(self.v1)
        self.uniswaps.extend(self.v2_routers.values())
        if self.v3:
            self.uniswaps.append(self.v3)
        if self.v3_forks:
            self.uniswaps.extend(self.v3_forks)

        self.v2_factories = [UNISWAPS[name]["factory"] for name in UNISWAPS]
        self._uid_lock = threading.Lock()

    @stuck_coro_debugger
    async def is_uniswap_pool(self, token_address: AnyAddressType) -> bool:
        token_address = await convert.to_address_async(token_address)
        try:
            await ERC20(token_address, asynchronous=True).decimals
        except NonStandardERC20:
            return False

        pool = UniswapV2Pool(token_address, asynchronous=True)
        with suppress(NotAUniswapV2Pool, ContractLogicError):
            if await pool.is_uniswap_pool(sync=False):
                factory = await pool.__factory__
                if factory not in self.v2_factories and factory != ZERO_ADDRESS:
                    _gh_issue_request(
                        f"UniClone Factory {factory} is unknown to ypricemagic.", logger
                    )
                    self.v2_factories.append(factory)
                return True
        return False

    @stuck_coro_debugger
    async def get_price(
        self,
        token_in: AnyAddressType,
        block: Optional[Block] = None,
        ignore_pools: Tuple[Pool, ...] = (),
        skip_cache: bool = ENVS.SKIP_CACHE,
    ) -> Optional[UsdPrice]:
        """
        Calculate a price based on Uniswap Router quote for selling one `token_in`.
        Always finds the deepest swap path for `token_in`.

        Args:
            token_in: The address of the input token.
            block: The block number to query. Defaults to the latest block.
            ignore_pools: A tuple of Pool objects to ignore when checking liquidity.
            skip_cache: If True, skip using the cache while fetching price data.

        Examples:
            >>> multiplexer = UniswapMultiplexer(asynchronous=True)
            >>> price = await multiplexer.get_price("0xTokenAddress", block=12345678)
            >>> print(price)

        See Also:
            - :meth:`~UniswapMultiplexer.routers_by_depth`
        """
        router: Uniswap
        token_in = await convert.to_address_async(token_in)
        logger = get_price_logger(token_in, block, extra=type(self).__name__)
        routers_by_depth = await self.routers_by_depth(
            token_in, block=block, ignore_pools=ignore_pools, sync=False
        )
        logger.debug("uniswap routers by depth: %s", routers_by_depth)
        for router in routers_by_depth:
            # tries each known router from most to least liquid
            # returns the first price we get back, almost always from the deepest router
            logger.debug("fetching from %s", router)
            price = await router.get_price(
                token_in,
                block=block,
                ignore_pools=ignore_pools,
                skip_cache=skip_cache,
                sync=False,
            )
            logger.debug("%s -> %s", router, price)
            if price:
                return price

    @stuck_coro_debugger
    async def routers_by_depth(
        self,
        token_in: AnyAddressType,
        block: Optional[Block] = None,
        ignore_pools: Tuple[Pool, ...] = (),
    ) -> List[UniswapRouterV2]:
        """
        Get Uniswap routers sorted by liquidity depth for a given token.

        This method checks the liquidity of the input token across all Uniswap instances
        and returns a list of routers sorted by their liquidity depth in descending order.

        Args:
            token_in: The address of the input token to check liquidity for.
            block (optional): The block number to query. Defaults to latest block.
            ignore_pools (optional): A tuple of Pool objects to ignore when checking liquidity.

        Returns:
            A list of UniswapRouterV2 objects sorted by liquidity depth in descending order.

        Note:
            - The method uses asyncio.gather to check liquidity across all Uniswap instances concurrently.
            - Routers with zero liquidity are excluded from the result.

        Examples:
            >>> multiplexer = UniswapMultiplexer(asynchronous=True)
            >>> routers = await multiplexer.routers_by_depth("0xTokenAddress", block=12345678)
            >>> print(routers)
        """
        token_in = await convert.to_address_async(token_in)
        liquidity = await igather(
            uniswap.check_liquidity(
                token_in, block, ignore_pools=ignore_pools, sync=False
            )
            for uniswap in self.uniswaps
        )
        depth_to_router = dict(zip(liquidity, self.uniswaps))
        return [
            depth_to_router[balance]
            for balance in sorted(depth_to_router, reverse=True)
            if balance
        ]

    @a_sync.Semaphore(100)  # some arbitrary number to keep the loop unclogged
    @stuck_coro_debugger
    async def check_liquidity(
        self,
        token: Address,
        block: Block,
        ignore_pools: Tuple[Pool, ...] = (),
    ) -> int:
        """
        Check the maximum liquidity for a token across all Uniswap instances.

        This method checks the liquidity of the given token across all Uniswap instances
        and returns the maximum liquidity found.

        Args:
            token: The address of the token to check liquidity for.
            block: The block number to query.
            ignore_pools (optional): A tuple of Pool objects to ignore when checking liquidity.

        Note:
            - The method uses asyncio.gather to check liquidity across all Uniswap instances concurrently.
            - A semaphore is used to limit the number of concurrent checks to 100.

        Examples:
            >>> multiplexer = UniswapMultiplexer(asynchronous=True)
            >>> liquidity = await multiplexer.check_liquidity("0xTokenAddress", block=12345678)
            >>> print(liquidity)
        """
        return max(
            await igather(
                uniswap.check_liquidity(
                    token, block, ignore_pools=ignore_pools, sync=False
                )
                for uniswap in self.uniswaps
            )
        )


uniswap_multiplexer = UniswapMultiplexer(asynchronous=True)
