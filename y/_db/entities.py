
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

class Block(db.Entity, _AsyncEntityMixin):
    _pk = PrimaryKey(int, auto=True)
    chain = Required(Chain, reverse="blocks")
    number = Required(int, lazy=True)
    hash = Optional(int, lazy=True)
    timestamp = Optional(datetime, lazy=True)
    
    composite_key(chain, number)
    composite_key(chain, hash)

    contracts_deployed = Set("Contract", reverse="deploy_block")

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
