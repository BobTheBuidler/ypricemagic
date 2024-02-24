
import logging
from datetime import datetime, timezone
from dateutil import parser
from functools import lru_cache
from typing import Dict, Optional, Set

import a_sync
from cachetools.func import ttl_cache
from pony.orm import select
from brownie import chain

from y._db.decorators import a_sync_read_db_session, a_sync_write_db_session, a_sync_write_db_session_cached
from y._db.entities import Block, BlockAtTimestamp, Chain, insert
from y._db.utils._ep import _get_get_block

logger = logging.getLogger(__name__)


@a_sync_read_db_session
def get_chain() -> Chain:
    return Chain.get(id=chain.id) or insert(type=Chain, id=chain.id) or Chain[chain.id]

@lru_cache
def ensure_chain() -> None:
    """ensures that the chain object for the connected chain has been inserted to the db"""
    get_chain(sync=True)

@a_sync_read_db_session
def get_block(number: int) -> Block:
    ensure_chain()
    if block := Block.get(chain=chain.id, number=number):
        return block
    return insert(type=Block, chain=chain.id, number=number) or get_block(number, sync=True)

@a_sync_write_db_session_cached
def ensure_block(number: int) -> None:
    if number not in known_blocks():
        get_block = _get_get_block()
        get_block(number, sync=True)

@a_sync_read_db_session
def get_block_timestamp(number: int) -> Optional[int]:
    if (ts := known_block_timestamps().get(number)) is None:
        get_block = _get_get_block()
        block = get_block(number, sync=True)
    if ts := ts or block.timestamp:
        if isinstance(ts, str):
            # TODO: debug why this happens, but only sometimes
            ts = parser.parse(ts)
        unix = ts.timestamp()
        logger.debug("got %s.timestamp from cache: %s, %s", block, unix, ts)
        return unix
    
def set_block_timestamp(block: int, timestamp: int) -> None:
    a_sync.create_task(
        coro=_set_block_timestamp(block, timestamp),
        name=f"set_block_timestamp {block}: {timestamp}",
        skip_gc_until_done=True,
    )

@a_sync_read_db_session
def get_block_at_timestamp(timestamp: datetime) -> Optional[int]:
    if block := known_blocks_for_timestamps().get(timestamp):
        logger.debug("found block %s for %s in ydb", block, timestamp)
        return block
    elif entity := BlockAtTimestamp.get(chainid=chain.id, timestamp=timestamp):
        block = entity.block
        logger.debug("found block %s for %s in ydb", block, timestamp)
        return block
    
def set_block_at_timestamp(timestamp: datetime, block: int) -> None:
    a_sync.create_task(
        coro=_set_block_at_timestamp(timestamp, block),
        name=f"set_block_at_timestamp {timestamp}: {block}",
        skip_gc_until_done=True,
    )

@a_sync_write_db_session
def _set_block_timestamp(block: int, timestamp: int) -> None:
    get_block = _get_get_block()
    block = get_block(block, sync=True)
    timestamp = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    block.timestamp = timestamp
    logger.debug("cached %s.timestamp %s", block, timestamp)

@a_sync_write_db_session
def _set_block_at_timestamp(timestamp: datetime, block: int) -> None:
    insert(BlockAtTimestamp, chainid=chain.id, timestamp=timestamp, block=block)
    logger.debug("inserted block %s for %s", block, timestamp)


# startup caches
    
@ttl_cache(maxsize=1, ttl=60*60)
def known_blocks() -> Set[int]:
    """cache and return all known blocks for this chain to minimize db reads"""
    return set(select(b.number for b in Block if b.chain.id == chain.id))

@ttl_cache(maxsize=1, ttl=60*60)
def known_block_timestamps() -> Dict[int, datetime]:
    """cache and return all known block timestamps for this chain to minimize db reads"""
    return dict(select((b.number, b.timestamp) for b in Block if b.chain.id == chain.id and b.timestamp))

@ttl_cache(maxsize=1, ttl=60*60)
def known_blocks_for_timestamps() -> Dict[datetime, int]:
    """return all known blocks for timestamps for this chain to minimize db reads"""
    return dict(select((x.timestamp, x.block) for x in BlockAtTimestamp if x.chainid == chain.id))
