
import abc
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import (Any, AsyncIterator, AsyncIterable, Callable, Generic, Iterator, List,
                    NoReturn, Optional, Type, TypeVar)

from a_sync.primitives.locks.counter import CounterLock
from dank_mids.semaphores import BlockSemaphore
from hexbytes import HexBytes
from tqdm.asyncio import tqdm_asyncio
from web3.datastructures import AttributeDict
from web3.middleware.filter import block_ranges

from y._db.exceptions import CacheNotPopulatedError
from y.constants import BIG_VALUE, thread_pool_executor
from y.utils.dank_mids import dank_w3

T = TypeVar('T')
S = TypeVar('S')
M = TypeVar('M')

logger = logging.getLogger(__name__)
executor = ThreadPoolExecutor(16)

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
    def set_metadata(self, from_block: int, done_thru: int) -> None:
        """Updates the cache metadata to indicate the cache is populated from block `from_block` to block `to_block`."""
    @abc.abstractmethod
    def is_cached_thru(self, from_block: int) -> int:
        """Returns max cached block for this cache or 0 if not cached."""
    @abc.abstractmethod
    def select(self, from_block: int, to_block: int) -> List[S]:
        """Selects all cached objects from block `from_block` to block `to_block`"""
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
    __slots__ = '_cache', '__objects'
    def __init__(self):
        self._cache = None
        self.__objects: List[T] = []
    @abc.abstractproperty
    def cache(self) -> C:
        ...
    
    async def _load_cache(self, from_block: int) -> int:
        """
        Loads cached logs from disk.
        Returns max block of logs loaded from cache.
        """
        if cached_thru := await thread_pool_executor.run(self.cache.is_cached_thru, from_block):
            self.__objects.extend(await thread_pool_executor.run(self.cache.select, from_block, cached_thru))
            logger.info('%s loaded %s objects thru block %s from disk', self, len(self.__objects), cached_thru)
            return cached_thru
        return from_block - 1

class ASyncIterable(AsyncIterable[T]):
    """An iterable that can be used in both a `for` loop and an `async for` loop."""
    def __iter__(self) -> Iterator[T]:
        return self.__sync_iterator()
    def __sync_iterator(self) -> Iterator[T]:
        aiterator = self.__aiter__()
        while True:
            try:
                yield asyncio.get_event_loop().run_until_complete(aiterator.__anext__())
            except StopAsyncIteration as e:
                raise StopIteration(*e.args) from e

class ASyncIterator(ASyncIterable[T]):
    """An iterator that can be used in both a `for` loop and an `async for` loop."""
    def __next__(self) -> T:
        return asyncio.get_event_loop().run_until_complete(self.__anext__())

class ASyncWrappedIterable(ASyncIterable[T]):
    def __init__(self, async_iterable: AsyncIterable[T]):
        self.__iterable = async_iterable.__aiter__()
    def __aiter__(self) -> AsyncIterable[T]:
        return self.__iterable
    
class ASyncWrappedIterator(ASyncWrappedIterable[T], ASyncIterator[T]):
    async def __anext__(self) -> T:
        return await self.__iterable.__anext__()
    
class Filter(ASyncIterable[T], _DiskCachedMixin[T, C]):
    __slots__ = 'from_block', 'to_block', '_batch_size', '_exc', '_interval', '_lock', '_semaphore', '_task', '_verbose'
    def __init__(
        self, 
        from_block: int,
        *, 
        batch_size: int = 1_000, 
        interval: int = 300, 
        semaphore: Optional[BlockSemaphore] = 32, 
        verbose: bool = False,
    ):
        self.from_block = from_block
        self._batch_size = batch_size
        self._exc = None
        self._interval = interval
        self._lock = CounterLock()
        self._semaphore = semaphore
        self._task = None
        self._verbose = verbose
        super().__init__()

    def __aiter__(self) -> AsyncIterator[T]:
        return self._objects_thru(block=None).__aiter__()
        
    @abc.abstractmethod
    async def _fetch_range(self, from_block: int, to_block: int) -> List[T]:
        ...
    @abc.abstractproperty
    def _db_insert_fn(self) -> Callable[[T], None]:
        ...
        
    @property
    def semaphore(self) -> BlockSemaphore:
        if isinstance(self._semaphore, int):
            self._semaphore = BlockSemaphore(self._semaphore)
        return self._semaphore
            
    async def _objects_thru(self, block: Optional[int]) -> AsyncIterator[T]:
        self._ensure_task()
        yielded = 0
        done_thru = 0
        while True:
            if block and done_thru < block:
                await self._lock.wait_for(done_thru + 1)
            if self._exc:
                raise self._exc
            for obj in self.__objects[yielded:]:
                if block and obj['blockNumber'] > block:
                    return
                yield obj
                yielded += 1
            done_thru = self._lock.value
    
    async def _fetch(self) -> NoReturn:
        try:
            await self.__fetch(self.from_block)
        except Exception as e:
            self._exc = e
            self._lock.set(BIG_VALUE)
    
    async def __fetch(self) -> NoReturn:
        """Override this if you want"""
        await self.__loop(self, self.from_block)
    
    async def _fetch_range_wrapped(self, i: int, range_start: int, range_end: int) -> List[T]:
        async with self.semaphore[range_end]:
            return i, range_end, await self._fetch_range(range_start, range_end)

    async def __loop(self, from_block: int) -> NoReturn:
        self._lock.set(await self._load_cache(from_block))
        while True:
            await self._load_new_objects()
            await asyncio.sleep(self._interval)
    
    async def _load_new_objects(self, to_block: Optional[int] = None) -> None:
        await self._load_range(self._lock.value + 1, to_block or await dank_w3.eth.block_number)

    async def _load_range(self, from_block: int, to_block: int) -> None:
        db_insert_tasks = []
        cache_info_tasks = []
        batches_yielded = 0
        done = {}
        as_completed = tqdm_asyncio.as_completed if self._verbose else asyncio.as_completed
        coros = [
            self._fetch_range_wrapped(i, start, end) 
            for i, (start, end) 
            in enumerate(block_ranges(from_block, to_block, self._batch_size))
        ]
        for objs in as_completed(coros, timeout=None):
            i, end, objs = await objs
            done[i] = end, objs
            for i in range(len(coros)):
                if batches_yielded > i:
                    continue
                if i not in done:
                    if db_insert_tasks:
                        await asyncio.gather(*db_insert_tasks)
                        db_insert_tasks.clear()
                    if cache_info_tasks:
                        await cache_info_tasks[-1]
                        cache_info_tasks.clear()
                    break
                end, objs = done.pop(i)
                self._extend(objs)
                db_insert_tasks.extend(thread_pool_executor.submit(self._db_insert_fn, obj) for obj in objs)
                cache_info_tasks.append(thread_pool_executor.submit(self.cache.set_metadata, from_block, end))
                batches_yielded += 1
                self._lock.set(end)

    def _ensure_task(self) -> None:
        if self._task is None:
            self._task = asyncio.create_task(self._fetch())
    
    def _extend(self, objs) -> None:
        return self.__objects.extend(objs)