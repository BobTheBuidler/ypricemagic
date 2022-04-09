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
def is_cauldron(token_address: AnyAddressType) -> bool:
    return has_methods(token_address, ['totalCollateralShare()(uint)','collateral()(address)','magicInternetMoney()(uint)'])

@log(logger)
def get_price(token: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
    address = convert.to_address(token)
    total_collateral = raw_call(address, 'totalCollateralShare()', block=block, output='int')
    total_collateral /= 10 ** _decimals(total_collateral, block)
    
    token = raw_call(address, 'collateral()', block=block, output='address')
    total_val = total_collateral * y.prices.magic.getPrice(token,block)
    total_supply = _totalSupplyReadable(address, block)

    return UsdPrice(total_val / total_supply)
