
import logging
from contextlib import suppress
from typing import List, Optional

from msgspec import json
from pony.orm import (OptimisticCheckError, TransactionIntegrityError, commit,
                      db_session, select)

from y._db.common import enc_hook
from y._db.entities import Log, LogCacheInfo
from y._db.utils import get_block

logger = logging.getLogger(__name__)


@db_session
def insert_log(log: dict):
    log_topics = log['topics']
    topics = {f"topic{i}": log_topics[i].hex() for i in range(min(len(log_topics), 4))}
    with suppress(TransactionIntegrityError):
        Log(
            block=get_block(log['blockNumber'], sync=True),
            transaction_hash = log['transactionHash'].hex(),
            log_index = log['logIndex'],
            address = log['address'],
            **topics,
            raw = json.encode(log, enc_hook=enc_hook),
        )
        commit()

class LogCache:
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
        """Returns max cached block for these getLogs params or 0 if not cached."""

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
    def select(self, from_block: int, to_block: int) -> List[dict]:
        from y._db.utils import utils as db
        if self.addresses:
            return [
                json.decode(log) for log in select(
                    log.raw for log in Log 
                    if log.block.chain == db.get_chain(sync=True)
                    and log.address in self.addresses
                    and (self.topic0 is None or log.topic0 in self.topic0)
                    and (self.topic1 is None or log.topic1 in self.topic1)
                    and (self.topic2 is None or log.topic2 in self.topic2)
                    and (self.topic3 is None or log.topic3 in self.topic3)
                    and from_block <= log.block.number <= to_block
                )
            ]
        else:
            return [
                json.decode(log) for log in select(
                    log.raw for log in Log 
                    if log.block.chain == db.get_chain(sync=True)
                    and (self.topic0 is None or log.topic0 in self.topic0)
                    and (self.topic1 is None or log.topic1 in self.topic1)
                    and (self.topic2 is None or log.topic2 in self.topic2)
                    and (self.topic3 is None or log.topic3 in self.topic3)
                    and log.block.number >= from_block
                    and from_block <= log.block.number <= to_block
                )
            ]
    
    @db_session
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