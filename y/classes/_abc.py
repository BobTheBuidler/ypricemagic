
import abc
import asyncio
from decimal import Decimal
from typing import Optional

import y.ENVIRONMENT_VARIABLES as ENVS
from y._decorators import stuck_coro_debugger
from y.classes.common import ERC20
from y.datatypes import Block, UsdPrice, UsdValue


class Wrapper(ERC20):
    """An ERC20 token that holds balances of (an) other ERC20 token(s)"""
    # TODO: implement

class LiquidityPool(Wrapper):
    """A :ref:`~Wrapper` that pools multiple ERC20s together for swapping"""
    # TODO: implement this elsewhere outside of just balancer
    @stuck_coro_debugger
    async def get_pool_price(self, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE) -> UsdPrice:
        tvl, total_supply = await asyncio.gather(
            self.get_tvl(block=block, skip_cache=skip_cache, sync=False),
            self.total_supply_readable(block=block, sync=False),
        )
        return UsdPrice(Decimal(tvl) / Decimal(total_supply))
        
    @abc.abstractmethod
    async def get_tvl(self, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE) -> UsdValue:
        ...