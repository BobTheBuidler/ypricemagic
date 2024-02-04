
import logging
from functools import lru_cache
from typing import Optional

import a_sync
from brownie import chain, convert
from pony.orm import commit

from y import constants
from y._db.decorators import a_sync_read_db_session, a_sync_write_db_session
from y._db.entities import Address, Token, insert
from y._db.exceptions import EEEError
from y._db.utils._ep import _get_get_token
from y._db.utils.utils import ensure_chain
from y.erc20 import decimals

logger = logging.getLogger(__name__)

@a_sync_read_db_session
def get_token(address: str) -> Token:
    ensure_chain()
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

@lru_cache(maxsize=None)
def ensure_token(address: str) -> None:
    get_token = _get_get_token()
    get_token(address, sync=True)

@a_sync_read_db_session
def get_bucket(address: str) -> Optional[str]:
    if address == constants.EEE_ADDRESS:
        return
    get_token = _get_get_token()
    bucket = get_token(address, sync=True).bucket
    if bucket:
        logger.debug("found %s bucket %s in ydb", address, bucket)
    return bucket

def set_bucket(address: str, bucket: str) -> None:
    a_sync.create_task(
        coro=_set_bucket(address, bucket),
        name=f"set_bucket {address}: {bucket}",
        skip_gc_until_done=True,
    )

@a_sync_write_db_session
def _set_bucket(address: str, bucket: str) -> None:
    if address == constants.EEE_ADDRESS:
        return
    get_token = _get_get_token()
    get_token(address, sync=True).bucket = bucket
    logger.debug("updated %s bucket in ydb: %s", address, bucket)

@a_sync_read_db_session
def get_symbol(address: str) -> Optional[str]:
    get_token = _get_get_token()
    symbol = get_token(address, sync=True).symbol
    if symbol:
        logger.debug("found %s symbol %s in ydb", address, symbol)
    return symbol

def set_symbol(address: str, symbol: str):
    a_sync.create_task(
        coro=_set_symbol(address, symbol), 
        name=f"set_symbol {symbol} for {address}",
        skip_gc_until_done=True,
    )

@a_sync_read_db_session
def get_name(address: str) -> Optional[str]:
    get_token = _get_get_token()
    name = get_token(address, sync=True).name
    if name:
        logger.debug("found %s name %s in ydb", address, name)
    return name

def set_name(address: str, name: str) -> None:
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
    get_token = _get_get_token()
    decimals = get_token(address, sync=True).decimals
    logger.debug("found %s decimals %s in ydb", address, decimals)
    if decimals:
        return decimals
