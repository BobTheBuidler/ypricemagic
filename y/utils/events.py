import abc
import asyncio
import inspect
import logging
import threading
from collections import Counter, defaultdict
from functools import cached_property
from importlib.metadata import version
from itertools import zip_longest
from typing import (TYPE_CHECKING, Any, AsyncGenerator, Awaitable, 
                    Callable, Dict, Iterable, List, NoReturn, Optional, 
                    TypeVar, Union)

import a_sync
import dank_mids
import eth_retry
from a_sync.executor import _AsyncExecutorMixin
from async_property import async_property
from brownie import web3
from brownie.convert.datatypes import EthAddress
from brownie.exceptions import EventLookupError
from brownie.network.event import _EventItem, _add_deployment_topics, _decode_logs, _deployment_topics, EventDict
from eth_typing import ChecksumAddress
from toolz import groupby
from web3.middleware.filter import block_ranges
from web3.types import LogReceipt

from y import ENVIRONMENT_VARIABLES as ENVS
from y._db import structs
from y._db.common import Filter, _clean_addresses
from y.datatypes import Address, Block
from y.utils.cache import memory
from y.utils.middleware import BATCH_SIZE

if TYPE_CHECKING:
    from y._db.utils.logs import LogCache


T = TypeVar('T')

logger = logging.getLogger(__name__)

# not really sure why this breaks things
ETH_EVENT_GTE_1_2_4 = tuple(int(i) for i in version("eth-event").split('.')) >= (1, 2, 4)

def decode_logs(logs: Union[List[LogReceipt], List[structs.Log]]) -> EventDict:
    """
    Decode logs to events and enrich them with additional info.
    """
    from y.contracts import Contract
    for log in logs:
        address = log['address']
        if address not in _deployment_topics:
            _add_deployment_topics(address, Contract(address).abi)
    
    # for some reason < this version can decode them just fine but >= cannot
    special_treatment = ETH_EVENT_GTE_1_2_4 and logs and isinstance(logs[0], structs.Log)
            
    try:
        decoded = _decode_logs([log.to_dict() for log in logs] if special_treatment else logs)
    except Exception:
        decoded = []
        for log in logs:
            try:
                # get some help for debugging
                decoded.extend(_decode_logs([log]))
            except Exception as e:
                raise e.__class__(log, *e.args) from e

    try:
        if logs and isinstance(logs[0], structs.Log):
            for i, log in enumerate(logs):
                # When we load logs from the ydb cache, its faster if we lookup attrs with getattr vs getitem
                setattr(decoded[i], "block_number", log.block_number)
                setattr(decoded[i], "transaction_hash", log.transaction_hash)
                setattr(decoded[i], "log_index", log.log_index)
        else:
            for i, log in enumerate(logs):
                setattr(decoded[i], "block_number", log["blockNumber"])
                setattr(decoded[i], "transaction_hash", log["transactionHash"])
                setattr(decoded[i], "log_index", log["logIndex"])
        return decoded
    except EventLookupError as e:
        raise type(e)(*e.args, len(logs), decoded) from None


@a_sync.a_sync(default='sync')
async def get_logs_asap(
    address: Optional[Address],
    topics: Optional[List[str]],
    from_block: Optional[Block] = None,
    to_block: Optional[Block] = None,
    verbose: int = 0
) -> List[Any]:

    if from_block is None:
        from y.contracts import contract_creation_block_async
        from_block = 0 if address is None else await contract_creation_block_async(address, True)
    if to_block is None:
        to_block = await dank_mids.eth.block_number

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
) -> AsyncGenerator[List[LogReceipt], None]:  # sourcery skip: low-code-quality
    # NOTE: If you don't need the logs in order, you will get your logs faster if you set `chronological` to False.

    if from_block is None:
        from y.contracts import contract_creation_block_async
        if address is None:
            from_block = 0
        elif isinstance(address, Iterable) and not isinstance(address, str):
            from_block = await _lowest_deploy_block(address, when_no_history_return_0=True)
        else:
            from_block = await contract_creation_block_async(address, True)
    if to_block is None:
        to_block = await dank_mids.eth.block_number
    elif run_forever:
        raise TypeError('`to_block` must be None if `run_forever` is True.')
    if from_block > to_block:
        raise ValueError(f"from_block must be <= to_block. You passed from_block: {from_block} to_block: {to_block}.")
    while True:
        ranges = list(block_ranges(from_block, to_block, BATCH_SIZE))
        if verbose > 0:
            logger.info('fetching %d batches', len(ranges))
        coros = [_get_logs_async(address, topics, start, end) for start, end in ranges]
        if chronological:
            yielded = 0
            done = {}
            async for i, result in a_sync.as_completed(dict(enumerate(coros)), aiter=True):
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
        current_block = await dank_mids.eth.block_number
        while current_block <= to_block:
            await asyncio.sleep(run_forever_interval)
            current_block = await dank_mids.eth.block_number
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

@a_sync.a_sync
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
    lambda: dank_mids.BlockSemaphore(
        ENVS.GETLOGS_DOP, 
        # We need to do this in case users use the sync api in a multithread context
        name="y.get_logs" + "" if threading.current_thread() == threading.main_thread() else f".{threading.current_thread()}",
    )
)

async def _get_logs_async(address, topics, start, end) -> List[LogReceipt]:
    async with get_logs_semaphore[asyncio.get_event_loop()][end]:
        return await _get_logs(address, topics, start, end, asynchronous=True)

@eth_retry.auto_retry
async def _get_logs_async_no_cache(address, topics, start, end) -> List[LogReceipt]:
    try:
        if address is None:
            return await dank_mids.eth.get_logs({"topics": topics, "fromBlock": start, "toBlock": end})
        elif topics is None:
            return await dank_mids.eth.get_logs({"address": address, "fromBlock": start, "toBlock": end})
        else:
            return await dank_mids.eth.get_logs({"address": address, "topics": topics, "fromBlock": start, "toBlock": end})
    except Exception as e:
        errs = [
            "Service Unavailable for url:",
            "exceed maximum block range",
            "block range is too wide",
            "request timed out",
            "parse error",
            "method handler crashed",
        ]
        if all(err not in str(e) for err in errs):
            raise
        logger.debug('your node is having trouble, breaking batch in half')
        batch_size = (end - start + 1)
        if batch_size <= 2:
            # breaks the logic below and usually just succeeds on retry anyway
            return await _get_logs_async_no_cache(address, topics, start, end)
        half_of_batch = batch_size // 2
        batch1_end = start + half_of_batch
        batch2_start = batch1_end + 1
        batch1 = await _get_logs_async_no_cache(address, topics, start, batch1_end)
        batch2 = await _get_logs_async_no_cache(address, topics, batch2_start, end)
        response = batch1 + batch2
    return response

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
            "parse error",
            "method handler crashed",
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


class LogFilter(Filter[LogReceipt, "LogCache"]):
    __slots__ = 'addresses', 'topics', 'from_block'
    def __init__(
        self, 
        *, 
        addresses = [], 
        topics = [], 
        from_block: Optional[int] = None,
        chunk_size: int = BATCH_SIZE,
        chunks_per_batch: Optional[int] = None,
        semaphore: Optional[dank_mids.BlockSemaphore] = None,
        executor: Optional[_AsyncExecutorMixin] = None,
        is_reusable: bool = True,
        verbose: bool = False,
    ) -> None:  # sourcery skip: default-mutable-arg
        self.addresses = _clean_addresses(addresses)
        self.topics = topics
        super().__init__(from_block, chunk_size=chunk_size, chunks_per_batch=chunks_per_batch, semaphore=semaphore, executor=executor, is_reusable=is_reusable, verbose=verbose)
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} addresses={self.addresses} topics={self.topics}>"
    
    @property
    def cache(self) -> "LogCache":
        if self._cache is None:
            from y._db.utils.logs import LogCache
            self._cache = LogCache(self.addresses, self.topics)
        return self._cache
    
    @property
    def semaphore(self) -> dank_mids.BlockSemaphore:
        if self._semaphore is None:
            self._semaphore = get_logs_semaphore[asyncio.get_event_loop()]
        return self._semaphore

    def logs(self, to_block: Optional[int]) -> a_sync.ASyncIterator[LogReceipt]:
        return self._objects_thru(block=to_block)

    @property
    def insert_to_db(self) -> Callable[[LogReceipt], None]:
        raise NotImplementedError  # TODO: refactor this out of the base class abc
    
    @cached_property
    def bulk_insert(self) -> Callable[[List[LogReceipt]], Awaitable[None]]:
        from y._db.utils.logs import bulk_insert
        return bulk_insert
    
    @async_property
    async def _from_block(self) -> int:
        if self.from_block is None:
            from y.contracts import contract_creation_block_async
            if self.addresses is None:
                self.from_block = 0
            elif isinstance(self.addresses, Iterable) and not isinstance(self.addresses, str):
                self.from_block = await _lowest_deploy_block(self.addresses, when_no_history_return_0=True)
            else:
                self.from_block = await contract_creation_block_async(self.addresses, when_no_history_return_0=True)
        return self.from_block
    
    async def _fetch_range(self, range_start: int, range_end: int) -> List[LogReceipt]:
        tries = 0
        while True:
            try:
                return await _get_logs_async_no_cache(self.addresses, self.topics, range_start, range_end)
            except ValueError as e:
                if "parse error" not in str(e) or tries >= 50:
                    raise
                tries += 1

    async def _fetch(self) -> NoReturn:
        from_block = await self._from_block
        await self._loop(from_block)


class Events(LogFilter):
    obj_type = _EventItem
    __slots__ = []
    def events(self, to_block: int) -> a_sync.ASyncIterator[_EventItem]:
        return self._objects_thru(block=to_block)
    async def _extend(self, objs) -> None:
        return self._objects.extend(decode_logs(objs))
    def _get_block_for_obj(self, obj: _EventItem) -> int:
        return obj.block_number

class ProcessedEvents(Events, a_sync.ASyncIterable[T]):
    __slots__ = []
    def _include_event(self, event: _EventItem) -> Union[bool, Awaitable[bool]]:
        """Override this to exclude specific events from processing and collection."""
        return True
    @abc.abstractmethod
    def _process_event(self, event: _EventItem) -> T:
        ...
    def objects(self, to_block: int) -> a_sync.ASyncIterator[_EventItem]:
        return self._objects_thru(block=to_block)
    async def _extend(self, logs: List[LogReceipt]) -> None:
        # .items() keeps the input order but yields them as they're ready
        decoded = decode_logs(logs)
        should_include = await asyncio.gather(*[self.__include_event(event) for event in decoded])
        for event, include in zip(decoded, should_include):
            if include:
                self._objects.append(self._process_event(event))
    async def __include_event(self, event: _EventItem) -> bool:
        # sourcery skip: assign-if-exp
        include = self._include_event(event)
        if isinstance(include, bool):
            return include
        if inspect.isawaitable(include):
            return bool(await include)
        return bool(include)

async def _lowest_deploy_block(addresses: Iterable[EthAddress], when_no_history_return_0: bool) -> Block:
    from y.contracts import contract_creation_block_async
    return await a_sync.map(
        contract_creation_block_async, 
        addresses, 
        when_no_history_return_0=when_no_history_return_0,
    ).min(sync=False)
