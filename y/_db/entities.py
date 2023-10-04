
from contextlib import suppress
from datetime import datetime
from decimal import Decimal
from typing import Any

from pony.orm import (Database, Optional, PrimaryKey, Required, Set,
                      TransactionIntegrityError, commit, composite_key,
                      db_session)

db = Database()


#E = TypeVar("E", bound=db.Entity)

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
    _pk = PrimaryKey(int, auto=True)
    id = Required(int, unique=True, lazy=True)

    blocks = Set("Block")
    addresses = Set("Address")
    log_cached = Set("LogCacheInfo")
    trace_caches = Set("TraceCacheInfo")

class Block(db.Entity, _AsyncEntityMixin):
    _pk = PrimaryKey(int, auto=True)
    chain = Required(Chain, reverse="blocks")
    number = Required(int, lazy=True)
    hash = Optional(int, lazy=True)
    timestamp = Optional(datetime, lazy=True)
    
    composite_key(chain, number)
    composite_key(chain, hash)

    prices = Set("Price", reverse="block", cascade_delete=False)
    contracts_deployed = Set("Contract", reverse="deploy_block")
    logs = Set("Log", reverse="block", cascade_delete=False)
    traces = Set("Trace", reverse="block", cascade_delete=False)

class Address(db.Entity, _AsyncEntityMixin):
    _pk = PrimaryKey(int, auto=True)
    chain = Required(Chain, lazy=True, reverse="addresses")
    address = Required(str, lazy=True)
    notes = Optional(str, lazy=True)
    
    composite_key(chain, address)

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
    dbid = PrimaryKey(int, auto=True)
    block = Required(Block, index=True, lazy=True)
    token = Required(Token, index=True, lazy=True)
    composite_key(block, token)
    price = Required(Decimal)
    
class TraceCacheInfo(db.Entity):
    chain = Required(Chain, index=True)
    to_addresses = Required(bytes, index=True)
    from_addresses = Required(bytes, index=True)
    composite_key(chain, to_addresses, from_addresses)
    cached_from = Required(int)
    cached_thru = Required(int)

class LogCacheInfo(db.Entity):
    chain = Required(Chain, index=True)
    address = Required(str, index=True)
    topics = Required(bytes)
    composite_key(chain, address, topics)
    cached_from = Required(int)
    cached_thru = Required(int)

class Log(db.Entity):
    block = Required(Block, index=True, lazy=True)
    transaction_hash = Required(str, lazy=True)
    log_index = Required(int, lazy=True)
    composite_key(block, transaction_hash, log_index)

    address = Required(str, index=True, lazy=True)
    topic0 = Required(str, index=True, lazy=True)
    topic1 = Optional(str, index=True, lazy=True)
    topic2 = Optional(str, index=True, lazy=True)
    topic3 = Optional(str, index=True, lazy=True)
    raw = Required(bytes, lazy=True)

class Trace(db.Entity):
    block = Required(Block, index=True, lazy=True)
    hash = Required(str, index=True, lazy=True)
    from_address = Required(str, index=True, lazy=True)
    to_address = Required(str, index=True, lazy=True)
    raw = Required(bytes)

from pony.orm import OperationalError, CommitException
@db_session
def insert(type: db.Entity, **kwargs: Any) -> None:
    while True:
        try:
            with suppress(TransactionIntegrityError):
                type(**kwargs)
                commit()
                return
        except CommitException as e:
            if "database is locked" not in str(e):
                raise e