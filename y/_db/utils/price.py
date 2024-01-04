
import asyncio
from contextlib import suppress
from decimal import Decimal, InvalidOperation
from typing import List, Optional

from a_sync import a_sync
from brownie import chain
from pony.orm import db_session

from y import constants
from y._db.common import token_attr_threads
from y._db.entities import Price, insert, retry_locked
from y._db.utils.token import ensure_token
from y._db.utils.utils import ensure_block


@a_sync(default='async', executor=token_attr_threads)
@db_session
@retry_locked
def get_price(address: str, block: int) -> Optional[Decimal]:
    ensure_block(block, sync=True)
    ensure_token(address, sync=True)
    if address == constants.EEE_ADDRESS:
        address = constants.WRAPPED_GAS_COIN
    if price := Price.get(
        token = (chain.id, address), 
        block = (chain.id, block), 
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
    with suppress(InvalidOperation): # happens with really big numbers sometimes. nbd, we can just skip the cache in this case.
        ensure_block(block, sync=True)
        ensure_token(address, sync=True)
        if address == constants.EEE_ADDRESS:
            address = constants.WRAPPED_GAS_COIN
        insert(
            type = Price,
            block = (chain.id, block),
            token = (chain.id, address),
            price = Decimal(price),
        )
        
_tasks: List[asyncio.Task] = []
