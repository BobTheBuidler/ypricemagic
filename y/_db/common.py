
import abc
import asyncio
import logging
from typing import (Any, AsyncIterator, Awaitable, Callable, Generic, List, NoReturn,
                    Optional, Type, TypeVar, Union)

import a_sync
import dank_mids
import eth_retry
from a_sync.executor import _AsyncExecutorMixin
from async_property import async_property
from brownie import ZERO_ADDRESS
from hexbytes import HexBytes
from pony.orm import (OptimisticCheckError, TransactionIntegrityError,
                      db_session)
from tqdm.asyncio import tqdm_asyncio
from web3.datastructures import AttributeDict
from web3.middleware.filter import block_ranges

from y import convert
from y._db.decorators import retry_locked
from y._db.exceptions import CacheNotPopulatedError
from y._decorators import stuck_coro_debugger
from y.utils.middleware import BATCH_SIZE

T = TypeVar('T')
S = TypeVar('S')
M = TypeVar('M')

logger = logging.getLogger(__name__)
default_filter_threads = a_sync.PruningThreadPoolExecutor(4)

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
    @retry_locked
    def set_metadata(self, from_block: int, done_thru: int) -> None:
        """Updates the cache metadata to indicate the cache is populated from block `from_block` to block `to_block`."""
        try:
            with db_session:
                return self._set_metadata(from_block, done_thru)
        except TransactionIntegrityError as e:
            logger.debug("%s got exc %s when setting cache metadata", self, e)
            return self.set_metadata(from_block, done_thru)
        except OptimisticCheckError as e:
            # Don't need to update in this case
            logger.debug("%s got exc %s when setting cache metadata", self, e)
        
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

class _DiskCachedMixin(a_sync.ASyncIterable[T], Generic[T, C], metaclass=abc.ABCMeta):
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
            self._executor = default_filter_threads
        return self._executor

    @abc.abstractproperty
    def insert_to_db(self) -> Callable[[T], None]:
        ...
    
    #abc.abstractproperty
    def bulk_insert(self) -> Callable[[List[T]], Awaitable[None]]:
        ...
        
    async def _extend(self, objs) -> None:
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
            await self._extend(await self.executor.run(self.cache.select, from_block, cached_thru))
            logger.debug('%s loaded %s objects thru block %s from disk', self, len(self._objects), cached_thru)
            return cached_thru
        return None

_E = TypeVar("_E", bound=_AsyncExecutorMixin)
    
class Filter(_DiskCachedMixin[T, C]):
    # defaults are stored as class vars to keep instance dicts smaller
    _chunk_size = BATCH_SIZE
    _chunks_per_batch = None
    _exc = None
    _db_task = None
    _sleep_fut = None
    _sleep_time = 60
    _task = None
    _semaphore = None
    _verbose = False
    __slots__ = 'from_block', 'to_block', '_interval', '_lock', '__dict__', '__weakref__'
    def __init__(
        self, 
        from_block: int,
        *, 
        chunk_size: int = BATCH_SIZE, 
        chunks_per_batch: Optional[int] = None,
        sleep_time: int = 60,
        semaphore: Optional[dank_mids.BlockSemaphore] = None,
        executor: Optional[_AsyncExecutorMixin] = None,
        is_reusable: bool = True,
        verbose: bool = False,
    ):
        self.from_block = from_block
        if chunk_size != self._chunk_size:
            self._chunk_size = chunk_size
        if chunks_per_batch != self._chunks_per_batch:
            self._chunks_per_batch = chunks_per_batch
        self._lock = a_sync.CounterLock()
        if semaphore != self._semaphore:
            self._semaphore = semaphore
        if sleep_time != self._sleep_time:
            self._sleep_time = sleep_time
        if verbose != self._verbose:
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
    def semaphore(self) -> dank_mids.BlockSemaphore:
        if self._semaphore is None:
            self._semaphore = dank_mids.BlockSemaphore(self._chunks_per_batch)
        return self._semaphore

    @property
    def is_asleep(self) -> bool:
        return not self._sleep_fut.done() if self._sleep_fut else False
    
    def _get_block_for_obj(self, obj: T) -> int:
        """Override this as needed for different object types"""
        return obj['blockNumber']
    
    @a_sync.ASyncIterator.wrap
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
                # create a new duplicate exc instead of building a massive traceback on the original
                try:
                    raise type(self._exc)(*self._exc.args).with_traceback(self._tb)
                except TypeError:
                    raise self._exc.with_traceback(self._tb) from None
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
            if block is None:
                await asyncio.sleep(self._sleep_time)

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
            import traceback
            logger.exception(e)
            self._exc = e
            self._tb = e.__traceback__
            # no need to hold vars in memory
            traceback.clear_frames(self._tb)
            self._lock.set(BIG_VALUE)
            raise
    
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
    
    @eth_retry.auto_retry
    @stuck_coro_debugger
    async def _load_new_objects(self, to_block: Optional[int] = None, start_from_block: Optional[int] = None) -> None:
        logger.debug('loading new objects for %s', self)
        start = v + 1 if (v := self._lock.value) else start_from_block or self.from_block
        if to_block:
            end = to_block
            if start > end:
                raise ValueError(f"start {start} is bigger than end {end}, can't do that")
        else:
            while start > (end := await dank_mids.eth.block_number):
                logger.debug('%s start %s is greater than end %s, sleeping...', self, start, end)
                await asyncio.sleep(1)
        await self._load_range(start, end)

    @stuck_coro_debugger
    async def _load_range(self, from_block: int, to_block: int) -> None:
        logger.debug('loading block range %s to %s', from_block, to_block)
        chunks_yielded = 0
        done = {}
        coros = [
            self._fetch_range_wrapped(i, start, end) 
            for i, (start, end) 
            in enumerate(block_ranges(from_block, to_block, self._chunk_size))
            if self._chunks_per_batch is None or i < self._chunks_per_batch
        ]
        async for i, end, objs in a_sync.as_completed(coros, aiter=True, tqdm=self._verbose):
            next_chunk_loaded = False
            done[i] = end, objs
            for i in range(chunks_yielded, len(coros)):
                if i not in done:
                    break
                end, objs = done.pop(i)
                self._insert_chunk(objs, from_block, end)
                await self._extend(objs)
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
            coro = self.__insert_chunk(objs, from_block, done_thru, prev_task, depth),
            name = f"_insert_chunk from {from_block} to {done_thru}",
        )
        task._depth = depth
        task._prev_task = prev_task
        self._db_task = task

    def _ensure_task(self) -> None:
        if self._task is None:
            logger.debug('creating task for %s', self)
            self._task = asyncio.create_task(coro=self.__fetch(), name=f"{self}.__fetch")
            # NOTE: The task does not return and will be cancelled when this object is 
            # garbage collected so there is no need to log the "destroy pending task" message.
            self._task._log_destroy_pending = False
        if self._task.done() and (e := self._task.exception()):
            raise e.with_traceback(e.__traceback__)
        
    @stuck_coro_debugger
    async def __insert_chunk(self, objs: List[T], from_block: int, done_thru: int, prev_chunk_task: Optional[asyncio.Task], depth: int) -> None:
        if prev_chunk_task:
            await prev_chunk_task
        if objs:
            await self.bulk_insert(objs, executor=self.executor)
        await self.executor.run(self.cache.set_metadata, from_block, done_thru)
        logger.debug("%s chunk %s thru block %s is now in db", self, depth, done_thru)
    
def _clean_addresses(addresses) -> Union[str, List[str]]:
    if addresses == ZERO_ADDRESS:
        raise ValueError("Cannot make a LogFilter for the zero address")
    if not addresses:
        return addresses
    if isinstance(addresses, str):
        return convert.to_address(addresses)
    elif hasattr(addresses, '__iter__'):
        if ZERO_ADDRESS in addresses:
            raise ValueError("Cannot make a LogFilter for the zero address")
        return [convert.to_address(address) for address in addresses]
    return convert.to_address(addresses)