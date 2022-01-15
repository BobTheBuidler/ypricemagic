
from y.contracts import Contract
from y.utils.cache import memory
from ypricemagic import magic
from ypricemagic.utils.multicall import fetch_multicall


@memory.cache()
def is_mstable_feeder_pool(address: str) -> bool:
    contract = Contract(address)
    return hasattr(contract,'getPrice') and hasattr(contract,'mAsset')

def get_price(address, block=None):
    contract = Contract(address)
    ratio, masset, decimals = fetch_multicall([contract,'getPrice'],[contract,'mAsset'],[contract,'decimals'],block=block)
    ratio = ratio[0] / 10 ** decimals
    underlying_price = magic.get_price(masset,block)
    return underlying_price * ratio
