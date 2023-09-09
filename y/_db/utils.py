
import logging
from concurrent.futures import ThreadPoolExecutor
from contextlib import suppress
from typing import Optional

from a_sync import a_sync
from brownie import chain, convert
from pony.orm import TransactionError, TransactionIntegrityError, commit, db_session

from y._db.config import connection_settings
from y._db.entities import Chain, Token, db
from y.constants import EEE_ADDRESS
from y.erc20 import decimals

logger = logging.getLogger(__name__)

try:
    db.bind(**connection_settings, create_db=True)
    db.generate_mapping(create_tables=True)
except TransactionError as e:
    if str(e) != "@db_session-decorated create_tables() function with `ddl` option cannot be called inside of another db_session":
        raise e
except TypeError as e:
    if not str(e).startswith('Database object was already bound to'):
        raise e


async def get_token_decimals(address: str) -> int:
    d = await _get_token_decimals(address)
    if d is None:
        d = await decimals(address, sync=False)
        await _set_token_decimals(address, d)
    return d


executor = ThreadPoolExecutor(16)

@a_sync(default='async', executor=executor)
@db_session
def get_chain() -> Chain:
    if c:=Chain.get(id=chain.id):
        return c
    with suppress(TransactionIntegrityError):
        Chain(id=chain.id)
        commit()
        logger.debug('chain %s added to ydb')
    return Chain.get(id=chain.id)

@a_sync(default='async', executor=executor)
@db_session
def get_token(address: str) -> Token:
    address = convert.to_address(address)
    if address == EEE_ADDRESS:
        raise ValueError(f"cannot create token entity for {EEE_ADDRESS}")
    chain = get_chain(sync=True)
    if token := Token.get(chain=chain, address=address):
        return token
    with suppress(TransactionIntegrityError):
        Token(chain=chain, address=address)
        commit()
        logger.debug('token %s added to ydb')
    return Token.get(chain=get_chain(sync=True), address=address)

@a_sync(default='async', executor=executor)
@db_session
def _get_token_symbol(address: str) -> Optional[str]:
    return get_token(address, sync=True).symbol

@a_sync(default='async', executor=executor)
@db_session
def _set_token_symbol(address: str, symbol: str) -> None:
    get_token(address, sync=True).symbol = symbol

@a_sync(default='async', executor=executor)
@db_session
def _get_token_name(address: str) -> Optional[str]:
    return get_token(address, sync=True).name

@a_sync(default='async', executor=executor)
@db_session
def _set_token_name(address: str, name: str) -> None:
    get_token(address, sync=True).name = name

@a_sync(default='async', executor=executor)
@db_session
def _get_token_decimals(address: str) -> Optional[int]:
    return get_token(address, sync=True).decimals

@a_sync(default='async', executor=executor)
@db_session
def _set_token_decimals(address: str, decimals: int) -> None:
    get_token(address, sync=True).decimals = decimals

@a_sync(default='async', executor=executor)
@db_session
def _get_token_bucket(address: str) -> Optional[str]:
    try:
        return get_token(address, sync=True).bucket
    except ValueError:
        return None

@a_sync(default='async', executor=executor)
@db_session
def _set_token_bucket(address: str, bucket: str) -> None:
    with suppress(ValueError):
        get_token(address, sync=True).bucket = bucket
