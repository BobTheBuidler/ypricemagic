
import asyncio
import logging
from itertools import chain
from typing import AsyncIterator, List, Optional

from msgspec import json
from pony.orm import (OptimisticCheckError, TransactionIntegrityError, commit,
                      db_session, select)

from y._db.common import DiskCache
from y._db.entities import Chain, Trace, TraceCacheInfo, insert
from y._db.utils.utils import get_block
from y.utils.dank_mids import dank_w3
from y.utils.events import BATCH_SIZE, Filter

logger = logging.getLogger(__name__)

def insert_trace(trace: dict) -> None:
    kwargs = {
        "block": get_block(trace['blockNumber'], sync=True),
        "hash": trace['transactionHash'],
        "raw": json.encode(trace),
    }
    for dct in [trace, *trace.values()]:
        if "from" in dct:
            kwargs['from_address'] = dct["from"]
        if "to" in dct:
            kwargs['to_address'] = dct["to"]
    insert(type=Trace, **kwargs)

class TraceCache(DiskCache[dict, TraceCacheInfo]):
    __slots__ = "from_addresses", "to_addresses"
    def __init__(self, from_addresses: List[str], to_addresses: List[str]):
        self.from_addresses = from_addresses
        self.to_addresses = to_addresses
    
    def load_metadata(self, chain: Chain, from_address: Optional[str], to_address: Optional[str]) -> Optional[TraceCacheInfo]:
        return TraceCacheInfo.get(chain=chain, from_address=str(from_address), to_address=str(to_address))
    
    @db_session
    def is_cached_thru(self, from_block: int) -> int:
        from y._db.utils import utils as db
        chain = db.get_chain(sync=True)
        infos = [
            self.load_metadata(chain, from_address, to_address)
            or self.load_metadata(chain, from_address, None)
            or self.load_metadata(chain, None, to_address)
            for from_address in self.from_addresses
            for to_address in self.to_addresses
        ]
        if all(info and info.cached_from <= from_block for info in infos):
            return max(info.cached_thru for info in infos)
        return 0

    @db_session
    def select(self, from_block: int, to_block: int) -> List[dict]:
        from y._db.utils import utils as db
        return [
            json.decode(trace) for trace in select(
                trace.raw for trace in Trace 
                if trace.block.chain == db.get_chain(sync=True)
                and (not self.from_addresses or trace.address in self.from_addresses)
                and (not self.to_addresses or trace.address in self.to_addresses)
                and trace.block.number >= from_block
                and trace.block.number <= to_block
            )
        ]
    
    @db_session
    def set_metadata(self, from_block: int, done_thru: int) -> None:
        from y._db.utils import utils as db
        chain = db.get_chain(sync=True)
        should_commit = False
        try:
            if self.to_addresses and self.from_addresses:
                for from_address in self.from_addresses:
                    for to_address in self.to_addresses:
                        if info := TraceCacheInfo.get(
                                chain=chain, 
                                from_address=json.encode([from_address]),
                                to_address=json.encode([to_address])
                            ):
                                if from_block < info.cached_from:
                                    info.cached_from = from_block
                                    should_commit = True
                                if done_thru > info.cached_thru:
                                    info.cached_thru = done_thru
                                    should_commit = True
                        else:
                            TraceCacheInfo(
                                chain=chain, 
                                from_address=json.encode([from_address]),
                                to_address=json.encode([to_address])
                            )
                            should_commit = True
            elif self.from_addresses:
                for from_address in self.from_addresses:
                    if info := TraceCacheInfo.get(
                        chain=chain, 
                        from_address=json.encode([from_address]),
                        to_address=json.encode([])
                    ):
                        if from_block < info.cached_from:
                            info.cached_from = from_block
                            should_commit = True
                        if done_thru > info.cached_thru:
                            info.cached_thru = done_thru
                            should_commit = True
                    else:
                        TraceCacheInfo(
                            chain=chain, 
                            from_address=json.encode([from_address]),
                            to_address=json.encode([])
                        )
                        should_commit = True
            elif self.to_addresses:
                for to_address in self.to_addresses:
                    if info := TraceCacheInfo.get(
                        chain=chain, 
                        from_address=json.encode([]),
                        to_address=json.encode([to_address])
                    ):
                        if from_block < info.cached_from:
                            info.cached_from = from_block
                            should_commit = True
                        if done_thru > info.cached_thru:
                            info.cached_thru = done_thru
                            should_commit = True
                    else:
                        TraceCacheInfo(
                            chain=chain, 
                            from_address=json.encode([]),
                            to_address=json.encode([to_address])
                        )
                        should_commit = True
            elif info := TraceCacheInfo.get(
                chain=chain, 
                from_address=json.encode([]),
                to_address=json.encode([])
            ):
                if from_block < info.cached_from:
                    info.cached_from = from_block
                    should_commit = True
                if done_thru > info.cached_thru:
                    info.cached_thru = done_thru
                    should_commit = True
            else:
                TraceCacheInfo(
                    chain=chain, 
                    from_address=json.encode([]),
                    to_address=json.encode([])
                )
                should_commit = True

            if should_commit:
                commit()
                logger.debug('cached %s %s thru %s', self.from_addresses, self.to_addresses, done_thru)
        except (TransactionIntegrityError, OptimisticCheckError):
            return self.set_metadata(from_block, done_thru)


class TraceFilter(Filter[dict, TraceCache]):
    _db_insert_fn = insert_trace
    __slots__ = "from_addresses", "to_addresses"
    def __init__(
        self, 
        from_addresses: List[str], 
        to_addresses: List[str], 
        from_block: int,
        *,
        batch_size: int = BATCH_SIZE,
        interval: int = 300,
        semaphore: int = 32,
        verbose: bool = False
    ):
        self.from_addresses = from_addresses
        self.to_addresses = to_addresses
        super().__init__(from_block, batch_size=batch_size, interval=interval, semaphore=semaphore, verbose=verbose)

    @property
    def cache(self) -> TraceCache:
        if self._cache is None:
            self._cache = TraceCache(self.from_addresses, self.to_addresses)
        return self._cache

    def traces(self, to_block: Optional[int]) -> AsyncIterator[dict]:
        return self._objects_thru(block=to_block)

    async def _fetch_range(self, from_block: int, to_block: int) -> List[dict]:
        try:
            return await dank_w3.provider.make_request("TraceFilter", {})
        except NotImplementedError:
            async def trace_block(number: int) -> List[dict]:
                return number, await dank_w3.provider.make_request("TraceBlock", number)
            
            results = {}
            for fut in asyncio.as_completed([trace_block(i) for i in range(from_block, to_block)]):
                block, traces = await fut
                results[block] = [
                    trace for trace in traces
                    if (not self.from_addresses or any("from" in x and x["from"] in self.from_addresses for x in [trace, trace.values()]))
                    and (not self.to_addresses or any("to" in x and x["to"] in self.to_addresses for x in [trace, trace.values()]))
                ]
            return list(chain(*[results[i] for i in range(from_block, to_block)]))