
import logging
from datetime import datetime
from functools import lru_cache
from typing import Optional

from a_sync import a_sync
from brownie import chain
from pony.orm import db_session

from y._db.common import token_attr_threads
from y._db.entities import Block, Chain, insert, retry_locked
from y._db.utils._ep import _get_get_block

logger = logging.getLogger(__name__)

@a_sync(default='async', executor=token_attr_threads)
@db_session
@retry_locked
def get_chain() -> Chain:
    return Chain.get(id=chain.id) or insert(type=Chain, id=chain.id) or Chain[chain.id]

@lru_cache
def ensure_chain() -> None:
    get_chain(sync=True)

@a_sync(default='async', executor=token_attr_threads)
@db_session
@retry_locked
def get_block(number: int) -> Block:
    ensure_chain()
    if block := Block.get(chain=chain.id, number=number):
        return block
    return insert(type=Block, chain=chain.id, number=number) or get_block(number, sync=True)

@a_sync(default='async', executor=token_attr_threads)
@db_session
@retry_locked
def get_block_timestamp(number: int) -> Optional[int]:
    get_block = _get_get_block()
    if ts := get_block(number, sync=True).timestamp:
        return ts.timestamp()
    
@a_sync(default='async', executor=token_attr_threads)
@db_session
@retry_locked
def set_block_timestamp(block: int, timestamp: int) -> None:
    get_block = _get_get_block()
    get_block(block, sync=True).timestamp = datetime.fromtimestamp(timestamp)
