from y.contracts import Contract
from y.utils.cache import memory
from ypricemagic import magic
from ypricemagic.utils.raw_calls import raw_call


def is_atoken_v1(address):
    contract = Contract(address)
    required = {"getInterestRedirectionAddress", "getRedirectedBalance", "underlyingAssetAddress"}
    return set(contract.__dict__) & required == required

def is_atoken_v2(address):
    contract = Contract(address)
    return all([
        hasattr(contract, 'UNDERLYING_ASSET_ADDRESS'),
        any([hasattr(contract,'LENDING_POOL'), hasattr(contract, 'ATOKEN_REVISION')])
    ])

@memory.cache()
def is_atoken(address):
    return is_atoken_v1(address) or is_atoken_v2(address)

def get_price_v1(token, block=None):
    underlying = raw_call(token, 'underlyingAssetAddress()', block=block, output='address')
    return magic.get_price(underlying, block=block)

def get_price_v2(token, block=None):
    underlying = raw_call(token, 'UNDERLYING_ASSET_ADDRESS()',block=block,output='address')
    return magic.get_price(underlying, block=block)

def get_price(token, block=None):
    if is_atoken_v1(token):
        return get_price_v1(token, block)
    if is_atoken_v2(token):
        return get_price_v2(token, block)
