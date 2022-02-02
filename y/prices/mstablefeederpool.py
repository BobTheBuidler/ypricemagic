
import logging
from functools import lru_cache

from y.contracts import Contract, has_methods
from y.decorators import log
from y.prices import magic
from y.utils.multicall import fetch_multicall

logger = logging.getLogger(__name__)

@log(logger)
@lru_cache
def is_mstable_feeder_pool(address: str) -> bool:
    return has_methods(address, ['getPrice()((uint,uint))','mAsset()(address)'])

@log(logger)
def get_price(address, block=None):
    contract = Contract(address)
    ratio, masset, decimals = fetch_multicall([contract,'getPrice'],[contract,'mAsset'],[contract,'decimals'],block=block)
    ratio = ratio[0] / 10 ** decimals
    underlying_price = magic.get_price(masset,block)
    return underlying_price * ratio
