
import asyncio
import logging
from typing import Optional

from a_sync import a_sync
from brownie import convert
from pony.orm import commit, db_session

from y import constants
from y._db.common import executor
from y._db.entities import Address, Token, insert, retry_locked
from y._db.utils._ep import _get_get_token
from y._db.utils.utils import get_chain
from y.erc20 import decimals

logger = logging.getLogger(__name__)

@a_sync(default='async', executor=executor)
@db_session
@retry_locked
def get_token(address: str) -> Token:
    address = convert.to_address(address)
    if address == constants.EEE_ADDRESS:
        raise ValueError(f"cannot create token entity for {constants.EEE_ADDRESS}")
    while True:
        if entity := Address.get(chain=get_chain(sync=True), address=address):
            if isinstance(entity, Token):
                return entity
            entity.delete()
            commit()
        return insert(type=Token, chain=get_chain(sync=True), address=address) or Token.get(chain=get_chain(sync=True), address=address)
        
@a_sync(default='async', executor=executor)
@db_session
@retry_locked
def get_bucket(address: str) -> Optional[str]:
    if address == constants.EEE_ADDRESS:
        return
    get_token = _get_get_token()
    return get_token(address, sync=True).bucket

@a_sync(default='async', executor=executor)
@db_session
@retry_locked
def set_bucket(address: str, bucket: str) -> None:
    if address == constants.EEE_ADDRESS:
        return
    get_token = _get_get_token()
    get_token(address, sync=True).bucket = bucket

@a_sync(default='async', executor=executor)
@db_session
@retry_locked
def get_symbol(address: str) -> Optional[str]:
    get_token = _get_get_token()
    return get_token(address, sync=True).symbol

@a_sync(default='async', executor=executor)
@db_session
@retry_locked
def set_symbol(address: str, symbol: str) -> None:
    get_token = _get_get_token()
    get_token(address, sync=True).symbol = symbol

@a_sync(default='async', executor=executor)
@db_session
@retry_locked
def get_name(address: str) -> Optional[str]:
    get_token = _get_get_token()
    return get_token(address, sync=True).name

@a_sync(default='async', executor=executor)
@db_session
@retry_locked
def set_name(address: str, name: str) -> None:
    get_token = _get_get_token()
    get_token(address, sync=True).name = name

async def get_decimals(address: str) -> int:
    d = await _get_token_decimals(address)
    if d is None:
        d = await decimals(address, sync=False)
        if d:
            asyncio.create_task(set_decimals(address, d))
    return d

@a_sync(default='async', executor=executor)
@db_session
@retry_locked
def _get_token_decimals(address: str) -> Optional[int]:
    get_token = _get_get_token()
    return get_token(address, sync=True).decimals

@a_sync(default='async', executor=executor)
@db_session
@retry_locked
def set_decimals(address: str, decimals: int) -> None:
    get_token = _get_get_token()
    get_token(address, sync=True).decimals = decimals
