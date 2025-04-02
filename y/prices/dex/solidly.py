from typing import List, Optional, Tuple

from a_sync import cgather

from y._decorators import continue_on_revert, stuck_coro_debugger
from y.datatypes import Address, Block
from y.exceptions import call_reverted
from y.prices.dex.uniswap.v2 import Path, UniswapRouterV2, UniswapV2Pool
from y.utils.cache import a_sync_ttl_cache


class SolidlyRouterBase(UniswapRouterV2):
    """
    Solidly is a modified fork of Uni V2.
    The `uniswap_multiplexer` is the entrypoint for pricing using this object.

    This class provides methods to interact with the Solidly protocol, which is
    based on the Uniswap V2 model. It includes functionality to get price quotes
    and determine routes for token swaps.

    See Also:
        - :class:`~y.prices.dex.uniswap.v2.UniswapRouterV2`
        - :class:`~y.prices.dex.uniswap.v2.UniswapV2Pool`
    """

    @continue_on_revert
    @stuck_coro_debugger
    async def get_quote(
        self, amount_in: int, path: Path, block: Optional[Block] = None
    ) -> Tuple[int, int]:
        """
        Get a price quote for a given input amount and swap path.

        This method calculates the output amount for a given input amount and
        swap path by interacting with the Solidly contract.

        Args:
            amount_in: The amount of input tokens.
            path: The swap path as a list of token addresses.
            block: The block number to query. Defaults to the latest block.

        Returns:
            A tuple containing the output amount and the path used.

        Raises:
            Exception: If the call reverts for reasons other than insufficient
            input amount or liquidity.

        Examples:
            >>> router = SolidlyRouterBase("0xRouterAddress")
            >>> quote = await router.get_quote(1000, ["0xTokenA", "0xTokenB"])
            >>> print(quote)
        """
        routes = await self.get_routes_from_path(path, block)
        try:
            return await self.contract.getAmountsOut.coroutine(
                amount_in, routes, block_identifier=block
            )
        except Exception as e:
            strings = (
                "INSUFFICIENT_INPUT_AMOUNT",
                "INSUFFICIENT_LIQUIDITY",
                "INSUFFICIENT_OUT_LIQUIDITY",
                "Sequence has incorrect length",
                "Call reverted: Integer overflow",
            )
            if not call_reverted(e) and not any(map(str(e).__contains__, strings)):
                raise


class SolidlyPool(UniswapV2Pool):
    """
    Represents a liquidity pool in the Solidly protocol.

    This class inherits from :class:`~y.prices.dex.uniswap.v2.UniswapV2Pool` and
    provides the same interface for interacting with liquidity pools.

    See Also:
        - :class:`~y.prices.dex.uniswap.v2.UniswapV2Pool`
    """

    pass


class SolidlyRouter(SolidlyRouterBase):
    """
    A router for interacting with the Solidly protocol.

    This class extends :class:`~SolidlyRouterBase` to provide additional
    functionality specific to the Solidly protocol, such as determining the
    appropriate pool for a token pair and calculating swap routes.

    See Also:
        - :class:`~SolidlyRouterBase`
    """

    @stuck_coro_debugger
    @a_sync_ttl_cache
    async def pair_for(
        self, input_token: Address, output_token: Address, stable: bool
    ) -> Address:
        """
        Get the address of the pool for a given token pair.

        This method returns the address of the pool that contains the specified
        input and output tokens, and indicates whether the pool is stable.

        Args:
            input_token: The address of the input token.
            output_token: The address of the output token.
            stable: A boolean indicating whether to look for a stable pool.

        Returns:
            The address of the pool.

        Examples:
            >>> router = SolidlyRouter("0xRouterAddress")
            >>> pool_address = await router.pair_for("0xTokenA", "0xTokenB", True)
            >>> print(pool_address)
        """
        return await self.contract.pairFor.coroutine(input_token, output_token, stable)

    @stuck_coro_debugger
    @a_sync_ttl_cache
    async def get_pool(
        self, input_token: Address, output_token: Address, stable: bool, block: Block
    ) -> Optional[SolidlyPool]:
        """
        Get the pool object for a given token pair.

        This method returns a :class:`~SolidlyPool` object representing the pool
        that contains the specified input and output tokens, and indicates
        whether the pool is stable.

        Args:
            input_token: The address of the input token.
            output_token: The address of the output token.
            stable: A boolean indicating whether to look for a stable pool.
            block: The block number to query.

        Returns:
            A :class:`~SolidlyPool` object if the pool exists, otherwise None.

        Examples:
            >>> router = SolidlyRouter("0xRouterAddress")
            >>> pool = await router.get_pool("0xTokenA", "0xTokenB", True, 12345678)
            >>> print(pool)
        """
        pool_address = await self.pair_for(
            input_token, output_token, stable, sync=False
        )
        if await self.contract.isPair.coroutine(pool_address, block_identifier=block):
            return SolidlyPool(pool_address, asynchronous=self.asynchronous)

    @stuck_coro_debugger
    async def get_routes_from_path(
        self, path: Path, block: Block
    ) -> List[Tuple[Address, Address, bool]]:
        """
        Determine the swap routes from a given path.

        This method calculates the swap routes for a given path by checking for
        available stable and unstable pools and selecting the deepest pool.

        Args:
            path: The swap path as a list of token addresses.
            block: The block number to query.

        Returns:
            A list of tuples, each containing the input token, output token, and
            a boolean indicating whether the pool is stable.

        Raises:
            ValueError: If no pool is found for a token pair.

        Examples:
            >>> router = SolidlyRouter("0xRouterAddress")
            >>> routes = await router.get_routes_from_path(["0xTokenA", "0xTokenB"], 12345678)
            >>> print(routes)
        """
        routes = []
        for i in range(len(path) - 1):
            input_token, output_token = path[i], path[i + 1]
            # Try for a stable pool first and use that if available
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
                stable_reserves = tuple(stable_reserves)
                unstable_reserves = tuple(unstable_reserves)

                # NOTE: using `__token0__` and `__token1__` is faster than `__tokens__` since they're already cached and return instantly
                #       it also creates 2 fewer tasks and 1 fewer future than `__tokens__` since there is no use of `asyncio.gather`.
                if (
                    await stable_pool.__token0__ == await unstable_pool.__token0__
                    and await stable_pool.__token1__ == await unstable_pool.__token1__
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
                routes.append([input_token, output_token, is_stable])
            elif stable_pool:
                routes.append([input_token, output_token, True])
            elif unstable_pool:
                routes.append([input_token, output_token, False])
            else:
                raise ValueError(
                    "Not sure why this function is even running if no pool is found"
                )

        return routes
