
import asyncio
from decimal import Decimal
from typing import List, Optional

from a_sync import a_sync
from pony.orm import TransactionIntegrityError, commit, db_session

from y import constants
from y._db.common import executor
from y._db.entities import Price, retry_locked
from y._db.utils.token import get_token
from y._db.utils.utils import get_block


@a_sync(default='async', executor=executor)
@db_session
@retry_locked
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
@retry_locked
def _set_price(address: str, block: int, price: Decimal) -> None:
    if address == constants.EEE_ADDRESS:
        address = constants.WRAPPED_GAS_COIN
    try:
        Price(
            block = get_block(block, sync=True),
            token = get_token(address, sync=True),
            price = Decimal(price),
        )
        commit()
    except TransactionIntegrityError:
        assert (p := Price.get(
            block = get_block(block, sync=True),
            token = get_token(address, sync=True),
        )) and p.price == Decimal(price), (p.price, price)

__tasks: List[asyncio.Task] = []
