
import logging
from datetime import datetime, timezone
from dateutil import parser
from functools import lru_cache
from typing import Dict, Optional, Set

import a_sync
from pony.orm import commit, select
from brownie import chain

from y._db.decorators import a_sync_read_db_session, a_sync_write_db_session, a_sync_write_db_session_cached, log_result_count
from y._db.entities import Block, BlockAtTimestamp, Chain, insert

logger = logging.getLogger(__name__)


@a_sync_read_db_session
def get_chain() -> Chain:
    return Chain.get(id=chain.id) or insert(type=Chain, id=chain.id) or Chain[chain.id]

@lru_cache
def ensure_chain() -> None:
    """ensures that the chain object for the connected chain has been inserted to the db"""
    get_chain(sync=True)
    commit()

@a_sync_read_db_session
def get_block(number: int) -> Block:
    if block := Block.get(chain=chain.id, number=number):
        return block
    return insert(type=Block, chain=chain.id, number=number) or get_block(number, sync=True)

@a_sync_write_db_session_cached
def ensure_block(number: int) -> None:
    if number not in known_blocks():
        from y._db.utils._ep import _get_get_block
        get_block = _get_get_block()
        get_block(number, sync=True)

@a_sync_read_db_session
def get_block_timestamp(number: int) -> Optional[int]:
    if (ts := known_block_timestamps().pop(number, None)) is None:
        from y._db.utils._ep import _get_get_block
        get_block = _get_get_block()
        ts = get_block(number, sync=True).timestamp
    if ts:
        # some db providers return a string here, we must parse it
        if isinstance(ts, str):
            ts = parser.parse(ts)
        unix = ts.timestamp()
        logger.debug("got Block[%s, %s].timestamp from cache: %s, %s", chain.id, number, unix, ts)
        return unix

@a_sync_read_db_session
def get_block_at_timestamp(timestamp: datetime) -> Optional[int]:
    if block := known_blocks_for_timestamps().pop(timestamp, None):
        logger.debug("found block %s for %s in ydb", block, timestamp)
        return block
    elif entity := BlockAtTimestamp.get(chainid=chain.id, timestamp=timestamp):
        block = entity.block
        logger.debug("found block %s for %s in ydb", block, timestamp)
        return block

@a_sync_write_db_session
def _set_block_timestamp(block: int, timestamp: int) -> None:
    from y._db.utils._ep import _get_get_block
    get_block = _get_get_block()
    block = get_block(block, sync=True)
    timestamp = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    block.timestamp = timestamp
    logger.debug("cached %s.timestamp %s", block, timestamp)

set_block_timestamp = a_sync.ProcessingQueue(_set_block_timestamp, num_workers=10, return_data=False)

@a_sync_write_db_session
def _set_block_at_timestamp(timestamp: datetime, block: int) -> None:
    insert(BlockAtTimestamp, chainid=chain.id, timestamp=timestamp, block=block)
    logger.debug("inserted block %s for %s", block, timestamp)

set_block_at_timestamp = a_sync.ProcessingQueue(_set_block_at_timestamp, num_workers=10, return_data=False)

# startup caches

@lru_cache(maxsize=1)
@log_result_count("blocks")
def known_blocks() -> Set[int]:
    """cache and return all known blocks for this chain to minimize db reads"""
    return set(select(b.number for b in Block if b.chain.id == chain.id))

@lru_cache(maxsize=1)
@log_result_count("block timestamps")
def known_block_timestamps() -> Dict[int, datetime]:
    """cache and return all known block timestamps for this chain to minimize db reads"""
    query = select((b.number, b.timestamp) for b in Block if b.chain.id == chain.id and b.timestamp)
    page_size = 100_000
    timestamps = {}
    for i in range((query.count() // page_size) + 1):
        for block, timestamp in query.page(i+1, page_size):
            timestamps[block] = timestamp
    return timestamps

@lru_cache(maxsize=1)
@log_result_count("blocks for timestamps")
def known_blocks_for_timestamps() -> Dict[datetime, int]:
    """return all known blocks for timestamps for this chain to minimize db reads"""
    return dict(select((x.timestamp, x.block) for x in BlockAtTimestamp if x.chainid == chain.id))
