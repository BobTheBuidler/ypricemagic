
import abc
import asyncio
from decimal import Decimal
from typing import Optional

import y.ENVIRONMENT_VARIABLES as ENVS
from y._decorators import stuck_coro_debugger
from y.classes.common import ERC20
from y.datatypes import Block, UsdPrice, UsdValue


class Wrapper(ERC20):
    """
    An abstract base class representing an ERC20 token that holds balances of (an)other ERC20 token(s).

    This class extends the ERC20 class to represent wrapper tokens, which are tokens that derive their value
    from holding other tokens. The specific implementation details are left to the subclasses.

    Note:
        This class is currently a placeholder and does not implement any additional methods.
    """
    # TODO: implement


class LiquidityPool(Wrapper):
    """
    An abstract base class representing a liquidity pool that pools multiple ERC20s together for swapping.

    This class extends the :class:`~Wrapper` class to represent liquidity pools, which are special types of wrapper
    tokens that allow for token swaps. It provides methods for getting the total value locked (TVL) and pool price.
    """

    # TODO: implement this elsewhere outside of just balancer

    @stuck_coro_debugger
    async def get_pool_price(self, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE) -> UsdPrice:
        """
        Calculate the price of the liquidity pool token.

        This method calculates the price of a single liquidity pool token by dividing the total value locked (TVL)
        by the total supply of the pool tokens.

        Args:
            block: The block number at which to calculate the price. If None, uses the latest block.
            skip_cache: If True, bypasses ypricemagic's local caching mechanisms and forces a fresh calculation.

        Returns:
            The price of a single liquidity pool token as a UsdPrice object.
        """
        tvl, total_supply = await asyncio.gather(
            self.get_tvl(block=block, skip_cache=skip_cache, sync=False),
            self.total_supply_readable(block=block, sync=False),
        )
        return UsdPrice(Decimal(tvl) / Decimal(total_supply))
        
    @abc.abstractmethod
    async def get_tvl(self, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE) -> UsdValue:
        """
        Get the Total Value Locked (TVL) in the liquidity pool.

        This is an abstract method that must be implemented by subclasses. It should return the total value
        of all assets locked in the liquidity pool.

        Args:
            block: The block number at which to calculate the TVL. If None, uses the latest block.
            skip_cache: If True, bypasses ypricemagic's local caching mechanisms and forces a fresh calculation.

        Returns:
            The Total Value Locked (TVL) in the pool as a UsdValue object.

        Note:
            The specific implementation of this method will depend on the type of liquidity pool.
        """
