
import asyncio
import logging
from contextlib import suppress
from decimal import Decimal, InvalidOperation
from typing import List, Optional

from brownie import chain

from y import constants
from y._db.entities import Price, insert
from y._db.utils.decorators import a_sync_db_session
from y._db.utils.token import ensure_token
from y._db.utils.utils import ensure_block


logger = logging.getLogger(__name__)

@a_sync_db_session
def get_price(address: str, block: int) -> Optional[Decimal]:
    ensure_block(block, sync=True)
    ensure_token(address)
    if address == constants.EEE_ADDRESS:
        address = constants.WRAPPED_GAS_COIN
    if price := Price.get(token = (chain.id, address), block = (chain.id, block)) and (price:=price.price):
        logger.debug("found %s block %s price %s in ydb", address, block, price)
        return price

async def set_price(address: str, block: int, price: Decimal) -> None:
    _tasks.append(asyncio.create_task(coro=_set_price(address, block, price), name=f"set_price {price} for {address} at {block}"))
    for t in _tasks[:]:
        if t.done():
            await t
            _tasks.remove(t)

@a_sync_db_session
def _set_price(address: str, block: int, price: Decimal) -> None:
    with suppress(InvalidOperation): # happens with really big numbers sometimes. nbd, we can just skip the cache in this case.
        ensure_block(block, sync=True)
        ensure_token(address)
        if address == constants.EEE_ADDRESS:
            address = constants.WRAPPED_GAS_COIN
        insert(
            type = Price,
            block = (chain.id, block),
            token = (chain.id, address),
            price = Decimal(price),
        )
        logger.debug("inserted %s block %s price to ydb: %s", address, block, price)
        
_tasks: List[asyncio.Task] = []
