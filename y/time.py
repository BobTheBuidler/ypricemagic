import asyncio
import datetime
import logging
import time
from typing import NewType, Union

from brownie import chain, web3
from a_sync import a_sync
from y.exceptions import NoBlockFound
from y.networks import Network
from y.utils.cache import memory
from y.utils.client import get_ethereum_client, get_ethereum_client_async
from y.utils.dank_mids import dank_w3
from y.utils.logging import yLazyLogger

logger = logging.getLogger(__name__)

@memory.cache()
@yLazyLogger(logger)
def get_block_timestamp(height: int) -> int:
    client = get_ethereum_client()
    if client in ['tg', 'erigon']:
        header = web3.manager.request_blocking(f"{client}_getHeaderByNumber", [height])
        return int(header.timestamp, 16)
    else:
        return chain[height].timestamp

@a_sync(cache_type='memory')
async def get_block_timestamp_async(height: int) -> int:
    client = await get_ethereum_client_async()
    if client in ['tg', 'erigon']:
        header = await dank_w3.manager.coro_request(f"{client}_getHeaderByNumber", [height])
        return int(header.timestamp, 16)
    else:
        block = await dank_w3.eth.get_block(height)
        return block.timestamp

@memory.cache()
#yLazyLogger(logger)
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
        logger.debug('block: ' + str(mid))
        mid_ts = get_block_timestamp(mid)
        mid_date = datetime.date.fromtimestamp(mid_ts)
        logger.debug(f'mid: {mid_date}')
        logger.debug(date)
        if mid_date > date:
            hi = mid
        else:
            lo = mid
    hi = hi - 1
    block = hi if hi != height else None
    logger.debug(f'last {Network.name()} block on date {date} -> {block}')
    return block

class UnixTimestamp(int):
    pass

Timestamp = Union[UnixTimestamp, datetime.datetime]

def _parse_timestamp(timestamp: Timestamp) -> UnixTimestamp:
    if isinstance(timestamp, datetime.datetime):
        timestamp = timestamp.timestamp()
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
    block = _closest_block_after_timestamp_cached(timestamp)
    logger.debug(f'closest {Network.name()} block after timestamp {timestamp} -> {block}')
    return block

@a_sync(cache_type='memory')
async def closest_block_after_timestamp_async(timestamp: Timestamp, wait_for_block_if_needed: bool = False) -> int:
    timestamp = _parse_timestamp(timestamp)
    while wait_for_block_if_needed:
        try:
            return await closest_block_after_timestamp_async(timestamp)
        except NoBlockFound:
            await asyncio.sleep(0.2)

    height = await dank_w3.eth.block_number
    lo, hi = 0, height
    while hi - lo > 1:
        mid = lo + (hi - lo) // 2
        if await get_block_timestamp_async(mid) > timestamp:
            hi = mid
        else:
            lo = mid
    if hi == height:
        raise NoBlockFound(f"No block found after timestamp {timestamp}")
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
        raise NoBlockFound(f"No block found after timestamp {timestamp}")
    return hi
