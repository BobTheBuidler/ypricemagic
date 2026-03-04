"""Utilities for purging cached prices from the ypricemagic database.

These functions delete Price rows from the local Pony ORM cache database and
invalidate the in-memory ``known_prices_at_block`` cache so subsequent reads
re-fetch from the network.

.. warning::
    Because :func:`~y._db.utils.price.set_price` is backed by an
    :class:`~a_sync.ProcessingQueue`, writes that are already queued but not yet
    flushed may re-insert recently purged data.  Call these helpers only when the
    price pipeline is idle, or accept that a small number of rows may reappear.
"""

import logging
from datetime import datetime

from eth_typing import BlockNumber, ChecksumAddress
from pony.orm import commit, db_session, delete, select

from y import constants
from y._db.decorators import retry_locked
from y._db.entities import Price
from y.constants import CHAINID

logger = logging.getLogger(__name__)


@db_session  # type: ignore[untyped-decorator]
@retry_locked
def purge_prices_by_token(address: ChecksumAddress) -> int:
    """Delete all cached prices for *address* on the current chain.

    If *address* is :data:`~y.constants.EEE_ADDRESS` it is transparently
    mapped to :data:`~y.constants.WRAPPED_GAS_COIN`, mirroring the behaviour
    of :func:`~y._db.utils.price.get_price` and
    :func:`~y._db.utils.price._set_price`.

    Returns the number of deleted rows, or ``0`` when the token does not
    exist in the database.

    .. note::
        Pending :class:`~a_sync.ProcessingQueue` ``set_price`` writes may
        re-insert recently purged data.  Call this when the price pipeline
        is idle or accept that a small number of rows may reappear.

    Args:
        address: The checksum address of the token whose prices should be
            removed.

    Returns:
        The count of deleted :class:`~y._db.entities.Price` rows.

    Examples:
        >>> purge_prices_by_token("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")
        42
    """
    if address == constants.EEE_ADDRESS:
        address = constants.WRAPPED_GAS_COIN

    count: int = delete(p for p in Price if p.token.chain.id == CHAINID and p.token.address == address)  # type: ignore[attr-defined]
    commit()

    if count:
        _clear_known_prices_cache()
        logger.debug("purged %s price rows for token %s on chain %s", count, address, CHAINID)

    return count


@db_session  # type: ignore[untyped-decorator]
@retry_locked
def purge_prices_by_block_range(start_block: BlockNumber, end_block: BlockNumber) -> int:
    """Delete all cached prices in the block range ``[start_block, end_block]``.

    Both bounds are **inclusive**.  Passing ``start_block == end_block``
    deletes prices at that single block.

    Raises :class:`ValueError` when ``start_block > end_block``.

    .. note::
        Pending :class:`~a_sync.ProcessingQueue` ``set_price`` writes may
        re-insert recently purged data.  Call this when the price pipeline
        is idle or accept that a small number of rows may reappear.

    Args:
        start_block: The lower bound block number (inclusive).
        end_block: The upper bound block number (inclusive).

    Returns:
        The count of deleted :class:`~y._db.entities.Price` rows.

    Raises:
        ValueError: If *start_block* is greater than *end_block*.

    Examples:
        >>> purge_prices_by_block_range(15_000_000, 15_100_000)
        137
    """
    if start_block > end_block:
        raise ValueError(f"start_block ({start_block}) must be <= end_block ({end_block})")

    count: int = delete(
        p
        for p in Price  # type: ignore[attr-defined]
        if p.block.chain.id == CHAINID
        and p.block.number >= start_block
        and p.block.number <= end_block
    )
    commit()

    if count:
        _clear_known_prices_cache()
        logger.debug(
            "purged %s price rows for blocks %s–%s on chain %s",
            count,
            start_block,
            end_block,
            CHAINID,
        )

    return count


@db_session  # type: ignore[untyped-decorator]
@retry_locked
def purge_prices_by_date_range(start_date: datetime, end_date: datetime) -> int:
    """Delete all cached prices whose block timestamp falls within
    ``[start_date, end_date]``.

    Both bounds are **inclusive**.  Blocks with a ``NULL`` timestamp are
    silently skipped (never deleted).

    Raises :class:`ValueError` when ``start_date > end_date``.

    .. note::
        Pending :class:`~a_sync.ProcessingQueue` ``set_price`` writes may
        re-insert recently purged data.  Call this when the price pipeline
        is idle or accept that a small number of rows may reappear.

    Args:
        start_date: The lower bound datetime (inclusive).
        end_date: The upper bound datetime (inclusive).

    Returns:
        The count of deleted :class:`~y._db.entities.Price` rows.

    Raises:
        ValueError: If *start_date* is greater than *end_date*.

    Examples:
        >>> from datetime import datetime
        >>> purge_prices_by_date_range(
        ...     datetime(2023, 1, 1), datetime(2023, 6, 30)
        ... )
        256
    """
    if start_date > end_date:
        raise ValueError(f"start_date ({start_date}) must be <= end_date ({end_date})")

    count: int = delete(
        p
        for p in Price  # type: ignore[attr-defined]
        if p.block.chain.id == CHAINID
        and p.block.timestamp is not None
        and p.block.timestamp >= start_date
        and p.block.timestamp <= end_date
    )
    commit()

    if count:
        _clear_known_prices_cache()
        logger.debug(
            "purged %s price rows for dates %s–%s on chain %s",
            count,
            start_date,
            end_date,
            CHAINID,
        )

    return count


def _clear_known_prices_cache() -> None:
    """Invalidate the in-memory ``known_prices_at_block`` cache.

    Imported lazily to avoid circular-import issues at module level.
    """
    from y._db.utils.price import known_prices_at_block

    known_prices_at_block.cache.clear()  # type: ignore[attr-defined]
