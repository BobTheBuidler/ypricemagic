
import logging
from typing import List, Optional

from brownie import chain
from brownie.convert import EthAddress
from brownie.network.event import _EventItem
from msgspec import json
from pony.orm import commit, db_session, select
from pony.orm.core import Query
from web3.types import LogReceipt

from y._db import decorators, entities, structs
from y._db.common import DiskCache, enc_hook
from y._db.utils import bulk
from y._db.utils.utils import ensure_block
from y import ENVIRONMENT_VARIABLES as ENVS

logger = logging.getLogger(__name__)


@db_session
@decorators.retry_locked
def insert_log(log: LogReceipt) -> None:
    block = log['blockNumber']
    ensure_block(block, sync=True)
    log_topics = log['topics']
    entities.insert(
        type=entities.Log,
        block=(chain.id, block),
        transaction_hash = log['transactionHash'].hex(),
        log_index = log['logIndex'],
        address = log['address'],
        **{f"topic{i}": log_topics[i].hex() for i in range(min(len(log_topics), 4))},
        raw = json.encode(log, enc_hook=enc_hook),
    )

@db_session
@decorators.retry_locked
def bulk_insert(logs: List[LogReceipt]) -> None:
    items = []
    blocks = set()
    for log in logs:
        block = log['blockNumber']
        blocks.add(block)
        log_topics = log['topics']
        topics = {f"topic{i}": log_topics[i].hex() if i < len(log_topics) else None for i in range(4)}
        item = {
            "block_chain": chain.id,
            "block_number": block,
            "transaction_hash": log['transactionHash'].hex(),
            "log_index": log['logIndex'],
            "address": log['address'],
            **topics,
            "raw": json.encode(log, enc_hook=enc_hook),
        }
        items.append(item)

    # TODO: replace this with bulk insert for big data projects
    for block in blocks:
        ensure_block(block, sync=True)
    #bulk.insert(entities.Block, ["chain", "number"], ((chain.id, block) for block in blocks))
    columns = ["block_chain", "block_number", "transaction_hash", "log_index", "address", "topic0", "topic1", "topic2", "topic3", "raw"]
    bulk.insert(entities.Log, columns, [tuple(i.values()) for i in items], sync=True)
    commit()
    logger.debug('inserted %s logs to ydb', len(items))

def get_decoded(log: structs.Log) -> _EventItem:
    # TODO: load these in bulk
    log = entities.Log[chain.id, log.block_number, log.transaction_hash, log.log_index]
    if decoded := log.decoded:
        return _EventItem(decoded['name'], decoded['address'], decoded['event_data'], decoded['pos'])

@db_session
@decorators.retry_locked
def set_decoded(log: structs.Log, decoded: _EventItem):
    entities.Log[chain.id, log.block_number, log.transaction_hash, log.log_index].decoded = decoded

page_size = 100

class LogCache(DiskCache[LogReceipt, entities.LogCacheInfo]):
    __slots__ = 'addresses', 'topics'

    def __init__(self, addresses, topics):
        self.addresses = addresses
        self.topics = topics
    
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
    
    def _select(self, from_block: int, to_block: int) -> List[LogReceipt]:
        return [json.decode(log.raw, type=structs.Log) for log in self._get_query(from_block, to_block)]
    
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

        query = select(generator).without_distinct().order_by(lambda l: (l.block.number, l.transaction_hash, l.log_index))
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
        if addresses := self.addresses:
            logger.debug("%s addresses: %s", self, addresses)
            if isinstance(addresses, str):
                return (log for log in generator if log.address == str(EthAddress(addresses)))
            return (log for log in generator if log.address in addresses)
        return generator
    
    def _wrap_query_with_topic(self, generator, topic: str) -> Query:
        if value := getattr(self, topic):
            logger.debug("%s %s is %s", self, topic, value)
            if isinstance(value, (bytes, str)):
                return (log for log in generator if getattr(log, topic) == value)
            return (log for log in generator if getattr(log, topic) in value)
        return generator
