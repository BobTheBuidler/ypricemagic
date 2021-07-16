from brownie import Contract
from . import magic

def is_atoken_v1(address):
    pool = Contract(address)
    required = {"getInterestRedirectionAddress", "getRedirectedBalance", "underlyingAssetAddress"}
    return set(pool.__dict__) & required == required

def get_price(token, block=None):
    underlying = Contract(token).underlyingAssetAddress(block_identifier = block)
    return magic.get_price(underlying, block=block)