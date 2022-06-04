
import logging
from typing import Optional

from async_lru import alru_cache
from y import convert
from y.contracts import Contract, has_methods_async
from y.datatypes import AnyAddressType, Block, UsdPrice
from y.prices import magic
from y.utils.logging import yLazyLogger
from y.utils.multicall import fetch_multicall

logger = logging.getLogger(__name__)

@yLazyLogger(logger)
@alru_cache(maxsize=None)
async def is_mstable_feeder_pool(address: AnyAddressType) -> bool:
    return await has_methods_async(address, ('getPrice()((uint,uint))','mAsset()(address)'))

@yLazyLogger(logger)
def get_price(token: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
    address = convert.to_address(token)
    contract = Contract(address)
    ratio, masset, decimals = fetch_multicall([contract,'getPrice'],[contract,'mAsset'],[contract,'decimals'],block=block)
    ratio = ratio[0] / 10 ** decimals
    underlying_price = magic.get_price(masset,block)
    return UsdPrice(underlying_price * ratio)
