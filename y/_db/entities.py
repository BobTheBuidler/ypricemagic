import logging
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Callable, TypeVar
from typing import Optional as typing_Optional

from pony.orm import (
    Database,
    InterfaceError,
    Optional,
    PrimaryKey,
    Required,
    Set,
    TransactionIntegrityError,
    commit,
    composite_index,
    db_session,
)
from typing_extensions import ParamSpec

from y._db.decorators import retry_locked, ydb_write_threads

db = Database()

# makes type checking work, see below for info:
# https://pypi.org/project/pony-stubs/
DbEntity = db.Entity


logger = logging.getLogger(__name__)


class _AsyncEntityMixin:
    """Mixin class intended for future asynchronous operations.

    This class is currently not implemented. It is designed to provide
    asynchronous capabilities to database entities in the future.

    TODO: Implement asynchronous methods for database operations.

    Examples:
        Intended usage once implemented:
        >>> class MyEntity(DbEntity, _AsyncEntityMixin):
        ...     pass

    See Also:
        - :mod:`a_sync` for asynchronous programming utilities.

    @classmethod
    @a_sync('async')
    def get(cls: E, *args, **kwargs) -> E:
        return super(DbEntity).get(*args, **kwargs)
    @classmethod
    @a_sync('async')
    def select(cls: E, *args, **kwargs) -> E:
        return super(DbEntity).select(*args, **kwargs)
    """


class Chain(DbEntity, _AsyncEntityMixin):
    """Represents a blockchain chain entity in the database."""

    id = PrimaryKey(int)

    if TYPE_CHECKING:
        # if we execute this code we get `TypeError: 'type' object is not subscriptable`
        blocks: Set["Block"]
        addresses: Set["Address"]
        log_cached: Set["LogCacheInfo"]
        trace_caches: Set["TraceCacheInfo"]

    blocks = Set("Block")
    addresses = Set("Address")
    log_cached = Set("LogCacheInfo")
    trace_caches = Set("TraceCacheInfo")


class Block(DbEntity, _AsyncEntityMixin):
    """Represents a block entity in the database."""

    chain = Required(Chain, reverse="blocks")
    number = Required(int)
    PrimaryKey(chain, number)
    hash = Optional(int, lazy=True)
    timestamp = Optional(datetime, lazy=True)

    composite_index(chain, hash)

    if TYPE_CHECKING:
        # if we execute this code we get `TypeError: 'type' object is not subscriptable`
        prices: Set["Price"]
        contracts_deployed: Set["Contract"]
        logs: Set["Log"]
        traces: Set["Trace"]

    prices = Set("Price", reverse="block", cascade_delete=False)
    contracts_deployed = Set("Contract", reverse="deploy_block")
    logs = Set("Log", reverse="block", cascade_delete=False)
    traces = Set("Trace", reverse="block", cascade_delete=False)


class Address(DbEntity, _AsyncEntityMixin):
    """Represents an address entity in the database."""

    chain = Required(Chain, lazy=True, reverse="addresses")
    address = Required(str, 42, lazy=True)
    PrimaryKey(chain, address)
    notes = Optional(str, lazy=True)

    if TYPE_CHECKING:
        # if we execute this code we get `TypeError: 'type' object is not subscriptable`
        contracts_deployed: Set["Contract"]

    contracts_deployed = Set("Contract", reverse="deployer")


class Contract(Address):
    """Represents a contract entity in the database."""

    deployer = Optional(
        Address, reverse="contracts_deployed", lazy=True, cascade_delete=False
    )
    deploy_block = Optional(
        Block, reverse="contracts_deployed", lazy=True, cascade_delete=False
    )


class Token(Contract):
    """Represents a token entity in the database."""

    symbol = Optional(str, lazy=True)
    name = Optional(str, lazy=True)
    decimals = Optional(int, lazy=True)
    bucket = Optional(str, index=True, lazy=True)

    if TYPE_CHECKING:
        # if we execute this code we get `TypeError: 'type' object is not subscriptable`
        prices: Set["Price"]

    prices = Set("Price", reverse="token")


class Price(DbEntity):
    """Represents a price entity in the database."""

    block = Required(Block, index=True, lazy=True)
    token = Required(Token, index=True, lazy=True)
    PrimaryKey(block, token)
    price = Required(Decimal, 38, 18)


class TraceCacheInfo(DbEntity):
    """Represents trace cache information in the database."""

    chain = Required(Chain, index=True)
    to_addresses = Required(bytes, index=True)
    from_addresses = Required(bytes, index=True)
    PrimaryKey(chain, to_addresses, from_addresses)
    cached_from = Required(int)
    cached_thru = Required(int)


class LogCacheInfo(DbEntity):
    """Represents log cache information in the database."""

    chain = Required(Chain, index=True)
    address = Required(str, 42, index=True)
    topics = Required(bytes)
    PrimaryKey(chain, address, topics)
    cached_from = Required(int)
    cached_thru = Required(int)


class LogTopic(DbEntity):
    """Represents a log topic entity in the database.

    Just makes the :ref:`Log` db smaller.
    """

    dbid = PrimaryKey(int, size=64, auto=True)
    topic = Required(str, 64, unique=True, lazy=True)

    if TYPE_CHECKING:
        # if we execute this code we get `TypeError: 'type' object is not subscriptable`
        logs_as_topic0: Set["Log"]
        logs_as_topic1: Set["Log"]
        logs_as_topic2: Set["Log"]
        logs_as_topic3: Set["Log"]

    logs_as_topic0 = Set("Log", reverse="topic0")
    logs_as_topic1 = Set("Log", reverse="topic1")
    logs_as_topic2 = Set("Log", reverse="topic2")
    logs_as_topic3 = Set("Log", reverse="topic3")


class Hashes(DbEntity):
    """Represents a hash entity in the database.

    Just makes :ref:`Log` pk and indexes smaller.
    """

    dbid = PrimaryKey(int, size=64, auto=True)
    hash = Required(str, 64, unique=True)

    if TYPE_CHECKING:
        # if we execute this code we get `TypeError: 'type' object is not subscriptable`
        logs_for_tx: Set["Log"]
        logs_for_addr: Set["Log"]

    logs_for_tx = Set("Log", reverse="tx")
    logs_for_addr = Set("Log", reverse="address")


class Log(DbEntity):
    """Represents a log entity in the database."""

    block = Required(Block, index=True, lazy=True)
    tx = Required(Hashes, lazy=True)
    log_index = Required(int, size=16, lazy=True)
    PrimaryKey(block, tx, log_index)

    address = Required(Hashes, index=True, lazy=True)

    topic0 = Required(LogTopic, index=True, lazy=True)
    topic1 = Optional(LogTopic, index=True, lazy=True)
    topic2 = Optional(LogTopic, index=True, lazy=True)
    topic3 = Optional(LogTopic, index=True, lazy=True)
    composite_index(address, topic0)
    composite_index(topic0, topic1)
    composite_index(topic0, topic2)
    composite_index(topic0, topic3)
    composite_index(block, address, topic0)
    composite_index(block, topic0, topic1)
    composite_index(block, topic0, topic2)
    composite_index(block, topic0, topic3)
    composite_index(topic0, topic1, topic2, topic3)
    composite_index(block, topic0, topic1, topic2, topic3)
    raw = Required(bytes, lazy=True)


class Trace(DbEntity):
    """Represents a trace entity in the database."""

    id = PrimaryKey(int, auto=True)
    block = Required(Block, index=True, lazy=True)
    hash = Required(str, 64, index=True, lazy=True)
    from_address = Required(str, 42, index=True, lazy=True)
    to_address = Required(str, 42, index=True, lazy=True)
    raw = Required(bytes)


class BlockAtTimestamp(DbEntity):
    """Represents a block at a specific timestamp in the database."""

    chainid = Required(int)
    timestamp = Required(datetime)
    PrimaryKey(chainid, timestamp)
    block = Required(int)


__write_threads_submit = ydb_write_threads.submit


def insert_nowait(type: DbEntity, **kwargs: Any) -> typing_Optional[DbEntity]:
    # sourcery skip: simplify-boolean-comparison
    __write_threads_submit(exc_wrapper, insert, type, **kwargs, fire_and_forget=True)


__P = ParamSpec("__P")
__T = TypeVar("__T")


def exc_wrapper(
    func: Callable[__P, __T], *args: __P.args, **kwargs: __P.kwargs
) -> typing_Optional[DbEntity]:
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.exception(e)


@db_session
@retry_locked
def insert(type: DbEntity, **kwargs: Any) -> typing_Optional[DbEntity]:
    """Inserts a new entity into the database with retry logic.

    This function attempts to insert a new entity of the specified type into the database.
    It includes retry logic to handle specific database exceptions.

    Args:
        type: The type of the entity to insert.
        **kwargs: The attributes of the entity to insert.

    Examples:
        >>> new_block = insert(Block, chain=chain_instance, number=123456)
        >>> new_token = insert(Token, symbol="ETH", name="Ethereum")

    See Also:
        - :func:`pony.orm.commit`
        - :func:`pony.orm.db_session`
        - :func:`retry_locked`
    """
    try:
        while True:
            try:
                entity = type(**kwargs)
                commit()
                logger.debug("inserted %s to db", entity)
                return entity
            except InterfaceError as e:
                logger.debug("%s while inserting %s", e, type.__name__)
    except TransactionIntegrityError as e:
        constraint_errs = (
            "UNIQUE constraint failed",
            "duplicate key value violates unique constraint",
        )
        if any(map((msg := str(e)).__contains__, constraint_errs)):
            logger.debug("%s: %s %s", msg, type.__name__, kwargs)
        else:
            logger.debug(
                "%s %s when inserting %s",
                e.__class__.__name__,
                str(e),
                e,
                type.__name__,
            )
            raise
