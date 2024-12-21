from abc import ABCMeta, abstractmethod
from asyncio import Task, create_task, get_event_loop, sleep
from functools import lru_cache
from logging import DEBUG, getLogger
from typing import (
    Any,
    AsyncIterator,
    Awaitable,
    Callable,
    Container,
    Generic,
    List,
    NoReturn,
    Optional,
    Type,
    TypeVar,
    Union,
)

import a_sync
import dank_mids
import eth_retry
from a_sync import (
    ASyncIterable,
    ASyncIterator,
    AsyncThreadPoolExecutor,
    CounterLock,
    PruningThreadPoolExecutor,
)
from async_property import async_property
from brownie import ZERO_ADDRESS
from dank_mids import BlockSemaphore, eth
from evmspec.data import Address, HexBytes32
from hexbytes import HexBytes
from pony.orm import OptimisticCheckError, TransactionIntegrityError, db_session
from web3.datastructures import AttributeDict
from web3.middleware.filter import block_ranges

from y import convert
from y._db.decorators import retry_locked
from y._db.exceptions import CacheNotPopulatedError
from y._decorators import stuck_coro_debugger
from y.exceptions import reraise_excs_with_extra_context
from y.utils.middleware import BATCH_SIZE

T = TypeVar("T")
S = TypeVar("S")
M = TypeVar("M")

logger = getLogger(__name__)
default_filter_threads = PruningThreadPoolExecutor(4)
"""
The thread pool executor used for all :class:`Filter` objects without one provided, with a maximum of 4 threads.
"""


def enc_hook(obj: Any) -> bytes:
    """
    Encode hook for JSON serialization of special types.

    Args:
        obj: The object to encode.

    Raises:
        NotImplementedError: If the object type is not supported for encoding.

    Note:
        Currently supports encoding of :class:`int`, :class:`Address`, :class:`HexBytes32`, :class:`HexBytes`, and :class:`AttributeDict` objects.

    Examples:
        >>> from web3.datastructures import AttributeDict
        >>> enc_hook(AttributeDict({'key': 'value'}))
        {'key': 'value'}

        >>> from hexbytes import HexBytes
        >>> enc_hook(HexBytes('0x1234'))
        '1234'

    See Also:
        - :func:`dec_hook`
    """
    typ = type(obj)
    # sometimes we get a recursion error from the instance checks, this helps us debug that case.
    with reraise_excs_with_extra_context(obj, typ):
        # we use issubclass instead of isinstance here to prevent a recursion error
        if issubclass(typ, int):
            return int(obj)
        elif issubclass(typ, Address):
            return obj[2:]
        elif isinstance(obj, HexBytes32):
            # we trim all leading zeroes since we know how many we need to put back later
            return hex(int(obj.hex(), 16))[2:]
        elif isinstance(obj, HexBytes):
            return bytes(obj).hex()
        elif isinstance(obj, AttributeDict):
            return dict(obj)
        raise TypeError


def dec_hook(typ: Type[T], obj: bytes) -> T:
    """
    Decode hook for JSON deserialization of special types.

    Args:
        typ: The type to decode into.
        obj: The object to decode.

    Raises:
        ValueError: If the type is not supported for decoding.

    Note:
        Currently only supports decoding of :class:`HexBytes` objects.

    Examples:
        >>> from hexbytes import HexBytes
        >>> dec_hook(HexBytes, b'1234')
        HexBytes('0x1234')

    See Also:
        - :func:`enc_hook`
    """
    if typ is HexBytes:
        return typ(obj)
    raise ValueError(f"{typ} is not a valid type for decoding")


class DiskCache(Generic[S, M], metaclass=ABCMeta):
    @abstractmethod
    def _set_metadata(self, from_block: int, done_thru: int) -> None:
        """
        Updates the cache metadata to indicate the cache is populated from block `from_block` to block `to_block`.

        Args:
            from_block: The starting block number.
            done_thru: The ending block number.
        """

    @abstractmethod
    def _is_cached_thru(self, from_block: int) -> int:
        """
        Returns max cached block for this cache or 0 if not cached.

        Args:
            from_block: The starting block number.

        Returns:
            The maximum cached block number.
        """

    @abstractmethod
    def _select(self, from_block: int, to_block: int) -> List[S]:
        """
        Selects all cached objects from block `from_block` to block `to_block`.

        Args:
            from_block: The starting block number.
            to_block: The ending block number.

        Returns:
            A list of cached objects.
        """

    @retry_locked
    def set_metadata(self, from_block: int, done_thru: int) -> None:
        """
        Updates the cache metadata to indicate the cache is populated from block `from_block` to block `to_block`.

        Args:
            from_block: The starting block number.
            done_thru: The ending block number.
        """
        try:
            with db_session:
                self._set_metadata(from_block, done_thru)
        except TransactionIntegrityError as e:
            logger.debug("%s got exc %s when setting cache metadata", self, e)
            self.set_metadata(from_block, done_thru)
        except OptimisticCheckError as e:
            # Don't need to update in this case
            logger.debug("%s got exc %s when setting cache metadata", self, e)

    @db_session
    @retry_locked
    def select(self, from_block: int, to_block: int) -> List[S]:
        """
        Selects all cached objects from block `from_block` to block `to_block`.

        Args:
            from_block: The starting block number.
            to_block: The ending block number.

        Returns:
            A list of cached objects.
        """
        return self._select(from_block, to_block)

    @db_session
    @retry_locked
    def is_cached_thru(self, from_block: int) -> int:
        """
        Returns max cached block for this cache or 0 if not cached.

        Args:
            from_block: The starting block number.

        Returns:
            The maximum cached block number.
        """
        return self._is_cached_thru(from_block)

    @db_session
    @retry_locked
    def check_and_select(self, from_block: int, to_block: int) -> List[S]:
        """
        Selects all cached objects within a specified block range.

        Args:
            from_block: The starting block number.
            to_block: The ending block number.

        Returns:
            A list of cached objects.

        Raises:
            CacheNotPopulatedError: If the cache is not fully populated.
        """
        if self.is_cached_thru(from_block) >= to_block:
            return self.select(from_block, to_block)
        raise CacheNotPopulatedError(self, from_block, to_block)

    __slots__ = []


C = TypeVar("C", bound=DiskCache)


class _DiskCachedMixin(ASyncIterable[T], Generic[T, C], metaclass=ABCMeta):
    __slots__ = "is_reusable", "_cache", "_executor", "_objects", "_pruned"

    def __init__(
        self,
        executor: Optional[AsyncThreadPoolExecutor] = None,
        is_reusable: bool = True,
    ):
        self.is_reusable = is_reusable
        self._cache = None
        self._executor = executor
        self._objects: List[T] = []
        self._pruned = 0

    @property
    @abstractmethod
    def cache(self) -> C: ...

    @property
    def executor(self) -> AsyncThreadPoolExecutor:
        if self._executor is None:
            self._executor = AsyncThreadPoolExecutor(1)
        return self._executor

    def __del__(self) -> None:
        if self._executor:
            self._executor.shutdown()

    @property
    @abstractmethod
    def insert_to_db(self) -> Callable[[T], None]: ...

    # abc.abstractproperty
    def bulk_insert(self) -> Callable[[List[T]], Awaitable[None]]: ...

    async def _extend(self, objs: Container[T]) -> None:
        """
        Override this to pre-process objects before storing.

        Args:
            objs: The objects to extend the list with.
        """
        if objs:
            self._objects.extend(objs)
            if self.is_reusable:
                block = self._get_block_for_obj(self._objects[-1])
                self._checkpoints[block] = len(self._objects)

    def _remove(self, obj: T) -> None:
        self._objects.remove(obj)
        self._pruned += 1

    async def _load_cache(self, from_block: int) -> int:
        """
        Loads cached logs from disk.

        Args:
            from_block: The starting block number.

        Returns:
            The maximum block number loaded from cache.
        """
        logger.debug("checking to see if %s is cached in local db", self)
        if cached_thru := await _metadata_executor.run(
            self.cache.is_cached_thru, from_block
        ):
            logger.info(
                "%s is cached thru block %s, loading from db", self, cached_thru
            )
            await self._extend(
                await self.executor.run(self.cache.select, from_block, cached_thru)
            )
            if self.is_reusable:
                objs_per_chunk = 50
                num_checkpoints = len(self._objects) // objs_per_chunk
                checkpoint_indexes = (
                    i * objs_per_chunk for i in range(1, num_checkpoints)
                )
                for index in checkpoint_indexes:
                    obj = self._objects[index]
                    if index < len(self._objects):
                        next_obj = self._objects[index + 1]
                        while self._get_block_for_obj(obj) == self._get_block_for_obj(
                            next_obj
                        ):
                            obj = next_obj
                            index += 1
                            try:
                                next_obj = self._objects[index + 1]
                            except IndexError:
                                break

                    self._checkpoints[self._get_block_for_obj(obj)] = index

            logger.info(
                "%s loaded %s objects thru block %s from disk",
                self,
                len(self._objects),
                cached_thru,
            )
            return cached_thru
        return None


_E = TypeVar("_E", bound=AsyncThreadPoolExecutor)
_MAX_LONG_LONG = 9223372036854775807

_metadata_executor = PruningThreadPoolExecutor(
    4, thread_name_prefix="ypricemagic Filter metadata"
)


class Filter(_DiskCachedMixin[T, C]):
    # defaults are stored as class vars to keep instance dicts smaller
    _chunk_size = BATCH_SIZE
    _chunks_per_batch = None
    _exc = None
    _db_task = None
    _sleep_fut = None
    _sleep_time = 60
    _task = None
    _depth = 0
    _semaphore = None
    _verbose = False
    __slots__ = (
        "from_block",
        "to_block",
        "_checkpoints",
        "_interval",
        "_lock",
        "__dict__",
        "__weakref__",
    )

    def __init__(
        self,
        from_block: int,
        *,
        chunk_size: int = BATCH_SIZE,
        chunks_per_batch: Optional[int] = None,
        sleep_time: int = 60,
        semaphore: Optional[BlockSemaphore] = None,
        executor: Optional[AsyncThreadPoolExecutor] = None,
        is_reusable: bool = True,
        verbose: bool = False,
    ):
        self.from_block = from_block
        if chunk_size != self._chunk_size:
            self._chunk_size = chunk_size
        if chunks_per_batch != self._chunks_per_batch:
            self._chunks_per_batch = chunks_per_batch
        self._lock = CounterLock(name=str(self))
        if semaphore != self._semaphore:
            self._semaphore = semaphore
        if sleep_time != self._sleep_time:
            self._sleep_time = sleep_time
        if verbose != self._verbose:
            self._verbose = verbose
        self._checkpoints = {}
        super().__init__(executor=executor, is_reusable=is_reusable)

    def __aiter__(self) -> AsyncIterator[T]:
        return self._objects_thru(block=None).__aiter__()

    def __del__(self) -> None:
        if self._task and not self._task.done():
            self._task.cancel()

    @abstractmethod
    async def _fetch_range(self, from_block: int, to_block: int) -> List[T]: ...

    @property
    def semaphore(self) -> BlockSemaphore:
        if self._semaphore is None:
            self._semaphore = BlockSemaphore(self._chunks_per_batch)
        return self._semaphore

    @property
    def is_asleep(self) -> bool:
        return not self._sleep_fut.done() if self._sleep_fut else False

    def _get_block_for_obj(self, obj: T) -> int:
        """
        Override this as needed for different object types.

        Args:
            obj: The object to get the block number for.

        Returns:
            The block number of the object.
        """
        return obj.blockNumber

    @ASyncIterator.wrap
    async def _objects_thru(self, block: Optional[int]) -> AsyncIterator[T]:
        self._ensure_task()
        debug_logs = logger.isEnabledFor(DEBUG)
        yielded = 0
        done_thru = 0
        if self.is_reusable and self._objects:
            if block is None:
                for obj in self._objects:
                    yield obj
                    yielded += 1
                done_thru = self._get_block_for_obj(obj)

            else:
                checkpoint_block = None
                for _block in self._checkpoints:
                    if _block <= block:
                        checkpoint_block = _block
                    else:
                        break

                if checkpoint_block:
                    checkpoint_index = self._checkpoints[checkpoint_block]
                    for obj in self._objects[:checkpoint_index]:
                        yield obj
                        yielded += 1
                    done_thru = self._get_block_for_obj(obj)

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
            if to_yield := self._objects[yielded - self._pruned :]:
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
            if debug_logs:
                logger._log(
                    DEBUG,
                    "%s lock value %s to_block %s",
                    (self, done_thru, block),
                )
            if block is None:
                await sleep(self._sleep_time)

    @async_property
    async def _sleep(self) -> None:
        if self._sleep_fut is None or self._sleep_fut.done():
            self._sleep_fut = get_event_loop().create_future()
        await self._sleep_fut

    def _wakeup(self) -> None:
        self._sleep_fut.set_result(None)

    async def __fetch(self) -> NoReturn:
        try:
            await self._fetch()
        except Exception as e:
            import traceback

            logger.exception(e)
            self._exc = e
            self._tb = e.__traceback__
            # no need to hold vars in memory
            traceback.clear_frames(self._tb)
            self._lock.set(_MAX_LONG_LONG)
            raise

    async def _fetch(self) -> NoReturn:
        """
        Override this if you want.
        """
        await self._loop(self.from_block)

    @stuck_coro_debugger
    async def _fetch_range_wrapped(
        self, i: int, range_start: int, range_end: int, debug_logs: bool
    ) -> List[T]:
        if debug_logs:
            async with self.semaphore[range_end]:
                logger._log(
                    DEBUG,
                    "fetching %s block %s to %s",
                    (self, range_start, range_end),
                )
                return i, range_end, await self._fetch_range(range_start, range_end)
        else:
            async with self.semaphore[range_end]:
                return i, range_end, await self._fetch_range(range_start, range_end)

    async def _loop(self, from_block: int) -> NoReturn:
        logger.debug("starting work loop for %s", self)
        if cached_thru := await self._load_cache(from_block):
            self._lock.set(cached_thru)
        while True:
            await self._load_new_objects(start_from_block=cached_thru or from_block)
            await self._sleep

    @eth_retry.auto_retry
    @stuck_coro_debugger
    async def _load_new_objects(
        self, to_block: Optional[int] = None, start_from_block: Optional[int] = None
    ) -> None:
        SLEEP_TIME = 1

        if debug_logs := logger.isEnabledFor(DEBUG):
            logger._log(DEBUG, "loading new objects for %s", (self,))

        start = (
            v + 1 if (v := self._lock.value) else start_from_block or self.from_block
        )
        if to_block:
            end = to_block
            if start > end:
                raise ValueError(
                    f"start {start} is bigger than end {end}, can't do that"
                )

        elif debug_logs:
            while start > (end := await dank_mids.eth.block_number):
                logger._log(
                    DEBUG,
                    "%s start %s is greater than end %s, sleeping...",
                    (self, start, end),
                )
                await sleep(SLEEP_TIME)

        else:
            while start > (end := await dank_mids.eth.block_number):
                await sleep(SLEEP_TIME)

        await self._load_range(start, end)

    @stuck_coro_debugger
    async def _load_range(self, from_block: int, to_block: int) -> None:
        if debug_logs := logger.isEnabledFor(DEBUG):
            logger._log(DEBUG, "loading block range %s to %s", (from_block, to_block))
        chunks_yielded = 0
        done = {}
        coros = [
            self._fetch_range_wrapped(i, start, end, debug_logs)
            for i, (start, end) in enumerate(
                block_ranges(from_block, to_block, self._chunk_size)
            )
            if self._chunks_per_batch is None or i < self._chunks_per_batch
        ]
        async for i, end, objs in a_sync.as_completed(
            coros, aiter=True, tqdm=self._verbose
        ):
            next_chunk_loaded = False
            done[i] = end, objs
            for i in range(chunks_yielded, len(coros)):
                if i not in done:
                    break
                end, objs = done.pop(i)
                self._insert_chunk(objs, from_block, end, debug_logs)
                await self._extend(objs)
                next_chunk_loaded = True
                chunks_yielded += 1
            if next_chunk_loaded:
                await self._set_lock(end)
                if debug_logs:
                    logger._log(DEBUG, "%s loaded thru block %s", (self, end))

    @stuck_coro_debugger
    async def _set_lock(self, block: int) -> None:
        """
        Override this if you want to, for things like awaiting for tasks to complete as I do in the curve module.

        Args:
            block: The block number to set the lock to.
        """
        self._lock.set(block)

    def _insert_chunk(
        self, objs: List[T], from_block: int, done_thru: int, debug_logs: bool
    ) -> None:

        if prev_task := self._db_task:
            if prev_task.done():
                if e := prev_task.exception():
                    raise e
                prev_task = None

        depth = self._depth
        self._depth += 1

        insert_coro = self.__insert_chunk(
            objs, from_block, done_thru, prev_task, depth, debug_logs
        )

        if debug_logs:
            logger._log(
                DEBUG,
                "%s queuing next db insert chunk %s thru block %s",
                (self, depth, done_thru),
            )
            task = create_task(
                coro=insert_coro,
                name=f"_insert_chunk from {from_block} to {done_thru}",
            )
        else:
            task = create_task(insert_coro)

        task._depth = depth
        self._db_task = task

    def _ensure_task(self) -> None:
        if self._task is None:
            logger.debug("creating task for %s", self)
            self._task = create_task(coro=self.__fetch(), name=f"{self}.__fetch")
            # NOTE: The task does not return and will be cancelled when this object is
            # garbage collected so there is no need to log the "destroy pending task" message.
            self._task._log_destroy_pending = False
        if self._task.done() and (e := self._task.exception()):
            raise e.with_traceback(e.__traceback__)

    async def __insert_chunk(
        self,
        objs: List[T],
        from_block: int,
        done_thru: int,
        prev_chunk_task: Optional[Task],
        depth: int,
        debug_logs: bool,
    ) -> None:
        if prev_chunk_task:
            await prev_chunk_task
        del prev_chunk_task

        if objs:
            await self.bulk_insert(objs)
        del objs

        await _metadata_executor.run(self.cache.set_metadata, from_block, done_thru)
        if debug_logs:
            logger._log(
                DEBUG,
                "%s chunk %s thru block %s is now in db",
                (self, depth, done_thru),
            )


def _clean_addresses(addresses) -> Union[str, List[str]]:
    if addresses == ZERO_ADDRESS:
        raise ValueError("Cannot make a LogFilter for the zero address")
    if not addresses:
        return addresses
    if isinstance(addresses, str):
        return convert.to_address(addresses)
    elif hasattr(addresses, "__iter__"):
        if ZERO_ADDRESS in addresses:
            raise ValueError("Cannot make a LogFilter for the zero address")
        return [convert.to_address(address) for address in addresses]
    return convert.to_address(addresses)
