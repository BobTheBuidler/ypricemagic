
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from contextlib import suppress
from decimal import Decimal
from typing import List, Optional

from a_sync import a_sync
from brownie import chain, convert
from pony.orm import (BindingError, TransactionError,
                      TransactionIntegrityError, commit, db_session)

from y import constants
from y._db.config import connection_settings
from y._db.entities import Address, Block, Chain, Price, Token, db
from y.erc20 import decimals

logger = logging.getLogger(__name__)

try:
    db.bind(**connection_settings, create_db=True)
    db.generate_mapping(create_tables=True)
except TransactionError as e:
    if str(e) != "@db_session-decorated create_tables() function with `ddl` option cannot be called inside of another db_session":
        raise e
except BindingError as e:
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
    return Block.get(chain=chain, number=number)

@a_sync(default='async', executor=executor)
@db_session
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
        with suppress(TransactionIntegrityError):
            Token(chain=get_chain(sync=True), address=address)
            commit()
            logger.debug('token %s added to ydb', address)
        if token := Token.get(chain=get_chain(sync=True), address=address):
            return token

@a_sync(default='async', executor=executor)
@db_session
def get_price(address: str, block: int) -> Optional[Decimal]:
    if address == constants.EEE_ADDRESS:
        address = constants.WRAPPED_GAS_COIN
    if price := Price.get(
        token = get_token(address, sync=True), 
        block = get_block(block, sync=True), 
    ):
        return price.price

async def set_price(address: str, block: int, price: Decimal) -> None:
    __tasks.append(asyncio.create_task(_set_price(address, block, price)))
    for t in __tasks[:]:
        if t.done():
            await t
            __tasks.remove(t)

@a_sync(default='async', executor=executor)
@db_session
def _set_price(address: str, block: int, price: Decimal) -> None:
    Price(
        block = get_block(block, sync=True),
        token = get_token(address, sync=True),
        price = price,
    )
    commit()

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
    if address == constants.EEE_ADDRESS:
        return
    return get_token(address, sync=True).bucket

@a_sync(default='async', executor=executor)
@db_session
def _set_token_bucket(address: str, bucket: str) -> None:
    if address == constants.EEE_ADDRESS:
        return
    get_token(address, sync=True).bucket = bucket

__tasks: List[asyncio.Task] = []