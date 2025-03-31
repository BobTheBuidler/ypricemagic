import itertools
import logging
from typing import List, Optional

from a_sync import a_sync, cgather, igather
from a_sync.executor import AsyncExecutor
from async_lru import alru_cache
from brownie.network.event import _EventItem
from eth_typing import HexStr
from eth_utils.toolz import concat
from evmspec.data import Address, HexBytes32, uint
from evmspec.structs.log import Topic
from hexbytes import HexBytes
from msgspec import json, ValidationError
from pony.orm import commit, db_session, select
from pony.orm.core import Query

from y import convert
from y._db.common import DiskCache, default_filter_threads, enc_hook, make_executor
from y._db.decorators import db_session_cached, db_session_retry_locked, retry_locked
from y._db.entities import Block, Hashes, LogCacheInfo, LogTopic
from y._db.entities import Log as DbLog
from y._db.log import Log
from y._db.utils._ep import _get_get_block
from y._db.utils.bulk import insert as _bulk_insert
from y.constants import CHAINID

logger = logging.getLogger(__name__)

LOG_COLS = (
    "block_chain",
    "block_number",
    "tx",
    "log_index",
    "address",
    "topic0",
    "topic1",
    "topic2",
    "topic3",
    "raw",
)

_BLOCK_COLS = "chain", "number"
_BLOCK_COLS_EXTENDED = "chain", "number", "classtype"

_topic_executor = make_executor(4, 8, "ypricemagic db executor [topic]")
_hash_executor = make_executor(4, 8, "ypricemagic db executor [hash]")

_get_log_cache_info = LogCacheInfo.get
_get_log_topic = LogTopic.get
_get_hash = Hashes.get


async def _prepare_log(log: Log) -> tuple:
    """
    Prepare a log for insertion into the database.

    This function gathers database IDs for the transaction hash, address, and topics
    of a given log. It then encodes the log as JSON using the `enc_hook` for special types.

    Args:
        log: The log entry to prepare.

    Returns:
        A tuple containing the prepared log parameters.

    Examples:
        >>> log = Log(transactionHash=HexBytes('0x1234'), address='0x...', topics=['0x...'], blockNumber=123, logIndex=0)
        >>> prepared_log = await _prepare_log(log)
        >>> print(prepared_log)

    See Also:
        - :func:`get_hash_dbid`
        - :func:`get_topic_dbid`
        - :func:`enc_hook`
    """
    transaction_dbid, address_dbid, topic_dbids = await cgather(
        get_hash_dbid(log.transactionHash.hex()),
        get_hash_dbid(log.address),
        igather(map(get_topic_dbid, log.topics)),
    )
    topics = {
        f"topic{i}": topic_dbid
        for i, topic_dbid in itertools.zip_longest(range(4), topic_dbids)
    }
    params = {
        "block_chain": CHAINID,
        "block_number": log.blockNumber,
        "transaction": transaction_dbid,
        "log_index": log.logIndex,
        "address": address_dbid,
        **topics,
        "raw": json.encode(Log(**log), enc_hook=enc_hook),
    }
    return tuple(params.values())


_check_using_extended_db = lambda: "eth_portfolio" in _get_get_block().__module__


async def bulk_insert(
    logs: List[Log], executor: AsyncExecutor = default_filter_threads
) -> None:
    if not logs:
        return

    submit = executor.submit

    # handle a conflict with eth-portfolio's extended db
    if _check_using_extended_db():
        blocks = tuple(
            (CHAINID, block, "BlockExtended")
            for block in {log.blockNumber for log in logs}
        )
        blocks_fut = submit(
            _bulk_insert, Block, _BLOCK_COLS_EXTENDED, blocks, sync=True
        )
    else:
        blocks = tuple((CHAINID, block) for block in {log.blockNumber for log in logs})
        blocks_fut = submit(_bulk_insert, Block, _BLOCK_COLS, blocks, sync=True)
    del blocks

    txhashes = (txhash.hex() for txhash in {log.transactionHash for log in logs})
    addresses = {log.address for log in logs}
    hashes = tuple(
        (_remove_0x_prefix(hash),) for hash in itertools.chain(txhashes, addresses)
    )
    hashes_fut = submit(_bulk_insert, Hashes, ("hash",), hashes, sync=True)
    del txhashes, addresses, hashes

    topics = set(concat(log.topics for log in logs))
    topics_fut = submit(
        _bulk_insert,
        LogTopic,
        ("topic",),
        tuple((_remove_0x_prefix(topic.strip()),) for topic in topics),
        sync=True,
    )
    del topics

    await cgather(blocks_fut, hashes_fut, topics_fut)

    await executor.run(
        _bulk_insert,
        DbLog,
        LOG_COLS,
        await igather(map(_prepare_log, logs)),
        sync=True,
    )


@a_sync(default="async", executor=_topic_executor, ram_cache_maxsize=None)
@db_session_cached
def get_topic_dbid(topic: Topic) -> int:
    topic = _remove_0x_prefix(topic.strip())
    entity = _get_log_topic(topic=topic)
    if entity is None:
        entity = LogTopic(topic=topic)
    return entity.dbid


@alru_cache(maxsize=10000, ttl=600)
async def get_hash_dbid(txhash: HexStr) -> int:
    return await _get_hash_dbid(txhash)


@a_sync(default="async", executor=_hash_executor)
@db_session_retry_locked
def _get_hash_dbid(hexstr: HexStr) -> int:
    if len(hexstr) == 42:
        hexstr = convert.to_address(hexstr)
    string = _remove_0x_prefix(hexstr)
    entity = _get_hash(hash=string)
    if entity is None:
        entity = Hashes(hash=string)
    return entity.dbid


def get_decoded(log: Log) -> Optional[_EventItem]:
    # TODO: load these in bulk
    if decoded := DbLog[
        CHAINID, log.block_number, log.transaction_hash, log.log_index
    ].decoded:
        return _EventItem(
            decoded["name"], decoded["address"], decoded["event_data"], decoded["pos"]
        )


@db_session
@retry_locked
def set_decoded(log: Log, decoded: _EventItem) -> None:
    DbLog[CHAINID, log.block_number, log.transaction_hash, log.log_index].decoded = (
        decoded
    )


page_size = 100


class LogCache(DiskCache[Log, LogCacheInfo]):
    __slots__ = "addresses", "topics"

    def __init__(self, addresses, topics):
        self.addresses = addresses
        self.topics = topics

    def __repr__(self) -> str:
        string = f"{type(self).__name__}(addresses={self.addresses}"
        for topic in ("topic0", "topic1", "topic2", "topic3"):
            if value := getattr(self, topic):
                string += f", {topic}={value}"
        return f"{string})"

    @property
    def topic0(self) -> str:
        return self.topics[0] if self.topics else None

    @property
    def topic1(self) -> str:
        return self.topics[1] if self.topics and len(self.topics) > 1 else None

    @property
    def topic2(self) -> str:
        return self.topics[2] if self.topics and len(self.topics) > 2 else None

    @property
    def topic3(self) -> str:
        return self.topics[3] if self.topics and len(self.topics) > 3 else None

    def load_metadata(self) -> Optional[LogCacheInfo]:
        """Loads the cache metadata from the db."""
        if self.addresses:
            raise NotImplementedError(self.addresses)

        from y._db.utils import utils as db

        chain = db.get_chain(sync=True)
        # If we cached all of this topic0 with no filtering for all addresses
        if self.topic0 and (
            info := _get_log_cache_info(
                chain=chain,
                address="None",
                topics=json.encode([self.topic0]),
            )
        ):
            return info
        # If we cached these specific topics for all addresses
        elif self.topics and (
            info := _get_log_cache_info(
                chain=chain,
                address="None",
                topics=json.encode(self.topics),
            )
        ):
            return info

    def _is_cached_thru(self, from_block: int) -> int:
        from y._db.utils import utils as db

        if self.addresses:
            chain = db.get_chain(sync=True)
            infos: List[LogCacheInfo]
            if isinstance(self.addresses, str):
                infos = [
                    # If we cached all logs for this address...
                    _get_log_cache_info(
                        chain=chain, address=self.addresses, topics=json.encode(None)
                    )
                    # ... or we cached all logs for these specific topics for this address
                    or _get_log_cache_info(
                        chain=chain,
                        address=self.addresses,
                        topics=json.encode(self.topics),
                    )
                ]
            else:
                infos = [
                    # If we cached all logs for this address...
                    _get_log_cache_info(
                        chain=chain, address=addr, topics=json.encode(None)
                    )
                    # ... or we cached all logs for these specific topics for this address
                    or _get_log_cache_info(
                        chain=chain, address=addr, topics=json.encode(self.topics)
                    )
                    for addr in self.addresses
                ]
            if all(info and from_block >= info.cached_from for info in infos):
                return min(info.cached_thru for info in infos)

        elif (info := self.load_metadata()) and from_block >= info.cached_from:
            return info.cached_thru
        return 0

    def _select(self, from_block: int, to_block: int) -> List[Log]:
        logger.warning("executing select query for %s", self)
        try:
            return [
                json.decode(log.raw, type=Log, dec_hook=_decode_hook)
                for log in self._get_query(from_block, to_block)
            ]
        except ValidationError:
            results = []
            for log in self._get_query(from_block, to_block):
                try:
                    results.append(
                        json.decode(log.raw, type=Log, dec_hook=_decode_hook)
                    )
                except ValidationError as e:
                    raise ValueError(e, json.decode(log.raw)) from e
            return results

    def _get_query(self, from_block: int, to_block: int) -> Query:
        from y._db.utils import utils as db

        generator = (
            log
            for log in DbLog
            if log.block.chain == db.get_chain(sync=True)
            and log.block.number >= from_block
            and log.block.number <= to_block
        )

        generator = self._wrap_query_with_addresses(generator)

        for topic in [f"topic{i}" for i in range(4)]:
            generator = self._wrap_query_with_topic(generator, topic)

        query = (
            select(generator)
            .without_distinct()
            .order_by(lambda l: (l.block.number, l.tx.hash, l.log_index))
        )
        logger.debug(query.get_sql())
        return query

    def _set_metadata(self, from_block: int, done_thru: int) -> None:
        from y._db.utils import utils as db

        chain = db.get_chain(sync=True)
        encoded_topics = json.encode(self.topics or None)
        should_commit = False
        if self.addresses:
            addresses = self.addresses
            if isinstance(addresses, str):
                addresses = [addresses]
            for address in addresses:
                if e := _get_log_cache_info(
                    chain=chain, address=address, topics=encoded_topics
                ):
                    if from_block < e.cached_from:
                        e.cached_from = from_block
                        should_commit = True
                    if done_thru > e.cached_thru:
                        e.cached_thru = done_thru
                        should_commit = True
                else:
                    LogCacheInfo(
                        chain=chain,
                        address=address,
                        topics=encoded_topics,
                        cached_from=from_block,
                        cached_thru=done_thru,
                    )
                    should_commit = True
        elif info := _get_log_cache_info(
            chain=chain,
            address="None",
            topics=encoded_topics,
        ):
            if from_block < info.cached_from:
                info.cached_from = from_block
                should_commit = True
            if done_thru > info.cached_thru:
                info.cached_thru = done_thru
                should_commit = True
        else:
            LogCacheInfo(
                chain=chain,
                address="None",
                topics=encoded_topics,
                cached_from=from_block,
                cached_thru=done_thru,
            )
            should_commit = True
        if should_commit:
            commit()
            logger.debug("cached %s %s thru %s", self.addresses, self.topics, done_thru)
        return

    def _wrap_query_with_addresses(self, generator) -> Query:
        if not (addresses := self.addresses):
            return generator
        elif isinstance(addresses, str):
            address = convert.to_address(addresses)[2:]
            return (log for log in generator if log.address.hash == address)
        addresses = tuple(convert.to_address(address)[2:] for address in addresses)
        return (log for log in generator if log.address.hash in addresses)

    def _wrap_query_with_topic(self, generator, topic_id: str) -> Query:
        if not (topic_or_topics := getattr(self, topic_id)):
            return generator

        if isinstance(topic_or_topics, (bytes, str)):
            topic = topic_or_topics
            topic = _remove_0x_prefix(HexBytes32(topic).strip())
            return (log for log in generator if getattr(log, topic_id).topic == topic)

        topics = [_remove_0x_prefix(HexBytes32(v).strip()) for v in topic_or_topics]
        return (log for log in generator if getattr(log, topic_id).topic in topics)


def _decode_hook(typ, obj):
    try:
        if issubclass(typ, uint):
            if isinstance(obj, int):
                return typ(obj)
            elif isinstance(obj, str):
                return typ.fromhex(obj)
        elif issubclass(typ, HexBytes):
            return typ(obj)
        elif typ is Address:
            return Address.checksum(obj)
    except (TypeError, ValueError, ValidationError) as e:
        raise Exception(e, typ, obj) from e
    raise NotImplementedError(typ, obj)


def _remove_0x_prefix(string: str) -> str:  # sourcery skip: str-prefix-suffix
    if not isinstance(string, str):
        raise TypeError(type(string), string)
    return string[2:] if string[:2] == "0x" else string
