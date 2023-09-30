
from datetime import datetime

from pony.orm import (Database, Optional, PrimaryKey, Required, Set,
                      composite_key)

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

class Block(db.Entity, _AsyncEntityMixin):
    _pk = PrimaryKey(int, auto=True)
    chain = Required(Chain, reverse="blocks")
    number = Required(int, lazy=True)
    hash = Optional(int, lazy=True)
    timestamp = Optional(datetime, lazy=True)
    
    composite_key(chain, number)
    composite_key(chain, hash)

    contracts_deployed = Set("Contract", reverse="deploy_block")
    logs = Set("Log", reverse="block")

class Address(db.Entity, _AsyncEntityMixin):
    _pk = PrimaryKey(int, auto=True)
    chain = Required(Chain, lazy=True, reverse="addresses")
    address = Required(str, lazy=True)
    notes = Optional(str, lazy=True)
    
    composite_key(chain, address)

    contracts_deployed = Set("Contract", reverse="deployer")

class Contract(Address):
    deployer = Optional(Address, reverse='contracts_deployed', lazy=True)
    deploy_block = Optional(Block, reverse='contracts_deployed', lazy=True)

class Token(Contract):
    symbol = Optional(str, lazy=True)
    name = Optional(str, lazy=True)
    decimals = Optional(int, lazy=True)
    bucket = Optional(str, lazy=True)

class LogCacheInfo(db.Entity):
    chain = Required(Chain)
    address = Optional(str)
    topics = Required(bytes)
    composite_key(chain, address, topics)
    cached_from = Required(int)
    cached_thru = Required(int)

class Log(db.Entity):
    block = Required(Block, lazy=True)
    transaction_hash = Required(str, lazy=True)
    log_index = Required(int, lazy=True)
    composite_key(block, transaction_hash, log_index)

    address = Required(str, lazy=True)
    topic0 = Optional(str, lazy=True)
    topic1 = Optional(str, lazy=True)
    topic2 = Optional(str, lazy=True)
    topic3 = Optional(str, lazy=True)
    raw = Required(bytes, lazy=True)
