from abc import ABCMeta, abstractmethod
from asyncio import Task, create_task, get_event_loop, sleep
from copy import copy
from itertools import dropwhile, groupby
from logging import DEBUG, getLogger
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncIterator,
    Awaitable,
    Callable,
    Container,
    Dict,
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
from dank_mids import BlockSemaphore
from evmspec.data import Address, HexBytes32
from hexbytes import HexBytes
from pony.orm import OptimisticCheckError, TransactionIntegrityError, db_session
from web3.datastructures import AttributeDict
from web3.middleware.filter import block_ranges

from y import convert
from y import ENVIRONMENT_VARIABLES as ENVS
from y._db.decorators import retry_locked
from y._db.exceptions import CacheNotPopulatedError
from y._decorators import stuck_coro_debugger
from y.exceptions import reraise_excs_with_extra_context
from y.utils.middleware import BATCH_SIZE

if TYPE_CHECKING:
    from y import Block

T = TypeVar("T")
S = TypeVar("S")
M = TypeVar("M")

Checkpoints = Dict["Block", int]

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

    Example:
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
    def _set_metadata(self, from_block: "Block", done_thru: "Block") -> None:
        """
        Update cache metadata to indicate that the cache is populated from block `from_block` to block `done_thru`.

        Args:
            from_block: The starting block number.
            done_thru: The ending block number indicating that the cache is populated up to this block.

        Example:
            >>> disk_cache._set_metadata(100, 200)

        See Also:
            - :meth:`set_metadata`
        """

    @abstractmethod
    def _is_cached_thru(self, from_block: "Block") -> "Block":
        """
        Returns max cached block for this cache or 0 if not cached.

        Args:
            from_block: The starting block number.

        Returns:
            The maximum cached block number.
        """

    @abstractmethod
    def _select(self, from_block: "Block", to_block: "Block") -> List[S]:
        """
        Selects all cached objects from block `from_block` to block `to_block`.

        Args:
            from_block: The starting block number.
            to_block: The ending block number.

        Returns:
            A list of cached objects.
        """

    @retry_locked
    def set_metadata(self, from_block: "Block", done_thru: "Block") -> None:
        """
        Update cache metadata to indicate that the cache is populated from block `from_block` to block `done_thru`.

        Args:
            from_block: The starting block number.
            done_thru: The ending block number up to which the cache is populated.

        Example:
            >>> cache.set_metadata(100, 200)

        See Also:
            - :meth:`_set_metadata`
            - :class:`CacheNotPopulatedError`
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
    def select(self, from_block: "Block", to_block: "Block") -> List[S]:
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
    def is_cached_thru(self, from_block: "Block") -> "Block":
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
    def check_and_select(self, from_block: "Block", to_block: "Block") -> List[S]:
        """
        Selects all cached objects within a specified block range.

        Args:
            from_block: The starting block number.
            to_block: The ending block number.

        Returns:
            A list of cached objects.

        Raises:
            CacheNotPopulatedError: If the cache is not fully populated.

        Example:
            >>> try:
            ...     data = cache.check_and_select(100, 200)
            ... except CacheNotPopulatedError:
            ...     print("Cache incomplete")

        See Also:
            - :meth:`set_metadata`
            - :meth:`select`
        """
        if self.is_cached_thru(from_block) >= to_block:
            return self.select(from_block, to_block)
        raise CacheNotPopulatedError(self, from_block, to_block)

    __slots__ = []


C = TypeVar("C", bound=DiskCache)


class _DiskCachedMixin(ASyncIterable[T], Generic[T, C], metaclass=ABCMeta):
    """
    Mixin that provides asynchronous features for data caches stored on disk.
    """

    _checkpoints: Checkpoints
    __slots__ = "is_reusable", "_cache", "_executor", "_objects", "_pruned"

    def __init__(
        self,
        executor: Optional[AsyncThreadPoolExecutor] = None,
        is_reusable: bool = True,
    ):
        """
        Initializes the mixin.

        Args:
            executor: Optional executor to use for I/O operations.
            is_reusable: Whether data should be kept in memory for reuse.
        """
        self.is_reusable = is_reusable
        self._cache = None
        self._executor = executor
        self._objects: List[T] = []
        self._pruned = 0

    @property
    @abstractmethod
    def cache(self) -> C:
        """
        Returns the associated cache object, which must be defined in subclasses.
        """

    @property
    def executor(self) -> AsyncThreadPoolExecutor:
        """
        Returns the executor used for disk operations, creating one if necessary.
        """
        executor = self._executor
        if executor is None:
            executor = self._executor = AsyncThreadPoolExecutor(1)
        return executor

    def __del__(self) -> None:
        """
        Shutdown the executor on deletion.
        """
        executor = self._executor
        if executor is not None:
            executor.shutdown()

    @property
    @abstractmethod
    def insert_to_db(self) -> Callable[[T], None]: ...

    def bulk_insert(self) -> Callable[[List[T]], Awaitable[None]]:
        """
        Function to bulk insert a list of objects into the database.

        This property must be overridden in subclasses to provide the desired bulk insertion logic.
        The implementation should return a callable that accepts a list of objects (List[T])
        and returns an awaitable.

        Example:
            >>> async def my_bulk_insert(objs):
            ...     # perform custom bulk insert operations here
            ...     pass
            >>> class MyFilter(_DiskCachedMixin):
            ...     @property
            ...     def bulk_insert(self) -> Callable[[List[T]], Awaitable[None]]:
            ...         return my_bulk_insert

        See Also:
            - :meth:`_load_cache`
        """

    async def _extend(self, objs: Container[T]) -> None:
        """
        Override this to pre-process objects before storing.

        Args:
            objs ("Container[T]"): The objects to extend the list with.

        Example:
            >>> await instance._extend([obj1, obj2])

        See Also:
            - :meth:`_load_cache`
        """
        if objs:
            self._objects.extend(objs)
            if self.is_reusable:
                block = self._get_block_for_obj(self._objects[-1])
                self._checkpoints[block] = len(self._objects)

    async def _load_cache(self, from_block: "Block") -> "Block":
        """
        Loads cached logs from disk.

        Args:
            from_block: The starting block number.

        Returns:
            The maximum block number loaded from cache, or None if no cached data is available.

        Example:
            >>> cached_thru = await instance._load_cache(100)
            >>> if cached_thru is None:
            ...     print("No cached data available")
            ... else:
            ...     print(f"Cache loaded through block {cached_thru}")

        See Also:
            - :meth:`_extend`
        """
        logger.debug("checking to see if %s is cached in local db", self)
        if cached_thru := await _metadata_read_executor.run(self.cache.is_cached_thru, from_block):
            logger.info("%s is cached thru block %s, loading from db", self, cached_thru)
            await self._extend(await self.executor.run(self.cache.select, from_block, cached_thru))
            if self.is_reusable:
                objs_per_chunk = 50
                num_checkpoints = len(self._objects) // objs_per_chunk
                checkpoint_indexes = (i * objs_per_chunk for i in range(1, num_checkpoints))
                get_block_for_obj = self._get_block_for_obj
                for index in checkpoint_indexes:
                    obj = self._objects[index]
                    if index < len(self._objects):
                        next_obj = self._objects[index + 1]
                        while get_block_for_obj(obj) == get_block_for_obj(next_obj):
                            obj = next_obj
                            index += 1
                            try:
                                next_obj = self._objects[index + 1]
                            except IndexError:
                                break

                    self._checkpoints[get_block_for_obj(obj)] = index

            logger.info(
                "%s loaded %s objects thru block %s from disk",
                self,
                len(self._objects),
                cached_thru,
            )
            return cached_thru
        return None


def make_executor(small: int, big: int, name: Optional[str] = None) -> PruningThreadPoolExecutor:
    """
    Creates a thread pool executor that prunes completed tasks.

    Args:
        small: Size of the pool if using a non-postgres DB.
        big: Size of the pool if using a postgres DB.
        name: Optional name for the executor.

    Returns:
        A PruningThreadPoolExecutor instance based on the environment configuration.
    """
    return PruningThreadPoolExecutor(big if ENVS.DB_PROVIDER == "postgres" else small, name)


_E = TypeVar("_E", bound=AsyncThreadPoolExecutor)
_MAX_LONG_LONG = 9223372036854775807

_metadata_read_executor = make_executor(2, 3, "ypricemagic Filter read metadata")
_metadata_write_executor = make_executor(1, 3, "ypricemagic Filter write metadata")


class Filter(_DiskCachedMixin[T, C]):
    # defaults are stored as class vars to keep instance dicts smaller
    _chunk_size = BATCH_SIZE
    _chunks_per_batch = None
    _exc = None
    _tb = None
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
    )

    def __init__(
        self,
        from_block: "Block",
        *,
        chunk_size: int = BATCH_SIZE,
        chunks_per_batch: Optional[int] = None,
        sleep_time: int = 60,
        semaphore: Optional[BlockSemaphore] = None,
        executor: Optional[AsyncThreadPoolExecutor] = None,
        is_reusable: bool = True,
        verbose: bool = False,
    ):
        """
        Initializes the Filter, specifying blocks, concurrency, and caching parameters.

        Args:
            from_block: Earliest block from which data should be retrieved.
            chunk_size: Size of each chunk to retrieve in a single RPC call.
            chunks_per_batch: How many chunks to load per batch (optional).
            sleep_time: Time (in seconds) to sleep between reloads when following chain head.
            semaphore: Block-based semaphore to limit concurrency.
            executor: Executor for disk-related tasks.
            is_reusable: Keeps data in memory if True; data is pruned when False.
            verbose: Enable debug-like progress logging if True.
        """
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
        """
        Returns an async iterator over the stored objects, yielding new ones as they are fetched.
        """
        return self._objects_thru(block=None).__aiter__()

    def __del__(self) -> None:
        """
        Cancels any pending fetch task upon deletion.
        """
        if self._task and not self._task.done():
            self._task.cancel()

    @abstractmethod
    async def _fetch_range(self, from_block: "Block", to_block: "Block") -> List[T]:
        """
        Fetches data for a given range of blocks from an on-chain or remote provider.

        Args:
            from_block: Lower bound of the block range.
            to_block: Upper bound of the block range.

        Returns:
            List of objects for that block range.
        """

    @property
    def semaphore(self) -> BlockSemaphore:
        if self._semaphore is None:
            self._semaphore = BlockSemaphore(self._chunks_per_batch)
        return self._semaphore

    def _get_block_for_obj(self, obj: T) -> "Block":
        """
        Override this as needed for different object types.

        Args:
            obj: The object to get the block number for.

        Returns:
            The block number of the object.

        Example:
            >>> block = instance._get_block_for_obj(some_obj)
        """
        return obj.blockNumber

    @ASyncIterator.wrap
    async def _objects_thru(
        self, block: Optional["Block"], from_block: Optional["Block"] = None
    ) -> AsyncIterator[T]:
        """
        Generates objects up to a specified block, or indefinitely if none is given.

        Args:
            block: Maximum block number to generate objects. If None, yields continuously.
            from_block: Minimum block from which to start yielding objects. Only valid if reusable.

        Yields:
            Objects that fall within the requested block range, if any.
        """
        self._ensure_task()
        debug_logs = logger.isEnabledFor(DEBUG)
        yielded = self._pruned
        done_thru = 0
        get_block_for_obj = self._get_block_for_obj
        if self.is_reusable:
            if from_block:
                reached_from_block = False

                def obj_out_of_range(obj) -> bool:
                    if get_block_for_obj(obj) < from_block:
                        return True
                    nonlocal reached_from_block
                    reached_from_block = True
                    return False

                def skip_too_early(objects):
                    nonlocal yielded
                    if checkpoints := self._checkpoints:
                        start_checkpoint_index = _get_checkpoint_index(from_block, checkpoints)
                        if start_checkpoint_index is not None:
                            objects = objects[start_checkpoint_index:]
                            yielded += start_checkpoint_index
                    start_len = len(objects)
                    objects = tuple(dropwhile(obj_out_of_range, objects))
                    yielded += start_len - len(objs)
                    return objects

            if objs := self._objects:
                if block is None:
                    if from_block:
                        objs = skip_too_early(objs)
                    for obj in objs:
                        yield obj
                    yielded += len(objs)
                    done_thru = get_block_for_obj(obj)
                elif self._checkpoints:
                    checkpoint_index = _get_checkpoint_index(block, self._checkpoints)
                    if checkpoint_index is not None:
                        objs = objs[:checkpoint_index]
                        done_thru = get_block_for_obj(objs[-1])
                        if from_block:
                            objs = skip_too_early(objs)
                        for obj in objs:
                            yield obj
                        yielded += len(objs)

                elif from_block:
                    skip_too_early(objs)

        elif from_block:
            raise RuntimeError(
                f"You cannot pass a value for `from_block` unless the {type(self).__name__} is reusable"
            )

        while True:
            if block is None or done_thru < block:
                self._wakeup()
                await self._lock.wait_for(done_thru + 1)
            if self._exc is not None:
                # raise a copy of it so multiple waiters don't destroy the traceback
                raise self._exc.with_traceback(self._tb) from self._exc.__cause__
            if to_yield := self._objects[yielded - self._pruned :]:
                if from_block and not reached_from_block:
                    objs = skip_too_early(to_yield)
                    if block is None:
                        for obj in objs:
                            yield obj
                    else:
                        for obj in objs:
                            if get_block_for_obj(obj) > block:
                                return
                            yield obj
                    yielded += len(objs)

                elif block:
                    if self.is_reusable:
                        for obj in to_yield:
                            if get_block_for_obj(obj) > block:
                                return
                            yield obj
                        yielded += len(to_yield)
                    else:
                        for obj in to_yield:
                            if get_block_for_obj(obj) > block:
                                self._prune(yielded - self._pruned)
                                return
                            yield obj
                            yielded += 1

                else:
                    for obj in to_yield:
                        yield obj
                    yielded += len(to_yield)

                if not self.is_reusable:
                    self._prune(len(to_yield))

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
        """
        Puts the Filter into a sleep state until `_wakeup` is called. No new requests will be made.
        """
        if self._sleep_fut is None or self._sleep_fut.done():
            self._sleep_fut = get_event_loop().create_future()
        await self._sleep_fut

    def _wakeup(self) -> None:
        """Wake up the Filter to query logs from blocks not yet loaded into memory."""
        if self._sleep_fut is not None:
            self._sleep_fut.set_result(None)
            del self._sleep_fut

    async def __fetch(self) -> NoReturn:
        """
        Main coroutine that continuously runs the internal fetch loop.
        """
        try:
            await self._fetch()
        except Exception as e:
            import traceback

            logger.exception(e)
            self._exc = e
            self._tb = e.__traceback__
            # no need to hold vars in memory
            self._lock.set(_MAX_LONG_LONG)
            raise

    async def _fetch(self) -> NoReturn:
        """
        Defines the main logic for populating the Filter with data. Subclasses can override if needed.

        Example:
            >>> await instance._fetch()

        See Also:
            - :meth:`_loop`
        """
        await self._loop(self.from_block)

    @stuck_coro_debugger
    async def _fetch_range_wrapped(
        self, i: int, range_start: "Block", range_end: "Block", debug_logs: bool
    ) -> List[T]:
        """
        Wraps the _fetch_range call with concurrency control.

        Args:
            i: Index of the chunk or range segment.
            range_start: Lower bound of this block range.
            range_end: Upper bound of this block range.
            debug_logs: Whether debug logging is enabled.

        Returns:
            A tuple containing the index, the ending block, and the fetched objects.
        """
        async with self.semaphore[range_end]:
            if debug_logs:
                logger._log(
                    DEBUG,
                    "fetching %s block %s to %s",
                    (self, range_start, range_end),
                )
            return i, range_end, await self._fetch_range(range_start, range_end)

    async def _loop(self, from_block: "Block") -> NoReturn:
        """
        Work loop that continually fetches new data, loads from cache if available, then sleeps.

        Args:
            from_block: Earliest block from which to begin loading data.
        """
        logger.debug("starting work loop for %s", self)
        if cached_thru := await self._load_cache(from_block):
            self._lock.set(cached_thru)
        while True:
            await self._load_new_objects(start_from_block=cached_thru or from_block)
            await self._sleep

    @eth_retry.auto_retry
    @stuck_coro_debugger
    async def _load_new_objects(
        self,
        to_block: Optional["Block"] = None,
        start_from_block: Optional["Block"] = None,
    ) -> None:
        """
        Asynchronously loads new objects from your RPC, up to an optionally-specified end block.

        Args:
            to_block: Specific block to stop at. If None, load up to the current chain head.
            start_from_block: Block to start from if no prior data is cached.
        """
        SLEEP_TIME = 1

        if debug_logs := logger.isEnabledFor(DEBUG):
            logger._log(DEBUG, "loading new objects for %s", (self,))

        start = v + 1 if (v := self._lock.value) else start_from_block or self.from_block
        if to_block:
            end = to_block
            if start > end:
                raise ValueError(f"start {start} is bigger than end {end}, can't do that")

            while end > (current_block := await dank_mids.eth.block_number):
                logger.warning(
                    "You're trying to query a block range that has not fully completed:\n"
                    "range end: %s  current block: %s  Waiting 1s and trying again...",
                    end,
                    current_block,
                )
                await sleep(5.0)

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

        try:
            await self._load_range(start, end)
        except ValueError as e:
            stre = str(e)
            # we shouldn't experience these errors since we validate our blocks before attempting to load,
            # but some provider load balance between nodes and they might not all be in perfect sync
            retry_on = (
                "One of the blocks specified in filter (fromBlock, toBlock or blockHash) cannot be found.",
                "from block is greater than latest block",
            )
            if any(err in stre for err in retry_on):
                logger.debug("Your rpc might be out of sync, trying again...")
            else:
                raise

    @stuck_coro_debugger
    async def _load_range(self, from_block: "Block", to_block: "Block") -> None:
        """
        Loads a particular block range in chunks, respecting concurrency limits.

        Args:
            from_block: Lower bound of the block range.
            to_block: Upper bound of the block range.
        """
        if debug_logs := logger.isEnabledFor(DEBUG):
            logger._log(DEBUG, "loading block range %s to %s", (from_block, to_block))
        chunks_yielded = 0
        done = {}
        coros = [
            self._fetch_range_wrapped(i, start, end, debug_logs)
            for i, (start, end) in enumerate(block_ranges(from_block, to_block, self._chunk_size))
            if self._chunks_per_batch is None or i < self._chunks_per_batch
        ]
        async for i, end, objs in a_sync.as_completed(coros, aiter=True, tqdm=self._verbose):
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
    async def _set_lock(self, block: "Block") -> None:
        """
        Override this if you want to, for things like awaiting for tasks to complete as I do in the curve module.

        Args:
            block: The block number to set the lock to.

        Example:
            >>> await instance._set_lock(150)

        See Also:
            - :meth:`_load_new_objects`
        """
        self._lock.set(block)

    def _insert_chunk(
        self, objs: List[T], from_block: "Block", done_thru: "Block", debug_logs: bool
    ) -> None:
        """
        Queues the insertion of a chunk of objects into the database, and sets metadata.

        Args:
            objs: List of objects to be inserted.
            from_block: Earliest block in the current overall range.
            done_thru: Block number up to which this chunk completes.
            debug_logs: Whether debug logging is active.
        """
        if prev_task := self._db_task:
            if prev_task.done():
                if e := prev_task.exception():
                    raise e
                prev_task = None

        depth = self._depth
        self._depth += 1

        insert_coro = self.__insert_chunk(objs, from_block, done_thru, prev_task, depth, debug_logs)

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
        """
        Ensures there is a main fetch task running in the background. If not, creates it.
        """
        if self._task is None:
            logger.debug("creating task for %s", self)
            self._task = create_task(coro=self.__fetch(), name=f"{self}.__fetch")
            # NOTE: The task does not return and will be cancelled when this object is
            # garbage collected so there is no need to log the "destroy pending task" message.
            self._task._log_destroy_pending = False
        if self._task.done() and (e := self._task.exception()):
            # copy the exc so the traceback doesn't get destroyed by other waiters
            raise copy(e).with_traceback(e.__traceback__) from e.__cause__

    async def __insert_chunk(
        self,
        objs: List[T],
        from_block: "Block",
        done_thru: "Block",
        prev_chunk_task: Optional[Task],
        depth: int,
        debug_logs: bool,
    ) -> None:
        """
        Inserts the previously fetched chunk into the database, waits on prior tasks if needed.

        Args:
            objs: List of objects to insert.
            from_block: Earliest block for the entire fetch range.
            done_thru: Ending block for this chunk.
            prev_chunk_task: Task that inserted previous chunk, if any.
            depth: Relative ordering of this chunk within the entire fetch.
            debug_logs: Whether debug logs are active.
        """
        if prev_chunk_task:
            await prev_chunk_task
        del prev_chunk_task

        if objs:
            await self.bulk_insert(objs)
        del objs

        await _metadata_write_executor.run(self.cache.set_metadata, from_block, done_thru)
        if debug_logs:
            logger._log(
                DEBUG,
                "%s chunk %s thru block %s is now in db",
                (self, depth, done_thru),
            )

    def _prune(self, count: int) -> None:
        """
        Removes a specified number of objects from the beginning of the in-memory list.

        Args:
            count: Number of objects to remove.
        """
        self._objects = self._objects[count:]
        self._pruned += count


def _clean_addresses(addresses: Union[list, tuple]) -> Union[str, List[str]]:
    """
    Converts addresses into a standardized format, raising an error if the zero address is encountered.

    Args:
        addresses: Single or multiple addresses to clean.

    Returns:
        Cleaned addresses in a consistent string format or a list of such strings.

    Raises:
        ValueError: If the zero address is encountered or if input is invalid.
    """
    if addresses == ZERO_ADDRESS:
        raise ValueError("Cannot make a LogFilter for the zero address")
    if not addresses:
        return addresses
    if isinstance(addresses, str):
        return convert.to_address(addresses)
    elif hasattr(addresses, "__iter__"):
        if ZERO_ADDRESS in addresses:
            raise ValueError("Cannot make a LogFilter for the zero address")
        return list(map(convert.to_address, addresses))
    return convert.to_address(addresses)


def _get_suitable_checkpoint(target_block: "Block", checkpoints: Checkpoints) -> Optional["Block"]:
    """
    Finds a suitable checkpoint block that is less than or equal to a target block.

    Args:
        target_block: The block number used as a reference.
        checkpoints: Dictionary of block -> index.

    Returns:
        Most recent checkpoint block before or equal to the target block, or None if none exist.
    """
    block_lt_checkpoint, group = next(groupby(checkpoints, target_block.__lt__))
    return None if block_lt_checkpoint is True else tuple(group)[-1]


def _get_checkpoint_index(target_block: "Block", checkpoints: Checkpoints) -> Optional[int]:
    """
    Retrieves the index for a checkpoint that is less than or equal to a given block.

    Args:
        target_block: The block number reference.
        checkpoints: Dictionary of block -> index.

    Returns:
        The index of the checkpoint, or None if no suitable checkpoint exists.
    """
    checkpoint_block = _get_suitable_checkpoint(target_block, checkpoints)
    return None if checkpoint_block is None else checkpoints[checkpoint_block]
