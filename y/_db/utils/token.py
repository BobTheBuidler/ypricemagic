
import logging
import threading
from functools import lru_cache
from typing import Dict, Optional, Set

import a_sync
from brownie import chain, convert
from cachetools import TTLCache, cached
from pony.orm import commit, db_session, select

from y import constants
from y._db.decorators import a_sync_read_db_session, a_sync_write_db_session, log_result_count
from y._db.entities import Address, Token, insert
from y._db.exceptions import EEEError
from y._db.utils._ep import _get_get_token
from y.erc20 import decimals

logger = logging.getLogger(__name__)

@a_sync_read_db_session
def get_token(address: str) -> Token:
    address = convert.to_address(address)
    if address == constants.EEE_ADDRESS:
        raise EEEError(f"cannot create token entity for {constants.EEE_ADDRESS}")
    while True:
        if entity := Address.get(chain=chain.id, address=address):
            if isinstance(entity, Token):
                return entity
            entity.delete()
            commit()
        return insert(type=Token, chain=chain.id, address=address) or Token.get(chain=chain.id, address=address)

@a_sync.a_sync(default='sync', ram_cache_maxsize=None)
def ensure_token(address: str) -> None:
    return _ensure_token(address)

@lru_cache(maxsize=None)
@db_session
def _ensure_token(address: str) -> None:
    """We can't wrap a `_Wrapped` object with `a_sync` so we have this helper fn"""
    if address not in known_tokens():
        get_token = _get_get_token()
        get_token(address, sync=True)

@a_sync_read_db_session
def get_bucket(address: str) -> Optional[str]:
    if address == constants.EEE_ADDRESS:
        return
    if (bucket := known_buckets().pop(address, None)) is None:
        get_token = _get_get_token()
        bucket = get_token(address, sync=True).bucket
    if bucket:
        logger.debug("found %s bucket %s in ydb", address, bucket)
    return bucket

@a_sync_write_db_session
def _set_bucket(address: str, bucket: str) -> None:
    if address == constants.EEE_ADDRESS:
        return
    get_token = _get_get_token()
    get_token(address, sync=True).bucket = bucket
    logger.debug("updated %s bucket in ydb: %s", address, bucket)

set_bucket = a_sync.ProcessingQueue(_set_bucket, num_workers=10, return_data=False)

@a_sync_read_db_session
def get_symbol(address: str) -> Optional[str]:
    if (symbol := known_symbols().pop(address, None)) is None:
        get_token = _get_get_token()
        symbol = get_token(address, sync=True).symbol
    if symbol:
        logger.debug("found %s symbol %s in ydb", address, symbol)
    return symbol

def set_symbol(address: str, symbol: str):
    if not symbol:
        raise ValueError("`symbol` is required")
    if not isinstance(symbol, str):
        raise TypeError(f"`symbol` must be a string. You passed {symbol}")
    a_sync.create_task(
        coro=_set_symbol(address, symbol), 
        name=f"set_symbol {symbol} for {address}",
        skip_gc_until_done=True,
    )

@a_sync_read_db_session
def get_name(address: str) -> Optional[str]:
    if (name := known_names().pop(address, None)) is None:
        get_token = _get_get_token()
        name = get_token(address, sync=True).name
    if name:
        logger.debug("found %s name %s in ydb", address, name)
    return name

def set_name(address: str, name: str) -> None:
    if not name:
        raise ValueError("`name` is required")
    if not isinstance(name, str):
        raise TypeError(f"`name` must be a string. You passed {name}")
    a_sync.create_task(
        coro=_set_name(address, name), 
        name=f"set_name {name} for {address}",
        skip_gc_until_done=True,
    )

async def get_decimals(address: str) -> int:
    d = await _get_token_decimals(address)
    if d is None:
        d = await decimals(address, sync=False)
        if d:
            if d > 2147483647:
                # raise this here so the task doesnt break
                # TODO debug where this comes from
                raise ValueError(f"Value {d} of attr Token.decimals is greater than the maximum allowed value 2147483647")
            a_sync.create_task(coro=set_decimals(address, d), name=f"set_decimals {address}", skip_gc_until_done=True)
    return d

@a_sync_write_db_session
def set_decimals(address: str, decimals: int) -> None:
    get_token = _get_get_token()
    get_token(address, sync=True).decimals = decimals
    logger.debug("updated %s decimals in ydb: %s", address, decimals)

@a_sync_write_db_session
def _set_symbol(address: str, symbol: str) -> None:
    get_token = _get_get_token()
    get_token(address, sync=True).symbol = symbol
    logger.debug("updated %s symbol in ydb: %s", address, symbol)
    
@a_sync_write_db_session
def _set_name(address: str, name: str) -> None:
    get_token = _get_get_token()
    get_token(address, sync=True).name = name
    logger.debug("updated %s name in ydb: %s", address, name)

@a_sync_read_db_session
def _get_token_decimals(address: str) -> Optional[int]:
    if (decimals := known_decimals().pop(address, None)) is None:
        get_token = _get_get_token()
        decimals = get_token(address, sync=True).decimals
    if decimals:
        logger.debug("found %s decimals %s in ydb", address, decimals)
        return decimals


# startup caches
    
@cached(TTLCache(maxsize=1, ttl=60*60), lock=threading.Lock())
@db_session
@log_result_count("tokens")
def known_tokens() -> Set[str]:
    """cache and return all known Tokens for this chain to minimize db reads"""
    return set(select(t.address for t in Token if t.chain.id == chain.id))

@cached(TTLCache(maxsize=1, ttl=60*60), lock=threading.Lock())
@log_result_count("buckets")
def known_buckets() -> Dict[str, str]:
    """cache and return all known token buckets for this chain to minimize db reads"""
    return dict(select((t.address, t.bucket) for t in Token if t.chain.id == chain.id and t.bucket))

@cached(TTLCache(maxsize=1, ttl=60*60), lock=threading.Lock())
@log_result_count("token decimals")
def known_decimals() -> Dict[Address, int]:
    """cache and return all known token decimals for this chain to minimize db reads"""
    return dict(select((t.address, t.decimals) for t in Token if t.chain.id == chain.id and t.decimals))

@cached(TTLCache(maxsize=1, ttl=60*60), lock=threading.Lock())
@log_result_count("token symbols")
def known_symbols() -> Dict[Address, str]:
    """cache and return all known token symbols for this chain to minimize db reads"""
    return dict(select((t.address, t.symbol) for t in Token if t.chain.id == chain.id and t.symbol))

@cached(TTLCache(maxsize=1, ttl=60*60), lock=threading.Lock())
@log_result_count("token names")
def known_names() -> Dict[Address, str]:
    """cache and return all known token names for this chain to minimize db reads"""
    return dict(select((t.address, t.name) for t in Token if t.chain.id == chain.id and t.name))