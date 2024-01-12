
import logging
from contextlib import suppress
from datetime import datetime
from decimal import Decimal
from functools import wraps
from typing import Any
from typing import Optional as typing_Optional

from pony.orm import (Database, InterfaceError, Optional, PrimaryKey, 
                      Required, Set, TransactionIntegrityError, commit,
                      composite_index, db_session)

db = Database()


logger = logging.getLogger(__name__)

class _AsyncEntityMixin:
    pass
    '''
    @classmethod
    @a_sync('async')
    def get(cls: E, *args, **kwargs) -> E:
        return super(db.Entity).get(*args, **kwargs)
    @classmethod
    @a_sync('async')
    def select(cls: E, *args, **kwargs) -> E:
        return super(db.Entity).select(*args, **kwargs)'''
    
class Chain(db.Entity, _AsyncEntityMixin):
    id = PrimaryKey(int)

    blocks = Set("Block")
    addresses = Set("Address")
    log_cached = Set("LogCacheInfo")
    trace_caches = Set("TraceCacheInfo")

class Block(db.Entity, _AsyncEntityMixin):
    chain = Required(Chain, reverse="blocks")
    number = Required(int)
    PrimaryKey(chain, number)
    hash = Optional(int, lazy=True)
    timestamp = Optional(datetime, lazy=True)
    
    composite_index(chain, hash)

    prices = Set("Price", reverse="block", cascade_delete=False)
    contracts_deployed = Set("Contract", reverse="deploy_block")
    logs = Set("Log", reverse="block", cascade_delete=False)
    traces = Set("Trace", reverse="block", cascade_delete=False)

class Address(db.Entity, _AsyncEntityMixin):
    chain = Required(Chain, lazy=True, reverse="addresses")
    address = Required(str, lazy=True)
    PrimaryKey(chain, address)
    notes = Optional(str, lazy=True)
    
    contracts_deployed = Set("Contract", reverse="deployer")

class Contract(Address):
    deployer = Optional(Address, reverse='contracts_deployed', lazy=True, cascade_delete=False)
    deploy_block = Optional(Block, reverse='contracts_deployed', lazy=True, cascade_delete=False)

class Token(Contract):
    symbol = Optional(str, lazy=True)
    name = Optional(str, lazy=True)
    decimals = Optional(int, lazy=True)
    bucket = Optional(str, index=True, lazy=True)

    prices = Set("Price", reverse="token")

class Price(db.Entity):
    block = Required(Block, index=True, lazy=True)
    token = Required(Token, index=True, lazy=True)
    PrimaryKey(block, token)
    price = Required(Decimal, 38, 18)
    
class TraceCacheInfo(db.Entity):
    chain = Required(Chain, index=True)
    to_addresses = Required(bytes, index=True)
    from_addresses = Required(bytes, index=True)
    PrimaryKey(chain, to_addresses, from_addresses)
    cached_from = Required(int)
    cached_thru = Required(int)

class LogCacheInfo(db.Entity):
    chain = Required(Chain, index=True)
    address = Required(str, index=True)
    topics = Required(bytes)
    PrimaryKey(chain, address, topics)
    cached_from = Required(int)
    cached_thru = Required(int)

class Log(db.Entity):
    block = Required(Block, index=True, lazy=True)
    transaction_hash = Required(str, lazy=True)
    log_index = Required(int, lazy=True)
    PrimaryKey(block, transaction_hash, log_index)

    address = Required(str, index=True, lazy=True)
    topic0 = Required(str, index=True, lazy=True)
    topic1 = Optional(str, index=True, lazy=True)
    topic2 = Optional(str, index=True, lazy=True)
    topic3 = Optional(str, index=True, lazy=True)
    composite_index(address, topic0)
    composite_index(topic0, topic1)
    composite_index(topic0, topic2)
    composite_index(topic0, topic3)
    composite_index(block, address, topic0)
    composite_index(block, topic0, topic1)
    composite_index(block, topic0, topic2)
    composite_index(block, topic0, topic3)
    composite_index(topic0, topic1, topic2, topic3)
    composite_index(block, topic0, topic1, topic2, topic3)
    raw = Required(bytes, lazy=True)

class Trace(db.Entity):
    id = PrimaryKey(int, auto=True)
    block = Required(Block, index=True, lazy=True)
    hash = Required(str, index=True, lazy=True)
    from_address = Required(str, index=True, lazy=True)
    to_address = Required(str, index=True, lazy=True)
    raw = Required(bytes)

class BlockAtTimestamp(db.Entity):
    chainid = Required(int)
    timestamp = Required(datetime)
    PrimaryKey(chainid, timestamp)
    block = Required(int)


@db_session
def insert(type: db.Entity, **kwargs: Any) -> typing_Optional[db.Entity]:
    try:
        while True:
            try:
                entity = type(**kwargs)
                commit()
                logger.debug("inserted %s to db", entity)
                return entity
            except InterfaceError as e:
                logger.debug("%s while inserting %s", e, type.__name__)
    except TransactionIntegrityError as e:
        constraint_errs = "UNIQUE constraint failed", "duplicate key value violates unique constraint"
        if any(err in (msg:=str(e)) for err in constraint_errs):
            logger.debug("%s: %s %s", msg, type.__name__, kwargs)
        else:
            logger.debug("%s %s when inserting %s", e.__class__.__name__, str(e), e, type.__name__)
            raise e
