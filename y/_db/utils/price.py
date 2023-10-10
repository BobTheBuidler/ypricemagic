
import asyncio
from decimal import Decimal
from typing import List, Optional

from a_sync import a_sync
from pony.orm import TransactionIntegrityError, commit, db_session

from y import constants
from y._db.common import token_attr_threads
from y._db.entities import Price, retry_locked, insert
from y._db.utils._ep import _get_get_block, _get_get_token


@a_sync(default='async', executor=token_attr_threads)
@db_session
@retry_locked
def get_price(address: str, block: int) -> Optional[Decimal]:
    get_block = _get_get_block()
    get_token = _get_get_token()
    if address == constants.EEE_ADDRESS:
        address = constants.WRAPPED_GAS_COIN
    if price := Price.get(
        token = get_token(address, sync=True), 
        block = get_block(block, sync=True), 
    ):
        return price.price

async def set_price(address: str, block: int, price: Decimal) -> None:
    _tasks.append(asyncio.create_task(coro=_set_price(address, block, price), name=f"set_price {price} for {address} at {block}"))
    for t in _tasks[:]:
        if t.done():
            await t
            _tasks.remove(t)

@a_sync(default='async', executor=token_attr_threads)
@db_session
@retry_locked
def _set_price(address: str, block: int, price: Decimal) -> None:
    get_block = _get_get_block()
    get_token = _get_get_token()
    if address == constants.EEE_ADDRESS:
        address = constants.WRAPPED_GAS_COIN
    insert(
        type = Price,
        block = get_block(block, sync=True),
        token = get_token(address, sync=True),
        price = Decimal(price),
    )
    
_tasks: List[asyncio.Task] = []
