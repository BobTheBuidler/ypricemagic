
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from a_sync import a_sync
from brownie import convert
from pony.orm import TransactionIntegrityError, commit, db_session

from y._db.config import connection_settings
from y._db.entities import Chain, Token, db
from y.constants import EEE_ADDRESS
from y.erc20 import decimals

logger = logging.getLogger(__name__)

db.bind(**connection_settings, create_db=True)

db.generate_mapping(create_tables=True)


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
    chain = Chain.get(id=chain.id)
    if chain is None:
        try:
            chain = Chain(id=chain.id)
            commit()
            logger.debug('chain %s added to ydb')
        except TransactionIntegrityError:
            chain = Chain.get(id=chain.id)
    return chain

@a_sync(default='async', executor=executor)
@db_session
def get_token(address: str) -> Token:
    address = convert.to_address(address)
    if address == EEE_ADDRESS:
        raise ValueError(f"cannot create token entity for {EEE_ADDRESS}")
    chain = get_chain(sync=True)
    token = Token.get(chain=chain, address=address)
    if token is None:
        try:
            token = Token(chain=chain, address=address)
            commit()
            logger.debug('token %s added to ydb')
        except TransactionIntegrityError:
            token = Token.get(chain=chain, address=address)
    return token

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
    return get_token(address, sync=True).bucket

@a_sync(default='async', executor=executor)
@db_session
def _set_token_bucket(address: str, bucket: str) -> None:
    get_token(address, sync=True).bucket = bucket
