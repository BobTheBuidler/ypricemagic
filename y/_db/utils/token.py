import logging
import threading
from functools import lru_cache
from typing import Dict, Optional, Set

import a_sync
from a_sync import PruningThreadPoolExecutor
from cachetools import TTLCache, cached
from pony.orm import commit, db_session, select

from y import constants, convert
from y._db.decorators import (
    a_sync_read_db_session,
    db_session_retry_locked,
    log_result_count,
)
from y._db.entities import Address, Token, insert
from y._db.exceptions import EEEError
from y._db.utils._ep import _get_get_token
from y.constants import CHAINID
from y.datatypes import AnyAddressType
from y.utils import _erc20

logger = logging.getLogger(__name__)
_logger_debug = logger.debug


_token_executor = PruningThreadPoolExecutor(10, "ypricemagic db executor [token]")


@a_sync.a_sync(default="async", executor=_token_executor)
@db_session_retry_locked
def get_token(address: str) -> Token:
    """Retrieve or insert a token entity for a given address.

    This function attempts to retrieve a token entity from the database
    for the specified address. If the address corresponds to the EEE address,
    an `EEEError` is raised. If the address is not found, a new token entity
    is inserted into the database.

    Args:
        address: The address of the token to retrieve or insert.

    Raises:
        EEEError: If the address is the EEE address.

    Returns:
        The token entity associated with the given address.

    Examples:
        >>> token = get_token("0x1234567890abcdef1234567890abcdef12345678")
        >>> print(token)

    See Also:
        - :class:`~y._db.entities.Token`
        - :func:`~y.convert.to_address`
    """
    address = convert.to_address(address)
    if address == constants.EEE_ADDRESS:
        raise EEEError(f"cannot create token entity for {constants.EEE_ADDRESS}")
    while True:
        if entity := Address.get(chain=CHAINID, address=address):
            if isinstance(entity, Token):
                return entity
            entity.delete()
            commit()
        return insert(type=Token, chain=CHAINID, address=address) or Token.get(
            chain=CHAINID, address=address
        )


@a_sync.a_sync(default="sync", ram_cache_maxsize=None)
def ensure_token(address: AnyAddressType) -> None:
    """Ensure a token entity exists for a given address.

    This function ensures that a token entity exists in the database for the
    specified address. If the token is not already known, it is retrieved
    and inserted into the database.

    Args:
        address: The address of the token to ensure.

    Examples:
        >>> ensure_token("0x1234567890abcdef1234567890abcdef12345678")
    """
    return _ensure_token(str(address))  # force to string for cache key


@lru_cache(maxsize=None)
@db_session_retry_locked
def _ensure_token(address: str) -> None:
    """Helper function to ensure a token entity exists.

    This function is a helper to `ensure_token` and cannot be wrapped with
    `a_sync` directly. It checks if the token is known and retrieves it if not.

    Args:
        address: The address of the token to ensure.

    See Also:
        - :func:`ensure_token`
    """
    if address not in known_tokens():
        get_token = _get_get_token()
        get_token(address, sync=True)


@a_sync_read_db_session
def get_bucket(address: str) -> Optional[str]:
    """Retrieve the bucket for a given token address.

    This function retrieves the bucket associated with a token address from
    the database. If the bucket is not known, it is retrieved and stored.

    Args:
        address: The address of the token to retrieve the bucket for.

    Returns:
        The bucket associated with the token address, if available.

    Examples:
        >>> bucket = get_bucket("0x1234567890abcdef1234567890abcdef12345678")
        >>> print(bucket)
    """
    if address == constants.EEE_ADDRESS:
        return
    if (bucket := known_buckets().pop(address, None)) is None:
        get_token = _get_get_token()
        bucket = get_token(address, sync=True).bucket
    if bucket:
        _logger_debug("found %s bucket %s in ydb", address, bucket)
    return bucket


@a_sync.a_sync(default="async", executor=_token_executor)
@db_session_retry_locked
def _set_bucket(address: str, bucket: str) -> None:
    """Set the bucket for a given token address.

    This function updates the bucket associated with a token address in the
    database.

    Args:
        address: The address of the token to set the bucket for.
        bucket: The bucket to associate with the token address.

    Examples:
        >>> _set_bucket("0x1234567890abcdef1234567890abcdef12345678", "bucket_name")
    """
    if address == constants.EEE_ADDRESS:
        return
    get_token = _get_get_token()
    get_token(address, sync=True).bucket = bucket
    _logger_debug("updated %s bucket in ydb: %s", address, bucket)


set_bucket = a_sync.ProcessingQueue(_set_bucket, num_workers=10, return_data=False)


@a_sync_read_db_session
def get_symbol(address: str) -> Optional[str]:
    """Retrieve the symbol for a given token address.

    This function retrieves the symbol associated with a token address from
    the database. If the symbol is not known, it is retrieved and stored.

    Args:
        address: The address of the token to retrieve the symbol for.

    Returns:
        The symbol associated with the token address, if available.

    Examples:
        >>> symbol = get_symbol("0x1234567890abcdef1234567890abcdef12345678")
        >>> print(symbol)
    """
    if (symbol := known_symbols().pop(address, None)) is None:
        get_token = _get_get_token()
        symbol = get_token(address, sync=True).symbol
    if symbol:
        _logger_debug("found %s symbol %s in ydb", address, symbol)
    return symbol


def set_symbol(address: str, symbol: str):
    """Set the symbol for a given token address.

    This function updates the symbol associated with a token address in the
    database.

    Args:
        address: The address of the token to set the symbol for.
        symbol: The symbol to associate with the token address.

    Raises:
        ValueError: If `symbol` is not provided.
        TypeError: If `symbol` is not a string.

    Examples:
        >>> set_symbol("0x1234567890abcdef1234567890abcdef12345678", "SYM")
    """
    if not symbol:
        raise ValueError("`symbol` is required")
    if not isinstance(symbol, str):
        raise TypeError(f"`symbol` must be a string. You passed {symbol}")
    a_sync.create_task(
        coro=_set_symbol(address, symbol),
        name=f"set_symbol {symbol} for {address}",
        skip_gc_until_done=True,
    )


@a_sync_read_db_session
def get_name(address: str) -> Optional[str]:
    """Retrieve the name for a given token address.

    This function retrieves the name associated with a token address from
    the database. If the name is not known, it is retrieved and stored.

    Args:
        address: The address of the token to retrieve the name for.

    Returns:
        The name associated with the token address, if available.

    Examples:
        >>> name = get_name("0x1234567890abcdef1234567890abcdef12345678")
        >>> print(name)
    """
    if (name := known_names().pop(address, None)) is None:
        get_token = _get_get_token()
        name = get_token(address, sync=True).name
    if name:
        _logger_debug("found %s name %s in ydb", address, name)
    return name


def set_name(address: str, name: str) -> None:
    """Set the name for a given token address.

    This function updates the name associated with a token address in the
    database.

    Args:
        address: The address of the token to set the name for.
        name: The name to associate with the token address.

    Raises:
        ValueError: If `name` is not provided.
        TypeError: If `name` is not a string.

    Examples:
        >>> set_name("0x1234567890abcdef1234567890abcdef12345678", "Token Name")
    """
    if not name:
        raise ValueError("`name` is required")
    if not isinstance(name, str):
        raise TypeError(f"`name` must be a string. You passed {name}")
    a_sync.create_task(
        coro=_set_name(address, name),
        name=f"set_name {name} for {address}",
        skip_gc_until_done=True,
    )


async def get_decimals(address: str) -> int:
    """Retrieve the decimals for a given token address.

    This function retrieves the decimals associated with a token address from
    the database. If the decimals are not known, they are retrieved and stored.

    Args:
        address: The address of the token to retrieve the decimals for.

    Returns:
        The decimals associated with the token address.

    Raises:
        ValueError: If the decimals value is greater than the maximum allowed.

    Examples:
        >>> decimals = await get_decimals("0x1234567890abcdef1234567890abcdef12345678")
        >>> print(decimals)
    """
    d = await _get_token_decimals(address)
    if d is None:
        d = await _erc20.decimals(address, sync=False)
        if d:
            if d > 2147483647:
                # raise this here so the task doesnt break
                # TODO debug where this comes from
                raise ValueError(
                    f"Value {d} of attr Token.decimals is greater than the maximum allowed value 2147483647"
                )
            a_sync.create_task(
                coro=set_decimals(address, d),
                name=f"set_decimals {address}",
                skip_gc_until_done=True,
            )
    return d


@a_sync.a_sync(default="async", executor=_token_executor)
@db_session_retry_locked
def set_decimals(address: str, decimals: int) -> None:
    """Set the decimals for a given token address.

    This function updates the decimals associated with a token address in the
    database.

    Args:
        address: The address of the token to set the decimals for.
        decimals: The decimals to associate with the token address.

    Examples:
        >>> set_decimals("0x1234567890abcdef1234567890abcdef12345678", 18)
    """
    get_token = _get_get_token()
    get_token(address, sync=True).decimals = decimals
    _logger_debug("updated %s decimals in ydb: %s", address, decimals)


@a_sync.a_sync(default="async", executor=_token_executor)
@db_session_retry_locked
def _set_symbol(address: str, symbol: str) -> None:
    """Set the symbol for a given token address.

    This function updates the symbol associated with a token address in the
    database.

    Args:
        address: The address of the token to set the symbol for.
        symbol: The symbol to associate with the token address.

    Examples:
        >>> _set_symbol("0x1234567890abcdef1234567890abcdef12345678", "SYM")
    """
    get_token = _get_get_token()
    get_token(address, sync=True).symbol = symbol
    _logger_debug("updated %s symbol in ydb: %s", address, symbol)


@a_sync.a_sync(default="async", executor=_token_executor)
@db_session_retry_locked
def _set_name(address: str, name: str) -> None:
    """Set the name for a given token address.

    This function updates the name associated with a token address in the
    database.

    Args:
        address: The address of the token to set the name for.
        name: The name to associate with the token address.

    Examples:
        >>> _set_name("0x1234567890abcdef1234567890abcdef12345678", "Token Name")
    """
    get_token = _get_get_token()
    get_token(address, sync=True).name = name
    _logger_debug("updated %s name in ydb: %s", address, name)


@a_sync_read_db_session
def _get_token_decimals(address: str) -> Optional[int]:
    """Retrieve the decimals for a given token address.

    This function retrieves the decimals associated with a token address from
    the database. If the decimals are not known, they are retrieved and stored.

    Args:
        address: The address of the token to retrieve the decimals for.

    Returns:
        The decimals associated with the token address, if available.

    Examples:
        >>> decimals = _get_token_decimals("0x1234567890abcdef1234567890abcdef12345678")
        >>> print(decimals)
    """
    if (decimals := known_decimals().pop(address, None)) is None:
        get_token = _get_get_token()
        decimals = get_token(address, sync=True).decimals
    if decimals:
        _logger_debug("found %s decimals %s in ydb", address, decimals)
        return decimals


# startup caches


@cached(TTLCache(maxsize=1, ttl=60 * 60), lock=threading.Lock())
@db_session_retry_locked
@log_result_count("tokens")
def known_tokens() -> Set[str]:
    """Cache and return all known tokens for this chain.

    This function caches and returns all known tokens for the current chain
    to minimize database reads.

    Returns:
        A set of known token addresses for the current chain.

    Examples:
        >>> tokens = known_tokens()
        >>> print(tokens)
    """
    return set(select(t.address for t in Token if t.chain.id == CHAINID))


@cached(TTLCache(maxsize=1, ttl=60 * 60), lock=threading.Lock())
@log_result_count("buckets")
def known_buckets() -> Dict[str, str]:
    """Cache and return all known token buckets for this chain.

    This function caches and returns all known token buckets for the current
    chain to minimize database reads.

    Returns:
        A dictionary mapping token addresses to their buckets for the current chain.

    Examples:
        >>> buckets = known_buckets()
        >>> print(buckets)
    """
    return dict(
        select(
            (t.address, t.bucket) for t in Token if t.chain.id == CHAINID and t.bucket
        )
    )


@cached(TTLCache(maxsize=1, ttl=60 * 60), lock=threading.Lock())
@log_result_count("token decimals")
def known_decimals() -> Dict[Address, int]:
    """Cache and return all known token decimals for this chain.

    This function caches and returns all known token decimals for the current
    chain to minimize database reads.

    Returns:
        A dictionary mapping token addresses to their decimals for the current chain.

    Examples:
        >>> decimals = known_decimals()
        >>> print(decimals)
    """
    return dict(
        select(
            (t.address, t.decimals)
            for t in Token
            if t.chain.id == CHAINID and t.decimals
        )
    )


@cached(TTLCache(maxsize=1, ttl=60 * 60), lock=threading.Lock())
@log_result_count("token symbols")
def known_symbols() -> Dict[Address, str]:
    """Cache and return all known token symbols for this chain.

    This function caches and returns all known token symbols for the current
    chain to minimize database reads.

    Returns:
        A dictionary mapping token addresses to their symbols for the current chain.

    Examples:
        >>> symbols = known_symbols()
        >>> print(symbols)
    """
    return dict(
        select(
            (t.address, t.symbol) for t in Token if t.chain.id == CHAINID and t.symbol
        )
    )


@cached(TTLCache(maxsize=1, ttl=60 * 60), lock=threading.Lock())
@log_result_count("token names")
def known_names() -> Dict[Address, str]:
    """Cache and return all known token names for this chain.

    This function caches and returns all known token names for the current
    chain to minimize database reads.

    Returns:
        A dictionary mapping token addresses to their names for the current chain.

    Examples:
        >>> names = known_names()
        >>> print(names)
    """
    return dict(
        select((t.address, t.name) for t in Token if t.chain.id == CHAINID and t.name)
    )
