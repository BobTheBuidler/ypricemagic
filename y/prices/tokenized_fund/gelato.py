import logging
from functools import lru_cache
from typing import Optional

import y.prices.magic
from async_lru import alru_cache
from multicall.utils import await_awaitable, gather
from y import convert
from y.classes.common import ERC20
from y.contracts import has_methods_async
from y.datatypes import AnyAddressType, Block, UsdPrice
from y.utils.logging import yLazyLogger
from y.utils.raw_calls import _totalSupplyReadable, raw_call_async

logger = logging.getLogger(__name__)

@yLazyLogger(logger)
@lru_cache(maxsize=None)
def is_gelato_pool(token_address: AnyAddressType) -> bool:
    return await_awaitable(is_gelato_pool_async(token_address))

@yLazyLogger(logger)
@alru_cache(maxsize=None)
async def is_gelato_pool_async(token_address: AnyAddressType) -> bool:
    return await has_methods_async(token_address, ('gelatoBalance0()(uint)','gelatoBalance1()(uint)'))

def get_price(token: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
    return await_awaitable(get_price_async(token, block=block))

@yLazyLogger(logger)
async def get_price_async(token: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
    address = convert.to_address(token) 

    token0, token1 = await gather([
        raw_call_async(address,'token0()',block=block,output='address'),
        raw_call_async(address,'token1()',block=block,output='address'),
    ])

    balance0, balance1, scale0, scale1, price0, price1, total_supply = await gather([
        raw_call_async(address,'gelatoBalance0()',block=block,output='int'),
        raw_call_async(address,'gelatoBalance1()',block=block,output='int'),
        ERC20(token0).scale,
        ERC20(token1).scale,
        y.prices.magic.get_price_async(token0,block),
        y.prices.magic.get_price_async(token1,block),
        _totalSupplyReadable(address,block),
    ])

    balance0 /= scale0
    balance1 /= scale1
    totalVal = balance0 * price0 + balance1 * price1
    return UsdPrice(totalVal / total_supply)
