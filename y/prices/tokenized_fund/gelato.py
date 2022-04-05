import logging
from functools import lru_cache
from typing import Optional

import y.prices.magic
from y import convert
from y.contracts import has_methods
from y.datatypes import UsdPrice
from y.decorators import log
from y.typing import AnyAddressType, Block
from y.utils.raw_calls import _decimals, _totalSupplyReadable, raw_call

logger = logging.getLogger(__name__)

@log(logger)
@lru_cache
def is_gelato_pool(token_address: AnyAddressType) -> bool:
    return has_methods(token_address, ['gelatoBalance0()(uint)','gelatoBalance1()(uint)'])

@log(logger)
def get_price(token: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
    address = convert.to_address(token)
    token0 = raw_call(address,'token0()',block=block,output='address')
    token1 = raw_call(address,'token1()',block=block,output='address')
    balance0 = raw_call(address,'gelatoBalance0()',block=block,output='int')
    balance1 = raw_call(address,'gelatoBalance1()',block=block,output='int')
    balance0 /= 10 ** _decimals(token0,block)
    balance1 /= 10 ** _decimals(token1,block)
    totalSupply = _totalSupplyReadable(address,block)
    totalVal = balance0 * y.prices.magic.get_price(token0,block) + balance1 * y.prices.magic.get_price(token1,block)
    return UsdPrice(totalVal / totalSupply)
