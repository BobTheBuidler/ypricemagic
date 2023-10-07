
import logging

from a_sync import a_sync
from brownie import chain
from pony.orm import db_session

from y._db.common import executor
from y._db.entities import Block, Chain, insert, retry_locked

logger = logging.getLogger(__name__)

@a_sync(default='async', executor=executor)
@db_session
@retry_locked
def get_chain() -> Chain:
    return Chain.get(id=chain.id) or insert(type=Chain, id=chain.id) or Chain.get(id=chain.id)

@a_sync(default='async', executor=executor)
@db_session
@retry_locked
def get_block(number: int) -> Block:
    chain = get_chain(sync=True)
    if block := Block.get(chain=chain, number=number):
        return block
    return insert(type=Block, chain=chain, number=number) or get_block(number, sync=True)
