
import logging
from contextlib import suppress
from decimal import Decimal, InvalidOperation
from typing import Dict, Optional

import a_sync
from brownie import chain
from cachetools.func import ttl_cache
from pony.orm import select

from y import constants
from y._db.decorators import a_sync_read_db_session, a_sync_write_db_session, log_result_count
from y._db.entities import Price, insert
from y._db.utils.token import ensure_token
from y._db.utils.utils import ensure_block
from y.datatypes import Address


logger = logging.getLogger(__name__)

@a_sync_read_db_session
def get_price(address: str, block: int) -> Optional[Decimal]:
    if address == constants.EEE_ADDRESS:
        address = constants.WRAPPED_GAS_COIN
    if price := known_prices_at_block(block).get(address):
        logger.debug("found %s block %s price %s in ydb", address, block, price)
        return price
    if (price := Price.get(token = (chain.id, address), block = (chain.id, block))) and (price:=price.price):
        logger.debug("found %s block %s price %s in ydb", address, block, price)
        return price

def set_price(address: str, block: int, price: Decimal) -> None:
    a_sync.create_task(
        coro=_set_price(address, block, price), 
        name=f"set_price {price} for {address} at {block}", 
        skip_gc_until_done=True,
    )

@a_sync_write_db_session
def _set_price(address: str, block: int, price: Decimal) -> None:
    with suppress(InvalidOperation): # happens with really big numbers sometimes. nbd, we can just skip the cache in this case.
        ensure_block(block, sync=True)
        if address == constants.EEE_ADDRESS:
            address = constants.WRAPPED_GAS_COIN
        ensure_token(address)
        insert(
            type = Price,
            block = (chain.id, block),
            token = (chain.id, address),
            price = Decimal(price),
        )
        logger.debug("inserted %s block %s price to ydb: %s", address, block, price)

@ttl_cache(maxsize=1_000, ttl=5*60)
@log_result_count("prices", ["block"])
def known_prices_at_block(number: int) -> Dict[Address, Decimal]:
    """cache and return all known prices at block `number` to minimize db reads"""
    return dict(select((p.token.address, p.price) for p in Price if p.block.chain.id == chain.id and p.block.number == number))