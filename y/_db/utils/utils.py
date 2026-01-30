from datetime import datetime, timezone
from functools import lru_cache
from logging import getLogger

from a_sync import ProcessingQueue, a_sync
from brownie import chain
from dateutil import parser
from eth_typing import BlockNumber
from pony.orm import TransactionIntegrityError, commit, select

from y._db.common import make_executor
from y._db.decorators import (
    a_sync_read_db_session,
    db_session_cached,
    db_session_retry_locked,
    log_result_count,
)
from y._db.entities import Block, BlockAtTimestamp, Chain, insert

logger = getLogger(__name__)
_logger_debug = logger.debug

CHAINID = chain.id
del chain


_block_executor = make_executor(2, 8, "ypricemagic db executor [block]")
_timestamp_executor = make_executor(1, 4, "ypricemagic db executor [timestamp]")


@a_sync_read_db_session
def get_chain() -> Chain:
    """Retrieve the current blockchain chain object from the database.

    If the chain object does not exist, it inserts a new one.

    Returns:
        The Chain object for the current blockchain.

    Examples:
        >>> chain = get_chain()
        >>> print(chain.id)

    See Also:
        - :class:`Chain`
        - :func:`insert`
    """
    return Chain.get(id=CHAINID) or insert(type=Chain, id=CHAINID) or Chain[CHAINID]


@lru_cache
def ensure_chain() -> None:
    """Ensures that the chain object for the connected chain has been inserted to the db.

    This function commits the chain object to the database if it does not already exist.

    Examples:
        >>> ensure_chain()

    See Also:
        - :func:`get_chain`
    """
    get_chain(sync=True)
    commit()


@a_sync_read_db_session
def get_block(number: int) -> Block:
    """Retrieve a block by its number from the database.

    If the block does not exist, it inserts a new one.

    Args:
        number: The block number to retrieve.

    Returns:
        The Block object for the specified block number.

    Examples:
        >>> block = get_block(123456)
        >>> print(block.number)

    See Also:
        - :class:`Block`
        - :func:`insert`
    """
    if block := Block.get(chain=CHAINID, number=number):
        return block
    return insert(type=Block, chain=CHAINID, number=number) or get_block(number, sync=True)


@a_sync(
    default="async",
    executor=_block_executor,
    ram_cache_maxsize=None,
)
@db_session_cached
def ensure_block(number: int) -> None:
    """Ensure that a block is known in the database.

    If the block is not known, it retrieves and caches the block.

    Args:
        number: The block number to ensure.

    Examples:
        >>> ensure_block(123456)

    See Also:
        - :func:`get_block`
        - :func:`known_blocks`
    """
    from y._db.utils._ep import _get_get_block

    get_block = _get_get_block()
    try:
        get_block(number, sync=True)
    except TransactionIntegrityError:
        get_block(number, sync=True)


@a_sync_read_db_session
def get_block_timestamp(number: int) -> int | None:
    """Retrieve the timestamp for a given block number.

    If the timestamp is not known, it retrieves and caches the block's timestamp.

    Args:
        number: The block number to retrieve the timestamp for.

    Returns:
        The timestamp of the block as a Unix timestamp, or None if not found.

    Examples:
        >>> timestamp = get_block_timestamp(123456)
        >>> print(timestamp)
    """
    from y._db.utils._ep import _get_get_block

    get_block = _get_get_block()
    ts = get_block(number, sync=True).timestamp
    if ts is None:
        return None
    # some db providers return a string here, we must parse it
    if isinstance(ts, str):
        ts = parser.parse(ts)
    unix = ts.timestamp()
    _logger_debug("got Block[%s, %s].timestamp from cache: %s, %s", CHAINID, number, unix, ts)
    return unix


@a_sync_read_db_session
def get_block_at_timestamp(timestamp: datetime) -> BlockNumber | None:
    """Retrieve the block number at a specific timestamp.

    If the block number is not known, it attempts to find it in the database.

    Args:
        timestamp: The timestamp to find the block number for.

    Returns:
        The block number at the given timestamp, or None if not found.

    Examples:
        >>> block_number = get_block_at_timestamp(datetime.now())
        >>> print(block_number)

    See Also:
        - :class:`BlockAtTimestamp`
    """
    if entity := BlockAtTimestamp.get(chainid=CHAINID, timestamp=timestamp):
        block = entity.block
        _logger_debug("found block %s for %s in ydb", block, timestamp)
        return block


@a_sync(default="async", executor=_timestamp_executor)
@db_session_retry_locked
def _set_block_timestamp(block: int, timestamp: int) -> None:
    """Set the timestamp for a specific block in the database.

    Args:
        block: The block number to set the timestamp for.
        timestamp: The timestamp to set for the block.

    Examples:
        >>> _set_block_timestamp(123456, 1609459200)

    See Also:
        - :func:`get_block`
    """
    from y._db.utils._ep import _get_get_block

    get_block = _get_get_block()
    block = get_block(block, sync=True)
    timestamp = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    block.timestamp = timestamp
    _logger_debug("cached %s.timestamp %s", block, timestamp)


def set_block_timestamp(block: int, timestamp: int) -> None:
    """Set the timestamp for a specific block in the database.

    Args:
        block: The block number to set the timestamp for.
        timestamp: The timestamp to set for the block.

    Examples:
        >>> _set_block_timestamp(123456, 1609459200)

    See Also:
        - :func:`get_block`
    """


set_block_timestamp = ProcessingQueue(_set_block_timestamp, num_workers=2, return_data=False)


@a_sync(default="async", executor=_timestamp_executor)
@db_session_retry_locked
def _set_block_at_timestamp(timestamp: datetime, block: int) -> None:
    """Insert a block number for a specific timestamp in the database.

    Args:
        timestamp: The timestamp to associate with the block number.
        block: The block number to insert.

    Examples:
        >>> _set_block_at_timestamp(datetime.now(), 123456)

    See Also:
        - :class:`BlockAtTimestamp`
    """
    insert(BlockAtTimestamp, chainid=CHAINID, timestamp=timestamp, block=block)
    _logger_debug("inserted block %s for %s", block, timestamp)


set_block_at_timestamp = ProcessingQueue(_set_block_at_timestamp, num_workers=2, return_data=False)
