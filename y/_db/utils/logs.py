
import asyncio
import itertools
import logging
from typing import _GenericAlias, List, Optional, final

from a_sync.executor import _AsyncExecutorMixin
from async_lru import alru_cache
from brownie import chain
from brownie.convert import EthAddress
from brownie.network.event import _EventItem
from dank_mids.structs import Log
from dank_mids.structs.data import Address, HashableList, HexBytes32, uint, checksum
from dank_mids.structs.log import Topic
from eth_typing import HexStr
from hexbytes import HexBytes
from msgspec import json, ValidationError
from pony.orm import commit, db_session, select
from pony.orm.core import Query

from y._db import decorators, entities
from y._db.common import DiskCache, enc_hook, default_filter_threads
from y._db.utils import bulk
from y._db.utils._ep import _get_get_block

logger = logging.getLogger(__name__)

LOG_COLS = ["block_chain", "block_number", "tx", "log_index", "address", "topic0", "topic1", "topic2", "topic3", "raw"]


@final
class ArrayEncodableLog(Log, frozen=True, kw_only=True, array_like=True):
    """
    It works just like a :class:`~structs.Log` but it encodes to a tuple instead of a dict to save space when keys are known.
    """


async def _prepare_log(log: Log) -> tuple:
    transaction_dbid, address_dbid = await asyncio.gather(get_hash_dbid(log.transactionHash.hex()), get_hash_dbid(log.address))
    return  tuple({
        "block_chain": chain.id,
        "block_number": log.blockNumber,
        "transaction": transaction_dbid,
        "log_index": log.logIndex,
        "address": address_dbid,
        **{f"topic{i}": await get_topic_dbid(log_topics[i]) if i < len(log_topics := log.topics) else None for i in range(4)},
        "raw": json.encode(ArrayEncodableLog(**log), enc_hook=enc_hook),
    }.values())

_check_using_extended_db = lambda: 'eth_portfolio' in _get_get_block().__module__

async def bulk_insert(logs: List[Log], executor: _AsyncExecutorMixin = default_filter_threads) -> None:
    if not logs:
        return
    
    block_cols = ["chain", "number"]
    # handle a conflict with eth-portfolio's extended db
    if _check_using_extended_db():
        # TODO: refactor this ugly shit out
        block_cols.append("classtype")
        blocks = [(chain.id, block, "BlockExtended") for block in {log.blockNumber for log in logs}]
    else:
        blocks = [(chain.id, block) for block in {log.blockNumber for log in logs}]
    await executor.run(bulk.insert, entities.Block, block_cols, blocks, sync=True)

    txhashes = (txhash.hex() for txhash in {log.transactionHash for log in logs})
    addresses = (EthAddress(addr) for addr in {log.address for log in logs})
    hashes = [[_remove_0x_prefix(hash)] for hash in itertools.chain(txhashes, addresses)]
    await executor.run(bulk.insert, entities.Hashes, ["hash"], hashes, sync=True)

    topics = {*itertools.chain(*(log.topics for log in logs))}
    await executor.run(bulk.insert, entities.LogTopic, ["topic"], [[_remove_0x_prefix(topic.strip())] for topic in topics], sync=True)

    await executor.run(bulk.insert, entities.Log, LOG_COLS, await asyncio.gather(*[_prepare_log(log) for log in logs]), sync=True)

@decorators.a_sync_write_db_session_cached
def get_topic_dbid(topic: Topic) -> int:
    topic = _remove_0x_prefix(topic.strip())
    entity = entities.LogTopic.get(topic=topic)
    if entity is None:
        entity = entities.LogTopic(topic=topic)
    return entity.dbid

@alru_cache(maxsize=1024, ttl=600)
async def get_hash_dbid(txhash: HexStr) -> int:
    return await _get_hash_dbid(txhash)

@decorators.a_sync_write_db_session
def _get_hash_dbid(hexstr: HexStr) -> int:
    if len(hexstr) == 42:
        hexstr = EthAddress(hexstr)
    string = _remove_0x_prefix(hexstr)
    entity = entities.Hashes.get(hash=string)
    if entity is None:
        entity = entities.Hashes(hash=string)
    return entity.dbid

def get_decoded(log: Log) -> Optional[_EventItem]:
    # TODO: load these in bulk
    if decoded := entities.Log[chain.id, log.block_number, log.transaction_hash, log.log_index].decoded:
        return _EventItem(decoded['name'], decoded['address'], decoded['event_data'], decoded['pos'])

@db_session
@decorators.retry_locked
def set_decoded(log: Log, decoded: _EventItem) -> None:
    entities.Log[chain.id, log.block_number, log.transaction_hash, log.log_index].decoded = decoded

page_size = 100

class LogCache(DiskCache[ArrayEncodableLog, entities.LogCacheInfo]):
    __slots__ = 'addresses', 'topics'

    def __init__(self, addresses, topics):
        self.addresses = addresses
        self.topics = topics
    
    def __repr__(self) -> str:
        string = f"{type(self).__name__}(addresses={self.addresses}"
        for topic in ['topic0', 'topic1', 'topic2', 'topic3']:
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
    
    def load_metadata(self) -> Optional["entities.LogCacheInfo"]:
        """Loads the cache metadata from the db."""
        if self.addresses:
            raise NotImplementedError(self.addresses)
            
        from y._db.utils import utils as db
        chain = db.get_chain(sync=True)
        # If we cached all of this topic0 with no filtering for all addresses
        if self.topic0 and (info := entities.LogCacheInfo.get(
            chain=chain,
            address='None',
            topics=json.encode([self.topic0]),
        )):
            return info
        # If we cached these specific topics for all addresses
        elif self.topics and (info := entities.LogCacheInfo.get(
            chain=chain,
            address='None',
            topics=json.encode(self.topics),
        )):
            return info
    
    def _is_cached_thru(self, from_block: int) -> int:
        from y._db.utils import utils as db
        if self.addresses:
            chain = db.get_chain(sync=True)
            infos: List[entities.LogCacheInfo]
            if isinstance(self.addresses, str):
                infos = [
                    # If we cached all logs for this address...
                    entities.LogCacheInfo.get(chain=chain, address=self.addresses, topics=json.encode(None))
                    # ... or we cached all logs for these specific topics for this address
                    or entities.LogCacheInfo.get(chain=chain, address=self.addresses, topics=json.encode(self.topics))
                ]
            else:
                infos = [
                    # If we cached all logs for this address...
                    entities.LogCacheInfo.get(chain=chain, address=addr, topics=json.encode(None))
                    # ... or we cached all logs for these specific topics for this address
                    or entities.LogCacheInfo.get(chain=chain, address=addr, topics=json.encode(self.topics))
                    for addr in self.addresses
                ]
            if all(info and from_block >= info.cached_from for info in infos):
                return min(info.cached_thru for info in infos)
                
        elif (info := self.load_metadata()) and from_block >= info.cached_from:
            return info.cached_thru
        return 0
    
    def _select(self, from_block: int, to_block: int) -> List[ArrayEncodableLog]:
        logger.warning("executing select query for %s", self)
        try:
            return [json.decode(log.raw, type=ArrayEncodableLog, dec_hook=_decode_hook) for log in self._get_query(from_block, to_block)]
        except ValidationError:
            results = []
            for log in self._get_query(from_block, to_block):
                try:
                    results.append(json.decode(log.raw, type=ArrayEncodableLog, dec_hook=_decode_hook))
                except ValidationError as e:
                    raise ValueError(e, json.decode(log.raw)) from e
            return results
    
    def _get_query(self, from_block: int, to_block: int) -> Query:
        from y._db.utils import utils as db

        generator = (
            log 
            for log in entities.Log
            if log.block.chain == db.get_chain(sync=True)
            and log.block.number >= from_block
            and log.block.number <= to_block
        )

        generator = self._wrap_query_with_addresses(generator)
        
        for topic in [f"topic{i}" for i in range(4)]:
            generator = self._wrap_query_with_topic(generator, topic)

        query = select(generator).without_distinct().order_by(lambda l: (l.block.number, l.tx.hash, l.log_index))
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
                if e:=entities.LogCacheInfo.get(chain=chain, address=address, topics=encoded_topics):
                    if from_block < e.cached_from:
                        e.cached_from = from_block
                        should_commit = True
                    if done_thru > e.cached_thru:
                        e.cached_thru = done_thru
                        should_commit = True
                else:
                    entities.LogCacheInfo(
                        chain=chain, 
                        address=address,
                        topics=encoded_topics,
                        cached_from = from_block,
                        cached_thru = done_thru,
                    )
                    should_commit = True
        elif info := entities.LogCacheInfo.get(
            chain=chain, 
            address='None',
            topics=encoded_topics,
        ):
            if from_block < info.cached_from:
                info.cached_from = from_block
                should_commit = True
            if done_thru > info.cached_thru:
                info.cached_thru = done_thru
                should_commit = True
        else:
            entities.LogCacheInfo(
                chain=chain,
                address='None',
                topics=encoded_topics,
                cached_from = from_block,
                cached_thru = done_thru,
            )
            should_commit = True
        if should_commit:
            commit()
            logger.debug('cached %s %s thru %s', self.addresses, self.topics, done_thru)
        return

    def _wrap_query_with_addresses(self, generator) -> Query:
        if not (addresses := self.addresses):
            logger.warning('skipping wrapping with addresses')
            return generator
        elif isinstance(addresses, str):
            address = _remove_0x_prefix(EthAddress(addresses))
            logger.warning('address modified to %s', address)
            return (log for log in generator if log.address.hash == address)
        addresses = [_remove_0x_prefix(EthAddress(address)) for address in addresses]
        logger.warning('addresses modified to %s', addresses)
        return (log for log in generator if log.address.hash in addresses)
    
    def _wrap_query_with_topic(self, generator, topic_id: str) -> Query:
        if not (topic_or_topics := getattr(self, topic_id)):
            return generator
        
        if isinstance(topic_or_topics, (bytes, str)):
            topic = topic_or_topics
            topic = _remove_0x_prefix(HexBytes32(topic).strip())
            logger.warning('new value %s', topic)
            return (log for log in generator if getattr(log, topic_id).topic == topic)
        
        topics = [_remove_0x_prefix(HexBytes32(v).strip()) for v in topic_or_topics]
        logger.warning("selecting %s: %s", topic_id, topics)
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
            return checksum(obj)
        elif getattr(typ, "__origin__", None) is HashableList:
            assert len(typ.__args__) == 1, typ.__dict__
            obj_cls = typ.__args__[0]
            return HashableList(_decode_hook(obj_cls, x) for x in obj)
    except (TypeError, ValueError, ValidationError) as e:
        raise Exception(e, typ, obj) from e
    raise NotImplementedError(typ, obj)
    
def _remove_0x_prefix(string: str) -> str:  # sourcery skip: str-prefix-suffix
    if not isinstance(string, str):
        raise TypeError(type(string), string)
    return string[2:] if string[:2] == "0x" else string
