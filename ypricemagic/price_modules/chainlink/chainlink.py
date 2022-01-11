import logging

from cachetools.func import ttl_cache
from ypricemagic.price_modules.chainlink.feeds import feeds

logger = logging.getLogger(__name__)

@ttl_cache(ttl=600)
def get_price(asset, block=None):
    try:
        price = feeds[asset].latestAnswer(block_identifier=block) / 1e8
        logger.debug("chainlink -> %s", price)
        return price
    except (KeyError, ValueError):
        return None
