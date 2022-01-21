import logging
from functools import lru_cache

from y.contracts import has_method, has_methods
from y.utils.cache import memory
from ypricemagic import magic
from ypricemagic.utils.raw_calls import raw_call

logger = logging.getLogger(__name__)


@lru_cache
def is_atoken_v1(address):
    logger.debug(f'Checking `is_atoken_v1({address})')
    result = has_methods(address, ['getInterestRedirectionAddress()(address)','getRedirectedBalance()(uint)','underlyingAssetAddress()(address)'])
    logger.debug(f'`is_atoken_v1({address}` returns `{result}`')
    return result

@lru_cache
def is_atoken_v2(address):
    logger.debug(f'Checking `is_atoken_v2({address})')
    result = all([
        has_method(address, 'UNDERLYING_ASSET_ADDRESS()(address)'),
        has_methods(address, ['LENDING_POOL()(address)','ATOKEN_REVISION()(address)'], any)
    ])
    logger.debug(f'`is_atoken_v1({address}` returns `{result}`')
    return result

@lru_cache
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
