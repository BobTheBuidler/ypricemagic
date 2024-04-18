
import logging
import threading
from contextlib import suppress
from decimal import Decimal, InvalidOperation
from typing import Dict, Optional

import a_sync
from brownie import chain
from cachetools import TTLCache, cached
from pony.orm import select

from y import constants
from y._db.decorators import a_sync_read_db_session, log_result_count, retry_locked
from y._db.entities import Price, insert
from y._db.utils.token import ensure_token
from y._db.utils.utils import ensure_block
from y.datatypes import Address


logger = logging.getLogger(__name__)

@a_sync_read_db_session
def get_price(address: str, block: int) -> Optional[Decimal]:
    if address == constants.EEE_ADDRESS:
        address = constants.WRAPPED_GAS_COIN
    if price := known_prices_at_block(block).pop(address, None):
        logger.debug("found %s block %s price %s in ydb", address, block, price)
        return price
    if (price := Price.get(token = (chain.id, address), block = (chain.id, block))) and (price:=price.price):
        logger.debug("found %s block %s price %s in ydb", address, block, price)
        return price

@retry_locked
async def _set_price(address: str, block: int, price: Decimal) -> None:
    await ensure_block(block, sync=False)
    if address == constants.EEE_ADDRESS:
        address = constants.WRAPPED_GAS_COIN
    await ensure_token(address, sync=False)
    with suppress(InvalidOperation): # happens with really big numbers sometimes. nbd, we can just skip the cache in this case.
        await insert(
            type = Price,
            block = (chain.id, block),
            token = (chain.id, address),
            price = Decimal(price),
            sync = False,
        )
        logger.debug("inserted %s block %s price to ydb: %s", address, block, price)

set_price = a_sync.ProcessingQueue(_set_price, num_workers=50, return_data=False)

@cached(TTLCache(maxsize=1_000, ttl=5*60), lock=threading.Lock())
@log_result_count("prices", ["block"])
def known_prices_at_block(number: int) -> Dict[Address, Decimal]:
    """cache and return all known prices at block `number` to minimize db reads"""
    return dict(select((p.token.address, p.price) for p in Price if p.block.chain.id == chain.id and p.block.number == number))