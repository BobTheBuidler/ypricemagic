import logging
import threading
from decimal import Decimal, InvalidOperation
from typing import Dict, Optional

from a_sync import ProcessingQueue
from cachetools import TTLCache, cached
from eth_typing import BlockNumber, ChecksumAddress
from pony.orm import select

from y import constants
from y._db.decorators import a_sync_read_db_session, log_result_count, retry_locked
from y._db.entities import Price, insert_nowait
from y._db.utils.token import ensure_token
from y._db.utils.utils import ensure_block
from y.constants import CHAINID


logger = logging.getLogger(__name__)
_logger_debug = logger.debug


@a_sync_read_db_session
def get_price(address: ChecksumAddress, block: BlockNumber) -> Optional[Decimal]:
    """
    Retrieve the price of a token at a specific block.

    This function checks if the price of a token at a given block is already known
    and returns it if available. It first checks a cache of known prices and then
    queries the database if necessary. If the price is not found, it implicitly returns None.

    Args:
        address: The address of the token.
        block: The block number.

    Examples:
        >>> price = get_price("0xTokenAddress", 12345678)
        >>> print(price)
        123.45

    See Also:
        - :func:`known_prices_at_block`
        - :class:`~y._db.entities.Price`
    """
    if address == constants.EEE_ADDRESS:
        address = constants.WRAPPED_GAS_COIN
    if price := known_prices_at_block(block).pop(address, None):
        _logger_debug("found %s block %s price %s in ydb", address, block, price)
        return price
    if (price := Price.get(token=(CHAINID, address), block=(CHAINID, block))) and (
        price := price.price
    ):
        _logger_debug("found %s block %s price %s in ydb", address, block, price)
        return price


@retry_locked
async def _set_price(
    address: ChecksumAddress, block: BlockNumber, price: Decimal
) -> None:
    """
    Set the price of a token at a specific block in the database.

    This function ensures the block and token are present in the database and
    inserts the price information. It handles large numbers by suppressing
    `InvalidOperation` exceptions.

    Args:
        address: The address of the token.
        block: The block number.
        price: The price of the token.

    Examples:
        >>> await _set_price("0xTokenAddress", 12345678, Decimal("123.45"))

    See Also:
        - :func:`ensure_block`
        - :func:`ensure_token`
        - :func:`insert`
    """
    await ensure_block(block, sync=False)
    if address == constants.EEE_ADDRESS:
        address = constants.WRAPPED_GAS_COIN
    await ensure_token(str(address), sync=False)  # force to string for cache key
    try:
        insert_nowait(
            type=Price,
            block=(CHAINID, block),
            token=(CHAINID, address),
            price=Decimal(price),
        )
        _logger_debug(
            "queued insert %s block %s price to ydb: %s", address, block, price
        )
    except InvalidOperation:
        # happens with really big numbers sometimes. nbd, we can just skip the cache in this case.
        pass


def set_price(address: ChecksumAddress, block: BlockNumber, price: Decimal) -> None:
    """
    Set the price of a token at a specific block in the database.

    This function ensures the block and token are present in the database and
    inserts the price information. It handles large numbers by suppressing
    `InvalidOperation` exceptions.

    This function delegates to a threadpool without waiting for the job to complete.

    Args:
        address: The address of the token.
        block: The block number.
        price: The price of the token.

    Examples:
        >>> await _set_price("0xTokenAddress", 12345678, Decimal("123.45"))

    See Also:
        - :func:`ensure_block`
        - :func:`ensure_token`
        - :func:`insert`
    """


set_price = ProcessingQueue(_set_price, num_workers=50, return_data=False)


@cached(TTLCache(maxsize=1_000, ttl=5 * 60), lock=threading.Lock())
@log_result_count("prices", ("block",))
def known_prices_at_block(number: BlockNumber) -> Dict[ChecksumAddress, Decimal]:
    """
    Cache and return all known prices at a specific block to minimize database reads.

    This function retrieves all known token prices at a given block from the database
    and caches them to reduce the number of database reads in future queries. It also
    logs the number of results found.

    Args:
        number: The block number.

    Returns:
        A dictionary mapping token addresses to their prices at the specified block.

    Examples:
        >>> prices = known_prices_at_block(12345678)
        >>> print(prices)
        {'0xTokenAddress': Decimal('123.45'), '0xAnotherToken': Decimal('67.89')}

    See Also:
        - :func:`get_price`
        - :class:`~y._db.entities.Price`
    """
    return dict(
        select(
            (p.token.address, p.price)
            for p in Price
            if p.block.chain.id == CHAINID and p.block.number == number
        )
    )
