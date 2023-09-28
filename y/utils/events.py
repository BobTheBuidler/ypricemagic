import asyncio
import logging
import threading
from collections import Counter, defaultdict
from itertools import zip_longest
from typing import (Any, AsyncGenerator, AsyncIterator, Dict, Iterable, List,
                    NoReturn, Optional)

import a_sync
import eth_retry
from a_sync.primitives.locks.counter import CounterLock
from brownie import web3
from brownie.convert.datatypes import EthAddress
from brownie.network.event import EventDict, _decode_logs, _EventItem
from dank_mids.semaphores import BlockSemaphore
from eth_typing import ChecksumAddress
from msgspec import json
from pony.orm import db_session, select
from toolz import groupby
from web3.middleware.filter import block_ranges
from web3.types import LogReceipt

from y.constants import thread_pool_executor
from y.contracts import contract_creation_block_async
from y.datatypes import Address, Block
from y.utils.cache import memory
from y.utils.dank_mids import dank_w3
from y.utils.middleware import BATCH_SIZE

logger = logging.getLogger(__name__)


def decode_logs(logs: List[LogReceipt]) -> EventDict:
    """
    Decode logs to events and enrich them with additional info.
    """
    decoded = _decode_logs(logs)
    for i, log in enumerate(logs):
        setattr(decoded[i], "block_number", log["blockNumber"])
        setattr(decoded[i], "transaction_hash", log["transactionHash"])
        setattr(decoded[i], "log_index", log["logIndex"])
    return decoded


@a_sync.a_sync(default='sync')
async def get_logs_asap(
    address: Optional[Address],
    topics: Optional[List[str]],
    from_block: Optional[Block] = None,
    to_block: Optional[Block] = None,
    verbose: int = 0
) -> List[Any]:

    if from_block is None:
        from_block = 0 if address is None else await contract_creation_block_async(address, True)
    if to_block is None:
        to_block = await dank_w3.eth.block_number

    ranges = list(block_ranges(from_block, to_block, BATCH_SIZE))
    if verbose > 0:
        logger.info('fetching %d batches', len(ranges))
    
    batches = await asyncio.gather(*[_get_logs_async(address, topics, start, end) for start, end in ranges])
    return [log for batch in batches for log in batch]


async def get_logs_asap_generator(
    address: Optional[Address],
    topics: Optional[List[str]] = None,
    from_block: Optional[Block] = None,
    to_block: Optional[Block] = None,
    chronological: bool = True,
    run_forever: bool = False,
    run_forever_interval: int = 60,
    verbose: int = 0
) -> AsyncGenerator[List[LogReceipt], None]:
    # NOTE: If you don't need the logs in order, you will get your logs faster if you set `chronological` to False.

    if from_block is None:
        if address is None:
            from_block = 0
        elif isinstance(address, Iterable) and not isinstance(address, str):
            from_block = min(await asyncio.gather(*[contract_creation_block_async(addr, True) for addr in address]))
        else:
            from_block = await contract_creation_block_async(address, True)
    if to_block is None:
        to_block = await dank_w3.eth.block_number
    elif run_forever:
        raise TypeError(f'`to_block` must be None if `run_forever` is True.')
    if from_block > to_block:
        raise ValueError(f"from_block must be <= to_block. You passed from_block: {from_block} to_block: {to_block}.")
    while True:
        ranges = list(block_ranges(from_block, to_block, BATCH_SIZE))
        if verbose > 0:
            logger.info('fetching %d batches', len(ranges))
        coros = [_get_logs_async(address, topics, start, end) for start, end in ranges]
        if chronological:
            async def wrap(i, coro):
                return i, await coro
            yielded = 0
            done = {}
            for logs in asyncio.as_completed([wrap(i, coro) for i, coro in enumerate(coros)], timeout=None):
                i, result = await logs
                done[i] = result
                for i in range(len(coros)):
                    if yielded > i:
                        continue
                    if i not in done:
                        break
                    yield done.pop(i)
                    yielded += 1
        else:
            for logs in asyncio.as_completed(coros, timeout=None):
                yield await logs
        if not run_forever:
            return
        
        await asyncio.sleep(run_forever_interval)
        
        # Find start and end block for next loop
        current_block = await dank_w3.eth.block_number
        while current_block <= to_block:
            await asyncio.sleep(run_forever_interval)
            current_block = await dank_w3.eth.block_number
        from_block = to_block + 1 if to_block + 1 <= current_block else current_block
        to_block = current_block


def logs_to_balance_checkpoints(logs) -> Dict[EthAddress,int]:
    """
    Convert Transfer logs to `{address: {from_block: balance}}` checkpoints.
    """
    balances = Counter()
    checkpoints = defaultdict(dict)
    for block, block_logs in groupby('blockNumber', logs).items():
        events = decode_logs(block_logs)
        for log in events:
            # ZERO_ADDRESS tracks -totalSupply
            sender, receiver, amount = log.values()  # there can be several different aliases
            balances[sender] -= amount
            checkpoints[sender][block] = balances[sender]
            balances[receiver] += amount
            checkpoints[receiver][block] = balances[receiver]
    return checkpoints


def checkpoints_to_weight(checkpoints, start_block: Block, end_block: Block) -> float:
    total = 0
    for a, b in zip_longest(list(checkpoints), list(checkpoints)[1:]):
        if a < start_block or a > end_block:
            continue
        b = min(b, end_block) if b else end_block
        total += checkpoints[a] * (b - a) / (end_block - start_block)
    return total

@a_sync.a_sync(executor=thread_pool_executor)
def _get_logs(
    address: Optional[ChecksumAddress],
    topics: Optional[List[str]],
    start: Block,
    end: Block
    ) -> List[LogReceipt]:
    if end - start == BATCH_SIZE - 1:
        response = _get_logs_batch_cached(address, topics, start, end)
    else:
        response = _get_logs_no_cache(address, topics, start, end)
    for log in response:
        if address and log.address != address:
            ''' I have this due to a corrupt cache on my local box that I would prefer not to lose. '''
            ''' It will not impact your scripts. ''' 
            response.remove(log)
    return response

get_logs_semaphore = defaultdict(
    lambda: BlockSemaphore(
        thread_pool_executor._max_workers * 10, 
        # We need to do this in case users use the sync api in a multithread context
        name="y.get_logs" + "" if threading.current_thread() == threading.main_thread() else f".{threading.current_thread()}",
    )
)

async def _get_logs_async(address, topics, start, end) -> List[LogReceipt]:
    async with get_logs_semaphore[threading.current_thread()][end]:
        return await _get_logs(address, topics, start, end, asynchronous=True)

@eth_retry.auto_retry
def _get_logs_no_cache(
    address: Optional[ChecksumAddress],
    topics: Optional[List[str]],
    start: Block,
    end: Block
    ) -> List[LogReceipt]:
    logger.debug('fetching logs %s to %s', start, end)
    try:
        if address is None:
            response = web3.eth.get_logs({"topics": topics, "fromBlock": start, "toBlock": end})
        elif topics is None:
            response = web3.eth.get_logs({"address": address, "fromBlock": start, "toBlock": end})
        else:
            response = web3.eth.get_logs({"address": address, "topics": topics, "fromBlock": start, "toBlock": end})
    except Exception as e:
        errs = [
            "Service Unavailable for url:",
            "exceed maximum block range",
            "block range is too wide",
            "request timed out",
        ]
        if any(err in str(e) for err in errs):
            logger.debug('your node is having trouble, breaking batch in half')
            batch_size = (end - start + 1)
            half_of_batch = batch_size // 2
            batch1_end = start + half_of_batch
            batch2_start = batch1_end + 1
            batch1 = _get_logs_no_cache(address, topics, start, batch1_end)
            batch2 = _get_logs_no_cache(address, topics, batch2_start, end)
            response = batch1 + batch2
        else:
            raise
    return response



##############################
# Leaving this here so as to not upset people's caches
##############################


@memory.cache()
def _get_logs_batch_cached(
    address: Optional[str],
    topics: Optional[List[str]],
    start: Block,
    end: Block
    ) -> List[LogReceipt]:
    return _get_logs_no_cache(address, topics, start, end)

BIG_VALUE = 9999999999999999999999999999999999999999999999999999999999999999999999999

@db_session
def _cache_log(addresses: bytes, topics: bytes, log: dict):
    from y._db import utils as db
    from y._db.entities import Block, Log
    chain = db.get_chain(sync=True)
    if (block := Block.get(chain=chain, number=log['blockNumber'])) is None:
        block = Block(chain=chain, number=log['blockNumber'])
    Log(
        addresses=addresses,
        topics=topics,
        block=block, 
        transaction_hash = log['transactionHash'],
        log_index = log['logIndex'],
    )

class Logs:
    __slots__ = 'addresses', 'topics', 'from_block', 'interval', '_logs_task', '_logs', '_lock', '_exc'
    @db_session
    def __init__(
        self, 
        *, 
        addresses = [], 
        topics = [], 
        from_block: Optional[int] = None,
        interval: int = 300,
    ):
        self.addresses = addresses
        self.topics = topics
        self.from_block = from_block
        self.interval = interval
        self._logs_task = None
        self._logs = []
        self._lock = CounterLock()
        self._exc = None

    
    async def _load_cache(self) -> None:
        from y._db import utils as db
        from y._db.entities import Log, LogCacheInfo
        with db_session:
            chain = await db.get_chain(sync=False)
            e: LogCacheInfo = LogCacheInfo.get(chain=chain, addresses=json.encode(self.addresses), topics=json.encode(self.topics))
            if e and (self.from_block is None or e.cached_from >= self.from_block):
                self._logs.extend(
                    json.decode(raw)
                    for raw in select(
                        log.raw 
                        for log in Log 
                        if log.addresses == json.encode(self.addresses) 
                        and log.topics == json.encode(self.topics) 
                        and (self.from_block is None or log.block.number >= self.from_block)
                    )
                )
                if self._logs:
                    self._lock.set(self._logs[-1]['blockNumber'])
    
    def __aiter__(self) -> AsyncIterator[_EventItem]:
        return self.logs().__aiter__()

    async def logs(self, to_block: Optional[int] = None) -> AsyncIterator[dict]:
        if self._logs_task is None:
            self._logs_task = asyncio.create_task(self._fetch())
        yielded = 0
        done_thru = 0
        from y._db import utils as db
        from y._db.entities import LogCacheInfo
        encoded = json.encode(self.addresses), json.encode(self.topics)
        while True:
            _tasks = []
            await self._lock.wait_for(done_thru + 1)
            if self._exc:
                raise self._exc
            for log in self._logs[yielded:]:
                block = log['blockNumber']
                if to_block and block > to_block:
                    return
                _tasks.append(thread_pool_executor.submit(_cache_log, *encoded, log))
                yield log
                yielded += 1
            await asyncio.gather(_tasks)
            with db_session:
                chain = await db.get_chain(sync=False)
                if e:=LogCacheInfo.get(chain=chain, addresses=encoded[0], topics=encoded[1]):
                    if self.from_block < e.cached_from:
                        e.cached_from = self.from_block
                    if block > e.cached_thru:
                        e.cached_thru = block
                else:
                    LogCacheInfo(
                        chain=chain, 
                        addresses=encoded[0],
                        topics=encoded[1],
                        cached_from = self.from_block,
                        cached_thru = block
                    )
            done_thru = block
    
    async def _fetch(self) -> NoReturn:
        try:
            await self.__fetch()
        except Exception as e:
            self._exc = e
            self._lock.set(BIG_VALUE)

    async def __fetch(self) -> NoReturn:
        from_block = self.from_block
        if from_block is None:
            if self.addresses is None:
                from_block = 0
            elif isinstance(self.addresses, Iterable) and not isinstance(self.addresses, str):
                from_block = min(await asyncio.gather(*[contract_creation_block_async(addr, True) for addr in self.addresses]))
            else:
                from_block = await contract_creation_block_async(self.addresses, True)
    
        done_thru = from_block - 1
        while True:
            range_start, range_end = done_thru + 1, await dank_w3.eth.block_number
            ranges = list(block_ranges(range_start, range_end, BATCH_SIZE))
            coros = [_get_logs_async(self.addresses, self.topics, start, end) for start, end in ranges]
            async def wrap(i, end, coro):
                return i, end, await coro
            batches_yielded = 0
            done = {}
            for logs in asyncio.as_completed([wrap(i, end, coro) for i, (start, end), coro in enumerate(zip(ranges,coros))], timeout=None):
                i, end, logs = await logs
                done[i] = end, logs
                for i in range(len(coros)):
                    if batches_yielded > i:
                        continue
                    if i not in done:
                        break
                    end, logs = done.pop(i)
                    for log in logs:
                        yield log
                    batches_yielded += 1
                    self._lock.set(end)
            done_thru = range_end
            await asyncio.sleep(self.interval)


class Events(Logs):
    __slots__ = '_events', '_event_task'
    def __init__(
        self, 
        *, 
        addresses = [], 
        topics = [], 
        from_block: Optional[int] = None,
        interval: int = 300,
    ):
        super().__init__(addresses=addresses, topics=topics, from_block=from_block, interval=interval)
        self._events = []
    
    def __aiter__(self) -> AsyncIterator[_EventItem]:
        return self.events().__aiter__()

    async def events(self, to_block: int) -> AsyncIterator[_EventItem]:
        if self._event_task is None:
            self._event_task = asyncio.create_task(self._fetch())
        yielded = 0
        done_thru = 0
        while True:
            await self._lock.wait_for(done_thru + 1)
            if self._exc:
                raise self._exc
            for event in self._events[yielded:]:
                block = event.block_number
                if to_block and block > to_block:
                    return
                yield event
                yielded += 1
            done_thru = block

    async def _fetch(self) -> NoReturn:
        try:
            async for log in self.logs():
                decoded = decode_logs([log])
                self._events.extend(decoded)
        except Exception as e:
            self._exc = e
            self._lock.set(BIG_VALUE)

from typing import Callable, TypeVar

T = TypeVar('T')

class ProcessedEvents(Events, AsyncIterator[T]):
    __slots__ = 'event_processor', '_processed_events'
    def __init__(
        self,
        event_processor: Callable[[_EventItem], T],
        *, 
        addresses = [], 
        topics = [], 
        from_block: Optional[int] = None,
    ):
        super().__init__(addresses=addresses, topics=topics, from_block=from_block)
        self._processed_events = []
    
    def __aiter__(self) -> AsyncIterator[_EventItem]:
        return self.events().__aiter__()

    async def processed_events(self, to_block: int) -> AsyncIterator[_EventItem]:
        if self._event_task is None:
            self._event_task = asyncio.create_task(self._fetch())
        yielded = 0
        done_thru = 0
        while True:
            await self._lock.wait_for(done_thru + 1)
            for event in self._processed_events[yielded:]:
                block = event.block_number
                if to_block and block > to_block:
                    return
                yield event
                yielded += 1
            done_thru = block

    async def _fetch(self) -> NoReturn:
        async for log in self.logs():
            decoded = decode_logs([log])
            self._events.extend(decoded)
    