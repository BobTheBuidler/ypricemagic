import asyncio
import logging
from typing import Optional

import a_sync

import y.prices.magic
from y import convert
from y.classes.common import ERC20
from y.contracts import has_methods
from y.datatypes import AnyAddressType, Block, UsdPrice
from y.utils.raw_calls import raw_call

logger = logging.getLogger(__name__)

@a_sync.a_sync(default='sync', cache_type='memory')
async def is_gelato_pool(token_address: AnyAddressType) -> bool:
    return await has_methods(token_address, ('gelatoBalance0()(uint)','gelatoBalance1()(uint)'), sync=False)

@a_sync.a_sync(default='sync')
async def get_price(token: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
    address = convert.to_address(token) 

    token0, token1 = await asyncio.gather(
        raw_call(address,'token0()',block=block,output='address', sync=False),
        raw_call(address,'token1()',block=block,output='address', sync=False),
    )

    balance0, balance1, scale0, scale1, price0, price1, total_supply = await asyncio.gather(
        raw_call(address,'gelatoBalance0()',block=block,output='int', sync=False),
        raw_call(address,'gelatoBalance1()',block=block,output='int', sync=False),
        ERC20(token0, asynchronous=True).scale,
        ERC20(token1, asynchronous=True).scale,
        y.prices.magic.get_price(token0, block, sync=False),
        y.prices.magic.get_price(token1, block, sync=False),
        ERC20(address, asynchronous=True).total_supply_readable(block, sync=False),
    )

    balance0 /= scale0
    balance1 /= scale1
    totalVal = balance0 * price0 + balance1 * price1
    return UsdPrice(totalVal / total_supply)
