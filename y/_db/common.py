
import abc
import asyncio
import logging
from typing import (Any, AsyncIterator, Callable, Generic, List, NoReturn,
                    Optional, Type, TypeVar, Union)

from a_sync.iter import ASyncIterable
from a_sync.primitives.executor import (PruningThreadPoolExecutor,
                                        _AsyncExecutorMixin)
from a_sync.primitives.locks.counter import CounterLock
from async_property import async_property
from dank_mids.semaphores import BlockSemaphore
from hexbytes import HexBytes
from pony.orm import (OptimisticCheckError, TransactionIntegrityError,
                      db_session)
from tqdm.asyncio import tqdm_asyncio
from web3.datastructures import AttributeDict
from web3.middleware.filter import block_ranges

from y import convert
from y._db.entities import retry_locked
from y._db.exceptions import CacheNotPopulatedError
from y.decorators import stuck_coro_debugger
from y.utils.dank_mids import dank_w3
from y.utils.middleware import BATCH_SIZE

T = TypeVar('T')
S = TypeVar('S')
M = TypeVar('M')

logger = logging.getLogger(__name__)
token_attr_threads = PruningThreadPoolExecutor(32)
filter_threads = PruningThreadPoolExecutor(16)

def enc_hook(obj: Any) -> bytes:
    if isinstance(obj, AttributeDict):
        return dict(obj)
    elif isinstance(obj, HexBytes):
        return obj.hex()
    raise NotImplementedError(obj)

def dec_hook(typ: Type[T], obj: bytes) -> T:
    if typ == HexBytes:
        return HexBytes(obj)
    raise ValueError(f"{typ} is not a valid type for decoding")

class DiskCache(Generic[S, M], metaclass=abc.ABCMeta):
    __slots__ = []
    @abc.abstractmethod
    def _set_metadata(self, from_block: int, done_thru: int) -> None:
        """Updates the cache metadata to indicate the cache is populated from block `from_block` to block `to_block`."""
    @abc.abstractmethod
    def _is_cached_thru(self, from_block: int) -> int:
        """Returns max cached block for this cache or 0 if not cached."""
    @abc.abstractmethod
    def _select(self, from_block: int, to_block: int) -> List[S]:
        """Selects all cached objects from block `from_block` to block `to_block`"""
    @db_session
    @retry_locked
    def set_metadata(self, from_block: int, done_thru: int) -> None:
        """Updates the cache metadata to indicate the cache is populated from block `from_block` to block `to_block`."""
        try:
            return self._set_metadata(from_block, done_thru)
        except (TransactionIntegrityError, OptimisticCheckError):
            return self._set_metadata(from_block, done_thru)
    @db_session
    @retry_locked
    def select(self, from_block: int, to_block: int) -> List[S]:
        """Selects all cached objects from block `from_block` to block `to_block`"""
        return self._select(from_block, to_block)
    @db_session
    @retry_locked
    def is_cached_thru(self, from_block: int) -> int:
        """Returns max cached block for this cache or 0 if not cached."""
        return self._is_cached_thru(from_block)
    def check_and_select(self, from_block: int, to_block: int) -> List[S]:
        """
        Selects all cached objects from block `from_block` to block `to_block` if the cache is fully populated.
        Raises `CacheNotPopulatedError` if it is not.
        """
        if self.is_cached_thru(from_block) >= to_block:
            return self.select(from_block, to_block)
        else:
            raise CacheNotPopulatedError(self, from_block, to_block)

C = TypeVar('C', bound=DiskCache)

class _DiskCachedMixin(Generic[T, C], metaclass=abc.ABCMeta):
    __slots__ = 'is_reusable', '_cache', '_executor', '_objects', '_pruned'
    def __init__(
        self, 
        executor: Optional[_AsyncExecutorMixin] = None,
        is_reusable: bool = True,
    ):
        self.is_reusable = is_reusable
        self._cache = None
        self._executor = executor
        self._objects: List[T] = []
        self._pruned = 0
    @abc.abstractproperty
    def cache(self) -> C:
        ...
    @property
    def executor(self) -> _AsyncExecutorMixin:
        if self._executor is None:
            self._executor = filter_threads
        return self._executor

    @abc.abstractproperty
    def insert_to_db(self) -> Callable[[T], None]:
        ...
    def _extend(self, objs) -> None:
        """Override this to pre-process objects before storing."""
        return self._objects.extend(objs)
    def _remove(self, obj: T) -> None:
        self._objects.remove(obj)
        self._pruned += 1
    async def _load_cache(self, from_block: int) -> int:
        """
        Loads cached logs from disk.
        Returns max block of logs loaded from cache.
        """
        logger.debug('checking to see if %s is cached in local db', self)
        if cached_thru := await self.executor.run(self.cache.is_cached_thru, from_block):
            logger.debug('%s is cached thru block %s, loading from db', self, cached_thru)
            self._extend(await self.executor.run(self.cache.select, from_block, cached_thru))
            if self._objects:
                # TODO: figure out why the log filter with no addresses is busted and then get rid of the if check and do this always
                logger.info('%s loaded %s objects thru block %s from disk', self, len(self._objects), cached_thru)
                return cached_thru
        return None
    
class Filter(ASyncIterable[T], _DiskCachedMixin[T, C]):
    __slots__ = 'from_block', 'to_block', '_chunk_size', '_chunks_per_batch', '_db_task', '_exc', '_interval', '_lock', '_semaphore', '_sleep_fut', '_task', '_verbose'
    def __init__(
        self, 
        from_block: int,
        *, 
        chunk_size: int = BATCH_SIZE, 
        chunks_per_batch: Optional[int] = None,
        semaphore: Optional[BlockSemaphore] = None,
        executor: Optional[_AsyncExecutorMixin] = None,
        is_reusable: bool = True,
        verbose: bool = False,
    ):
        self.from_block = from_block
        self._chunk_size = chunk_size
        self._chunks_per_batch = chunks_per_batch
        self._exc = None
        self._lock = CounterLock()
        self._db_task = None
        self._semaphore = semaphore
        self._sleep_fut = None
        self._task = None
        self._verbose = verbose
        super().__init__(executor=executor, is_reusable=is_reusable)

    def __aiter__(self) -> AsyncIterator[T]:
        return self._objects_thru(block=None).__aiter__()
        
    def __del__(self) -> None:
        if self._task and not self._task.done():
            self._task.cancel()
        
    @abc.abstractmethod
    async def _fetch_range(self, from_block: int, to_block: int) -> List[T]:
        ...
        
    @property
    def semaphore(self) -> BlockSemaphore:
        if self._semaphore is None:
            self._semaphore = BlockSemaphore(self._chunks_per_batch)
        return self._semaphore

    @property
    def is_asleep(self) -> bool:
        return not self._sleep_fut.done() if self._sleep_fut else False
    
    def _get_block_for_obj(self, obj: T) -> int:
        """Override this as needed for different object types"""
        return obj['blockNumber']
    
    async def _objects_thru(self, block: Optional[int]) -> AsyncIterator[T]:
        self._ensure_task()
        yielded = 0
        done_thru = 0
        while True:
            if block is None or done_thru < block:
                if self.is_asleep:
                    self._wakeup()
                await self._lock.wait_for(done_thru + 1)
            if self._exc:
                raise self._exc
            if to_yield := self._objects[yielded-self._pruned:]:
                for obj in to_yield:
                    if block and self._get_block_for_obj(obj) > block:
                        return
                    if not self.is_reusable:
                        self._remove(obj)
                    yield obj
                    yielded += 1
            elif block and done_thru >= block:
                return
            done_thru = self._lock.value
            logger.debug('%s lock value %s to_block %s', self, done_thru, block)

    @async_property  
    async def _sleep(self) -> None:
        if self._sleep_fut is None or self._sleep_fut.done():
            self._sleep_fut = asyncio.get_event_loop().create_future()
        await self._sleep_fut
    
    def _wakeup(self) -> None:
        self._sleep_fut.set_result(None)
    
    async def __fetch(self) -> NoReturn:
        from y.constants import BIG_VALUE
        try:
            await self._fetch()
        except Exception as e:
            logger.exception(e)
            self._exc = e
            self._lock.set(BIG_VALUE)
            raise e
    
    async def _fetch(self) -> NoReturn:
        """Override this if you want"""
        await self._loop(self.from_block)
    
    @stuck_coro_debugger
    async def _fetch_range_wrapped(self, i: int, range_start: int, range_end: int) -> List[T]:
        async with self.semaphore[range_end]:
            logger.debug("fetching %s block %s to %s", self, range_start, range_end)
            return i, range_end, await self._fetch_range(range_start, range_end)

    async def _loop(self, from_block: int) -> NoReturn:
        logger.debug('starting work loop for %s', self)
        if cached_thru := await self._load_cache(from_block):
            self._lock.set(cached_thru)
        while True:
            await self._load_new_objects(start_from_block=cached_thru or from_block)
            await self._sleep
    
    @stuck_coro_debugger
    async def _load_new_objects(self, to_block: Optional[int] = None, start_from_block: Optional[int] = None) -> None:
        logger.debug('loading new objects for %s', self)
        start = v + 1 if (v := self._lock.value) else start_from_block or self.from_block
        if to_block:
            end = to_block
            if start > end:
                raise ValueError(f"start {start} is bigger than end {end}, can't do that")
        else:
            while start > (end := await dank_w3.eth.block_number):
                logger.debug('%s start %s is greater than end %s, sleeping...', self, start, end)
                await asyncio.sleep(1)
        await self._load_range(start, end)

    @stuck_coro_debugger
    async def _load_range(self, from_block: int, to_block: int) -> None:
        logger.debug('loading block range %s to %s', from_block, to_block)
        chunks_yielded = 0
        done = {}
        as_completed = tqdm_asyncio.as_completed if self._verbose else asyncio.as_completed
        coros = [
            self._fetch_range_wrapped(i, start, end) 
            for i, (start, end) 
            in enumerate(block_ranges(from_block, to_block, self._chunk_size))
            if self._chunks_per_batch is None or i < self._chunks_per_batch
        ]
        for objs in as_completed(coros, timeout=None):
            next_chunk_loaded = False
            i, end, objs = await objs
            done[i] = end, objs
            for i in range(chunks_yielded, len(coros)):
                if i not in done:
                    break
                end, objs = done.pop(i)
                self._insert_chunk(objs, from_block, end)
                self._extend(objs)
                next_chunk_loaded = True
                chunks_yielded += 1
            if next_chunk_loaded:
                await self._set_lock(end)
                logger.debug("%s loaded thru block %s", self, end)
    
    @stuck_coro_debugger
    async def _set_lock(self, block: int) -> None:
        """Override this if you want to, for things like awaiting for tasks to complete as I do in the curve module"""
        self._lock.set(block)
    
    def _insert_chunk(self, objs: List[T], from_block: int, done_thru: int) -> None:
        if (prev_task := self._db_task) and prev_task.done() and (e := prev_task.exception()):
            raise e
        depth = prev_task._depth + 1 if prev_task else 0
        logger.debug("%s queuing next db insert chunk %s thru block %s", self, depth, done_thru)
        task = asyncio.create_task(
            coro = self.__insert_chunk([self.executor.run(self.insert_to_db, obj) for obj in objs], from_block, done_thru, prev_task, depth),
            name = f"_insert_chunk from {from_block} to {done_thru}",
        )
        task._depth = depth
        task._prev_task = prev_task
        self._db_task = task

    def _ensure_task(self) -> None:
        if self._task is None:
            logger.debug('creating task for %s', self)
            self._task = asyncio.create_task(coro=self.__fetch(), name=f"{self}.__fetch")
        if self._task.done() and (e := self._task.exception()):
            raise e
        
    @stuck_coro_debugger
    async def __insert_chunk(self, tasks: List[asyncio.Task], from_block: int, done_thru: int, prev_chunk_task: Optional[asyncio.Task], depth: int) -> None:
        if prev_chunk_task:
            await prev_chunk_task
        if tasks:
            await asyncio.gather(*tasks)
        await self.executor.run(self.cache.set_metadata, from_block, done_thru)
        logger.debug("%s chunk %s thru block %s is now in db", self, depth, done_thru)
    
def _clean_addresses(addresses) -> Union[str, List[str]]:
    if not addresses:
        return addresses
    if isinstance(addresses, str):
        return convert.to_address(addresses)
    elif hasattr(addresses, '__iter__'):
        return [convert.to_address(address) for address in addresses]
    return convert.to_address(addresses)