import abc
from decimal import Decimal
from typing import Optional

from a_sync import cgather

import y.ENVIRONMENT_VARIABLES as ENVS
from y._decorators import stuck_coro_debugger
from y.classes.common import ERC20
from y.datatypes import Block, UsdPrice, UsdValue


class Wrapper(ERC20):
    """
    An abstract base class representing an ERC20 token that holds balances of (an)other ERC20 token(s).

    This class extends the :class:`~y.classes.common.ERC20` class to represent wrapper tokens, which are tokens that derive their value
    from holding other tokens. The specific implementation details are left to the subclasses.

    Note:
        This class is currently a placeholder and does not implement any additional methods.

    See Also:
        - :class:`~y.classes.common.ERC20`
    """

    # TODO: implement


class LiquidityPool(Wrapper):
    """
    An abstract base class representing a liquidity pool that pools multiple ERC20s together for swapping.

    This class extends the :class:`~Wrapper` class to represent liquidity pools, which are special types of wrapper
    tokens that allow for token swaps. It provides methods for getting the total value locked (TVL) and pool price.

    Examples:
        >>> class MyLiquidityPool(LiquidityPool):
        ...     async def get_tvl(self, block=None, skip_cache=False):
        ...         return UsdValue(1000000)
        ...
        >>> pool = MyLiquidityPool("0xAddress")
        >>> price = await pool.get_pool_price()
        >>> print(price)
        1000000.0

    See Also:
        - :class:`~Wrapper`
    """

    # TODO: implement this elsewhere outside of just balancer

    @stuck_coro_debugger
    async def get_pool_price(
        self, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE
    ) -> Optional[UsdPrice]:
        """
        Calculate the price of the liquidity pool token.

        This method calculates the price of a single liquidity pool token by dividing the total value locked (TVL)
        by the total supply of the pool tokens.

        Args:
            block: The block number at which to calculate the price. If None, uses the latest block.
            skip_cache: If True, bypasses ypricemagic's local caching mechanisms and forces a fresh calculation.

        Returns:
            The price of a single liquidity pool token as a :class:`~y.datatypes.UsdPrice` object.

        Examples:
            >>> class MyLiquidityPool(LiquidityPool):
            ...     async def get_tvl(self, block=None, skip_cache=False):
            ...         return UsdValue(1000000)
            ...
            >>> pool = MyLiquidityPool("0xAddress")
            >>> price = await pool.get_pool_price()
            >>> print(price)
            1000000.0

        See Also:
            - :meth:`get_tvl`
        """
        tvl, total_supply = await cgather(
            self.get_tvl(block=block, skip_cache=skip_cache, sync=False),
            self.total_supply_readable(block=block, sync=False),
        )
        return None if tvl is None else UsdPrice(Decimal(tvl) / Decimal(total_supply))

    @abc.abstractmethod
    async def get_tvl(
        self, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE
    ) -> Optional[UsdValue]:
        """
        Get the Total Value Locked (TVL) in the liquidity pool.

        This is an abstract method that must be implemented by subclasses. It should return the total value
        of all assets locked in the liquidity pool.

        Args:
            block: The block number at which to calculate the TVL. If None, uses the latest block.
            skip_cache: If True, bypasses ypricemagic's local caching mechanisms and forces a fresh calculation.

        Returns:
            The Total Value Locked (TVL) in the pool as a :class:`~y.datatypes.UsdValue` object.

        Note:
            The specific implementation of this method will depend on the type of liquidity pool.

        Examples:
            >>> class MyLiquidityPool(LiquidityPool):
            ...     async def get_tvl(self, block=None, skip_cache=False):
            ...         return UsdValue(1000000)
            ...
            >>> pool = MyLiquidityPool("0xAddress")
            >>> tvl = await pool.get_tvl()
            >>> print(tvl)
            1000000.0
        """
