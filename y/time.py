import asyncio
import datetime
import logging
import time
from typing import NewType, Union

import dank_mids
import eth_retry
from async_lru import alru_cache
from brownie import chain, web3
from cachetools.func import ttl_cache

try:
    from dank_mids.ENVIRONMENT_VARIABLES import GANACHE_FORK
except ImportError:
    from dank_mids._config import GANACHE_FORK

from y.exceptions import NodeNotSynced
from y.networks import Network
from y.utils.cache import a_sync_ttl_cache, memory
from y.utils.client import get_ethereum_client, get_ethereum_client_async
from y.utils.logging import yLazyLogger


UnixTimestamp = NewType("UnixTimestamp", int)
Timestamp = Union[UnixTimestamp, datetime.datetime]

logger = logging.getLogger(__name__)

class NoBlockFound(Exception):
    """
    Raised when no block is found for a specified timestamp because the timestamp is in the future.
    """
    def __init__(self, timestamp: Timestamp):
        super().__init__(f"No block found after timestamp {timestamp}")

@memory.cache()
@yLazyLogger(logger)
@eth_retry.auto_retry
def get_block_timestamp(height: int) -> int:
    import y._db.utils.utils as db
    if ts := db.get_block_timestamp(height, sync=True):
        return ts
    client = get_ethereum_client()
    if client in ['tg', 'erigon'] and chain.id not in [Network.Polygon]:
        # NOTE: polygon erigon does not support this method
        header = web3.manager.request_blocking(f"{client}_getHeaderByNumber", [height])
        ts = int(header.timestamp, 16)
        db.set_block_timestamp(height, ts, sync=True)
        return ts
    return chain[height].timestamp
    

@a_sync_ttl_cache
@eth_retry.auto_retry
async def get_block_timestamp_async(height: int) -> int:
    import y._db.utils.utils as db
    if ts := await db.get_block_timestamp(height, sync=False):
        return ts
    client = await get_ethereum_client_async()
    if client in ['tg', 'erigon'] and chain.id not in [Network.Polygon]:
        # NOTE: polygon erigon does not support this method
        header = await dank_mids.web3.manager.coro_request(f"{client}_getHeaderByNumber", [height])
        ts = int(header.timestamp, 16)
    else:
        block = await dank_mids.eth.get_block(height)
        ts = block.timestamp
    db.set_block_timestamp(height, ts)
    return ts

# TODO: deprecate
@memory.cache()
def last_block_on_date(date: Union[str, datetime.date]) -> int:
    """ Returns the last block on a given `date`. You can pass either a `datetime.date` object or a date string formatted as 'YYYY-MM-DD'. """
    if isinstance(date, datetime.datetime):
        raise TypeError(
            "You can not pass in a `datetime.datetime` object. Please call date() on your input before passing it to this funciton."
        )
    if not isinstance(date, datetime.date):
        date = datetime.datetime.strptime(date, "%Y-%m-%d").date()

    height = chain.height
    lo, hi = 0, height
    while hi - lo > 1:
        mid = lo + (hi - lo) // 2
        logger.debug('block: %s', str(mid))
        mid_ts = get_block_timestamp(mid)
        mid_date = datetime.date.fromtimestamp(mid_ts)
        logger.debug('mid: %s', mid_date)
        logger.debug(date)
        if mid_date > date:
            hi = mid
        else:
            lo = mid
    hi = hi - 1
    block = hi if hi != height else None
    logger.debug('last %s block on date %s -> %s', Network.name(), date, block)
    return block


@a_sync_ttl_cache
async def get_block_at_timestamp(timestamp: datetime.datetime) -> int:
    import y._db.utils.utils as db
    if block_at_timestamp := await db.get_block_at_timestamp(timestamp):
        return block_at_timestamp
    
    # TODO: invert this and use this fn inside of closest_block_after_timestamp for backwards compatability before deprecating closest_block_after_timestamp
    block_after_timestamp = await closest_block_after_timestamp_async(timestamp)
    block_at_timestamp = block_after_timestamp - 1
    db.set_block_at_timestamp(timestamp, block_at_timestamp)
    return block_at_timestamp

def _parse_timestamp(timestamp: Timestamp) -> UnixTimestamp:
    if isinstance(timestamp, datetime.datetime):
        timestamp = int(timestamp.timestamp())
    elif not isinstance(timestamp, int):
        raise TypeError("You may only pass in a unix timestamp or a datetime object.")
    return UnixTimestamp(timestamp)

#yLazyLogger(logger)
def closest_block_after_timestamp(timestamp: Timestamp, wait_for_block_if_needed: bool = False) -> int:
    timestamp = _parse_timestamp(timestamp)
    while wait_for_block_if_needed:
        try:
            return closest_block_after_timestamp(timestamp)
        except NoBlockFound:
            time.sleep(.2)
    check_node()
    block = _closest_block_after_timestamp_cached(timestamp)
    logger.debug('closest %s block after timestamp %s -> %s', Network.name(), timestamp, block)
    return block

@a_sync_ttl_cache
async def closest_block_after_timestamp_async(timestamp: Timestamp, wait_for_block_if_needed: bool = False) -> int:
    timestamp = _parse_timestamp(timestamp)
    while wait_for_block_if_needed:
        try:
            return await get_block_at_timestamp(datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc), sync=False) + 1
        except NoBlockFound:
            await asyncio.sleep(0.2)
    
    await check_node_async()

    height = await dank_mids.eth.block_number
    lo, hi = 0, height
    while hi - lo > 1:
        mid = lo + (hi - lo) // 2
        if await get_block_timestamp_async(mid) > timestamp:
            hi = mid
        else:
            lo = mid
    if hi == height:
        raise NoBlockFound(timestamp)
    return hi

@memory.cache()
def _closest_block_after_timestamp_cached(timestamp: int) -> int:
    height = chain.height
    lo, hi = 0, height
    while hi - lo > 1:
        mid = lo + (hi - lo) // 2
        if get_block_timestamp(mid) > timestamp:
            hi = mid
        else:
            lo = mid
    if hi == height:
        raise NoBlockFound(timestamp)
    return hi


@ttl_cache(ttl=300)
@eth_retry.auto_retry
def check_node() -> None:
    if GANACHE_FORK:
        return
    current_time = time.time()
    node_timestamp = web3.eth.get_block('latest').timestamp
    if current_time - node_timestamp > 5 * 60:
        raise NodeNotSynced(f"current time: {current_time}  latest block time: {node_timestamp}  discrepancy: {round((current_time - node_timestamp) / 60, 2)} minutes")

@alru_cache(ttl=300)
@eth_retry.auto_retry
async def check_node_async() -> None:
    if GANACHE_FORK:
        return
    current_time = time.time()
    latest = await dank_mids.eth.get_block('latest')
    node_timestamp = latest.timestamp
    if current_time - node_timestamp > 5 * 60:
        raise NodeNotSynced(f"current time: {current_time}  latest block time: {node_timestamp}  discrepancy: {round((current_time - node_timestamp) / 60, 2)} minutes")
