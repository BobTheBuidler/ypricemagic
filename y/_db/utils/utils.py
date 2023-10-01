
import logging
from contextlib import suppress

from a_sync import a_sync
from brownie import chain
from pony.orm import TransactionIntegrityError, commit, db_session

from y._db.entities import Block, Chain
from y._db.utils.common import executor


logger = logging.getLogger(__name__)

@a_sync(default='async', executor=executor)
@db_session
def get_chain() -> Chain:
    if c:=Chain.get(id=chain.id):
        return c
    with suppress(TransactionIntegrityError):
        Chain(id=chain.id)
        commit()
        logger.debug('chain %s added to ydb', chain.id)
    return Chain.get(id=chain.id)

@a_sync(default='async', executor=executor)
@db_session
def get_block(number: int) -> Block:
    chain = get_chain(sync=True)
    if block := Block.get(chain=chain, number=number):
        return block
    with suppress(TransactionIntegrityError):
        block = Block(chain=chain, number=number)
        commit()
    return Block.get(chain=get_chain(sync=True), number=number)
