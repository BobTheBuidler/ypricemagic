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

_CHAINID = chain.id


class NoBlockFound(Exception):
    """
    Raised when no block is found for a specified timestamp because the timestamp is in the future.

    Args:
        timestamp: The timestamp for which no block was found.
    """

    def __init__(self, timestamp: Timestamp):
        super().__init__(f"No block found after timestamp {timestamp}")


@memory.cache()
@yLazyLogger(logger)
@eth_retry.auto_retry
def get_block_timestamp(height: int) -> int:
    """
    Get the timestamp of a block by its height.

    Args:
        height: The block height.

    Returns:
        The timestamp of the block.

    Examples:
        >>> get_block_timestamp(12345678)
        1609459200

    See Also:
        - :func:`get_block_timestamp_async`
        - :func:`last_block_on_date`
    """
    import y._db.utils.utils as db

    if ts := db.get_block_timestamp(height, sync=True):
        return ts
    client = get_ethereum_client()
    if client in ("tg", "erigon") and _CHAINID not in (Network.Polygon,):
        # NOTE: polygon erigon does not support this method
        header = web3.manager.request_blocking(f"{client}_getHeaderByNumber", [height])
        ts = int(header.timestamp, 16)
        db.set_block_timestamp(height, ts, sync=True)
        return ts
    return chain[height].timestamp


@a_sync_ttl_cache
@eth_retry.auto_retry
async def get_block_timestamp_async(height: int) -> int:
    """
    Asynchronously get the timestamp of a block by its height.

    Args:
        height: The block height.

    Returns:
        The timestamp of the block.

    Examples:
        >>> await get_block_timestamp_async(12345678)
        1609459200

    See Also:
        - :func:`get_block_timestamp`
        - :func:`get_block_at_timestamp`
    """
    import y._db.utils.utils as db

    if ts := await db.get_block_timestamp(height, sync=False):
        return ts
    client = await get_ethereum_client_async()
    if client in ("tg", "erigon") and _CHAINID not in (Network.Polygon,):
        # NOTE: polygon erigon does not support this method
        header = await dank_mids.web3.manager.coro_request(
            f"{client}_getHeaderByNumber", [height]
        )
        ts = int(header.timestamp, 16)
    else:
        ts = await dank_mids.eth.get_block_timestamp(height)
    db.set_block_timestamp(height, ts)
    return ts


# TODO: deprecate
@memory.cache()
def last_block_on_date(date: Union[str, datetime.date]) -> int:
    """
    Returns the last block on a given date. You can pass either a `datetime.date` object or a date string formatted as 'YYYY-MM-DD'.

    .. warning::
        This function is marked for deprecation and may be removed in future versions. It is recommended to use alternative methods for obtaining block information.

    Args:
        date: The date for which to find the last block.

    Returns:
        The block number of the last block on the given date.

    Raises:
        TypeError: If a `datetime.datetime` object is passed instead of a `datetime.date`.

    Example:
        >>> last_block_on_date('2023-01-01')
        12345678

    See Also:
        - :func:`get_block_timestamp`
        - :func:`get_block_timestamp_async`
    """
    if isinstance(date, datetime.datetime):
        raise TypeError(
            "You can not pass in a `datetime.datetime` object. Please call date() on your input before passing it to this function."
        )
    if not isinstance(date, datetime.date):
        date = datetime.datetime.strptime(date, "%Y-%m-%d").date()

    height = chain.height
    lo, hi = 0, height
    while hi - lo > 1:
        mid = lo + (hi - lo) // 2
        logger.debug("block: %s", str(mid))
        mid_ts = get_block_timestamp(mid)
        mid_date = datetime.date.fromtimestamp(mid_ts)
        logger.debug("mid: %s", mid_date)
        logger.debug(date)
        if mid_date > date:
            hi = mid
        else:
            lo = mid
    hi = hi - 1
    block = hi if hi != height else None
    logger.debug("last %s block on date %s -> %s", Network.name(), date, block)
    return block


@a_sync_ttl_cache
async def get_block_at_timestamp(timestamp: datetime.datetime) -> int:
    """
    Get the block number just before a specific timestamp.

    This function returns the block number at the given timestamp, which is the block number just before the specified timestamp.

    Args:
        timestamp: The timestamp to find the block for.

    Returns:
        The block number just before the given timestamp.

    Example:
        >>> await get_block_at_timestamp(datetime.datetime(2023, 1, 1))
        12345678

    See Also:
        - :func:`get_block_timestamp`
        - :func:`get_block_timestamp_async`
    """
    import y._db.utils.utils as db

    if block_at_timestamp := await db.get_block_at_timestamp(timestamp):
        return block_at_timestamp

    # TODO: invert this and use this fn inside of closest_block_after_timestamp for backwards compatibility before deprecating closest_block_after_timestamp
    block_after_timestamp = await closest_block_after_timestamp_async(timestamp)
    block_at_timestamp = block_after_timestamp - 1
    db.set_block_at_timestamp(timestamp, block_at_timestamp)
    return block_at_timestamp


def _parse_timestamp(timestamp: Timestamp) -> UnixTimestamp:
    """
    Parse a timestamp into a Unix timestamp.

    Args:
        timestamp: The timestamp to parse.

    Returns:
        The Unix timestamp.

    Raises:
        TypeError: If the input is not a valid timestamp type.

    Examples:
        >>> _parse_timestamp(datetime.datetime(2023, 1, 1))
        1672531200
        >>> _parse_timestamp(1672531200)
        1672531200
    """
    if isinstance(timestamp, datetime.datetime):
        timestamp = int(timestamp.timestamp())
    elif not isinstance(timestamp, int):
        raise TypeError("You may only pass in a unix timestamp or a datetime object.")
    return UnixTimestamp(timestamp)


# yLazyLogger(logger)
def closest_block_after_timestamp(
    timestamp: Timestamp, wait_for_block_if_needed: bool = False
) -> int:
    """
    Get the closest block after a given timestamp.

    Args:
        timestamp: The timestamp to find the closest block after.
        wait_for_block_if_needed: Whether to wait for a block if needed.

    Returns:
        The block number closest after the given timestamp.

    Raises:
        NoBlockFound: If no block is found after the timestamp.

    Example:
        >>> closest_block_after_timestamp(1672531199)
        12345678

    See Also:
        - :func:`get_block_at_timestamp`
        - :func:`get_block_timestamp`
    """
    timestamp = _parse_timestamp(timestamp)
    while wait_for_block_if_needed:
        try:
            return closest_block_after_timestamp(timestamp)
        except NoBlockFound:
            time.sleep(0.2)
    check_node()
    block = _closest_block_after_timestamp_cached(timestamp)
    logger.debug(
        "closest %s block after timestamp %s -> %s", Network.name(), timestamp, block
    )
    return block


@a_sync_ttl_cache
async def closest_block_after_timestamp_async(
    timestamp: Timestamp, wait_for_block_if_needed: bool = False
) -> int:
    """
    Asynchronously get the closest block after a given timestamp.

    Args:
        timestamp: The timestamp to find the closest block after.
        wait_for_block_if_needed: Whether to wait for a block if needed.

    Returns:
        The block number closest after the given timestamp.

    Raises:
        NoBlockFound: If no block is found after the timestamp.

    Example:
        >>> await closest_block_after_timestamp_async(1672531199)
        12345678

    See Also:
        - :func:`get_block_at_timestamp`
        - :func:`get_block_timestamp_async`
    """
    timestamp = _parse_timestamp(timestamp)
    while wait_for_block_if_needed:
        try:
            block_at_ts = await get_block_at_timestamp(
                datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc),
                sync=False,
            )
            return block_at_ts + 1
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
    """
    Check if the Ethereum node is synced.

    Raises:
        y.exceptions.NodeNotSynced: If the node is not synced.

    Examples:
        >>> check_node()
    """
    if GANACHE_FORK:
        return
    current_time = time.time()
    node_timestamp = web3.eth.get_block("latest").timestamp
    if current_time - node_timestamp > 5 * 60:
        raise NodeNotSynced(
            f"current time: {current_time}  latest block time: {node_timestamp}  discrepancy: {round((current_time - node_timestamp) / 60, 2)} minutes"
        )


@alru_cache(ttl=300)
@eth_retry.auto_retry
async def check_node_async() -> None:
    """
    Asynchronously check if the Ethereum node is synced.

    Raises:
        y.exceptions.NodeNotSynced: If the node is not synced.

    Examples:
        >>> await check_node_async()
    """
    if GANACHE_FORK:
        return
    current_time = time.time()
    node_timestamp = await dank_mids.eth.get_block_timestamp("latest")
    if current_time - node_timestamp > 5 * 60:
        raise NodeNotSynced(
            f"current time: {current_time}  latest block time: {node_timestamp}  discrepancy: {round((current_time - node_timestamp) / 60, 2)} minutes"
        )
