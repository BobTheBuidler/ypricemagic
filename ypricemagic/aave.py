from brownie import Contract
from . import magic

def is_atoken_v1(address):
    contract = Contract(address)
    required = {"getInterestRedirectionAddress", "getRedirectedBalance", "underlyingAssetAddress"}
    return set(contract.__dict__) & required == required

def is_atoken_v2(address):
    contract = Contract(address)
    required = {"ATOKEN_REVISION", "UNDERLYING_ASSET_ADDRESS"}
    return set(contract.__dict__) & required == required

def is_atoken(address):
    return is_atoken_v1(address) or is_atoken_v2(address)

def get_price_v1(token, block=None):
    underlying = Contract(token).underlyingAssetAddress(block_identifier = block)
    return magic.get_price(underlying, block=block)

def get_price_v2(token, block=None):
    underlying = Contract(token).UNDERLYING_ASSET_ADDRESS(block_identifier = block)
    return magic.get_price(underlying, block=block)

def get_price(token, block=None):
    if is_atoken_v1(token):
        return get_price_v1(token, block)
    if is_atoken_v2(token):
        return get_price_v2(token, block)