
import logging
from typing import List, Optional

from msgspec import json
from pony.orm import (OptimisticCheckError, TransactionIntegrityError, commit,
                      db_session, select)
from pony.orm.core import Query
from web3.types import LogReceipt

from y._db.common import DiskCache, enc_hook
from y._db.entities import Log, LogCacheInfo, insert, retry_locked
from y._db.utils._ep import _get_get_block

logger = logging.getLogger(__name__)


@db_session
@retry_locked
def insert_log(log: dict):
    get_block = _get_get_block()
    log_topics = log['topics']
    insert(
        type=Log,
        block=get_block(log['blockNumber'], sync=True),
        transaction_hash = log['transactionHash'].hex(),
        log_index = log['logIndex'],
        address = log['address'],
        **{f"topic{i}": log_topics[i].hex() for i in range(min(len(log_topics), 4))},
        raw = json.encode(log, enc_hook=enc_hook),
    )

class LogCache(DiskCache[LogReceipt, LogCacheInfo]):
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
    
    def load_metadata(self) -> Optional["LogCacheInfo"]:
        """Loads the cache metadata from the db."""
        if self.addresses:
            raise NotImplementedError(self.addresses)
            
        from y._db.utils import utils as db
        chain = db.get_chain(sync=True)
        # If we cached all of this topic0 with no filtering for all addresses
        if self.topic0 and (info := LogCacheInfo.get(
            chain=chain,
            address='None',
            topics=json.encode([self.topic0]),
        )):
            return info
        # If we cached these specific topics for all addresses
        elif self.topics and (info := LogCacheInfo.get(
            chain=chain,
            address='None',
            topics=json.encode(self.topics),
        )):
            return info
    
    @db_session
    def is_cached_thru(self, from_block: int) -> int:
        from y._db.utils import utils as db
        
        if self.addresses:
            chain = db.get_chain(sync=True)
            infos: List[LogCacheInfo] = [
                # If we cached all logs for this address...
                LogCacheInfo.get(chain=chain, address=addr, topics=json.encode(None))
                # ... or we cached all logs for these specific topics for this address
                or LogCacheInfo.get(chain=chain, address=addr, topics=json.encode(self.topics))
                for addr in self.addresses
            ]
            if all(info and from_block >= info.cached_from for info in infos):
                return min(info.cached_thru for info in infos)
                
        elif (info := self.load_metadata()) and from_block >= info.cached_from:
            return info.cached_thru
        return 0
    
    @db_session
    def select(self, from_block: int, to_block: int) -> List[LogReceipt]:
        from y._db.utils import utils as db

        generator = (
            log 
            for log in Log
            if log.block.chain == db.get_chain(sync=True)
            and log.block.number >= from_block
            and log.block.number <= to_block
        )

        self._wrap_query_with_addresses(generator)
        
        for topic in [f"topic{i}" for i in range(4)]:
            generator = self._wrap_query_with_topic(generator, topic)

        return select(log.raw for log in generator).without_distinct()
    
    @db_session
    @retry_locked
    def set_metadata(self, from_block: int, done_thru: int) -> None:
        from y._db.utils import utils as db
        chain = db.get_chain(sync=True)
        encoded_topics = json.encode(self.topics or None)
        should_commit = False
        try:
            if self.addresses:
                for address in self.addresses:
                    if e:=LogCacheInfo.get(chain=chain, address=address, topics=encoded_topics):
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
                            cached_from = from_block,
                            cached_thru = done_thru,
                        )
                        should_commit = True
            elif info := LogCacheInfo.get(
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
                LogCacheInfo(
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
        except (TransactionIntegrityError, OptimisticCheckError):
            return self.set_metadata(from_block, done_thru)
    
    def _wrap_query_with_addresses(self, generator) -> Query:
        if addresses := self.addresses:
            return (log for log in generator if log.address in addresses)
        return generator
    
    def _wrap_query_with_topic(self, generator, topic: str) -> Query:
        if value := getattr(self, topic):
            return (log for log in generator if getattr(log, topic) in value)
        return generator
