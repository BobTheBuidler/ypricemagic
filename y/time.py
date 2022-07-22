import datetime
import logging

from brownie import chain, web3
from y.utils.cache import memory
from y.utils.client import get_ethereum_client
from y.utils.logging import yLazyLogger

logger = logging.getLogger(__name__)


@memory.cache() 
#yLazyLogger(logger)
def get_block_timestamp(height: int) -> int:
    client = get_ethereum_client()
    if client in ['tg', 'erigon']:
        header = web3.manager.request_blocking(f"{client}_getHeaderByNumber", [height])
        return int(header.timestamp, 16)
    else:
        return chain[height].timestamp


@memory.cache()
#yLazyLogger(logger)
def last_block_on_date(date_string: str) -> int:
    logger.debug(f'last block on date {date_string}')
    date = datetime.datetime.strptime(date_string, "%Y-%m-%d")
    date = date.date()
    height = chain.height
    lo, hi = 0, height
    while hi - lo > 1:
        mid = lo + (hi - lo) // 2
        logger.debug('block: ' + str(mid))
        logger.debug('mid: ' + str(datetime.date.fromtimestamp(get_block_timestamp(mid))))
        logger.debug(date)
        if datetime.date.fromtimestamp(get_block_timestamp(mid)) > date:
            hi = mid
        else:
            lo = mid
    hi = hi - 1
    return hi if hi != height else None


@memory.cache()
#yLazyLogger(logger)
def closest_block_after_timestamp(timestamp: int) -> int:
    logger.info('closest block after timestamp %d', timestamp)
    height = chain.height
    lo, hi = 0, height
    while hi - lo > 1:
        mid = lo + (hi - lo) // 2
        if get_block_timestamp(mid) > timestamp:
            hi = mid
        else:
            lo = mid
    return hi if hi != height else None
