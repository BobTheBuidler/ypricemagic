import datetime
import logging

from brownie import chain, web3
from cachetools.func import lru_cache
from ypricemagic.utils.cache import memory

logger = logging.getLogger(__name__)

@lru_cache(1)
def get_ethereum_client():
    client = web3.clientVersion
    if client.startswith('TurboGeth'):
        return 'tg'
    if client.lower().startswith('erigon'):
        return 'erigon'
    if client.lower().startswith('geth'):
        return 'geth'
    logging.debug(f"client: {client}")
    return client


@memory.cache() 
def get_block_timestamp(height):
    client = get_ethereum_client()
    if client in ['tg', 'erigon']:
        header = web3.manager.request_blocking(f"{client}_getHeaderByNumber", [height])
        return int(header.timestamp, 16)
    else:
        return chain[height].timestamp


@memory.cache() 
def last_block_on_date(date_string):
    logger.debug('last block on date %d', date_string)
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
def closest_block_after_timestamp(timestamp):
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
    

@memory.cache()
def contract_creation_block(address) -> int:
    """
    Determine the block when a contract was created using binary search.
    NOTE Requires access to historical state. Doesn't account for CREATE2 or SELFDESTRUCT.
    """
    logger.info("contract creation block %s", address)
    height = chain.height
    lo, hi = 0, height
    while hi - lo > 1:
        mid = lo + (hi - lo) // 2
        if web3.eth.get_code(address, block_identifier=mid):
            hi = mid
        else:
            lo = mid
    return hi if hi != height else None