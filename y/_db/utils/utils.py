
import logging
from datetime import datetime, timezone
from dateutil import parser
from functools import lru_cache
from typing import Optional

from brownie import chain

from y._db.entities import Block, Chain, insert
from y._db.utils._ep import _get_get_block
from y._db.utils.decorators import a_sync_db_session, a_sync_db_session_cached

logger = logging.getLogger(__name__)


@a_sync_db_session
def get_chain() -> Chain:
    return Chain.get(id=chain.id) or insert(type=Chain, id=chain.id) or Chain[chain.id]

@lru_cache
def ensure_chain() -> None:
    """ensures that the chain object for the connected chain has been inserted to the db"""
    get_chain(sync=True)

@a_sync_db_session
def get_block(number: int) -> Block:
    ensure_chain()
    if block := Block.get(chain=chain.id, number=number):
        return block
    return insert(type=Block, chain=chain.id, number=number) or get_block(number, sync=True)

@a_sync_db_session_cached
def ensure_block(number: int) -> None:
    get_block = _get_get_block()
    get_block(number, sync=True)

@a_sync_db_session
def get_block_timestamp(number: int) -> Optional[int]:
    get_block = _get_get_block()
    block = get_block(number, sync=True)
    if ts := block.timestamp:
        if isinstance(ts, str):
            # TODO: debug why this happens, but only sometimes
            ts = parser.parse(ts)
        unix = ts.timestamp()
        logger.debug("got %s.timestamp from cache: %s, %s", block, unix, ts)
        return unix
    
@a_sync_db_session
def set_block_timestamp(block: int, timestamp: int) -> None:
    get_block = _get_get_block()
    block = get_block(block, sync=True)
    timestamp = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    block.timestamp = timestamp
    logger.debug("cached %s.timestamp %s", block, timestamp)
