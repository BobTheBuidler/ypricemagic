import logging
from typing import AsyncIterator, List, Optional

import a_sync
import dank_mids
import msgspec.json
import pony.orm
from a_sync import AsyncThreadPoolExecutor, PruningThreadPoolExecutor
from eth_utils.toolz import concat
from evmspec import FilterTrace

from y._db.common import DiskCache, Filter, _clean_addresses
from y._db.decorators import db_session_retry_locked
from y._db.entities import Chain, Trace, TraceCacheInfo, insert
from y._db.utils._ep import _get_get_block
from y.utils.middleware import BATCH_SIZE

logger = logging.getLogger(__name__)
_logger_debug = logger.debug


_trace_executor = PruningThreadPoolExecutor(10, "ypricemagic db executor [trace]")


@a_sync.a_sync(default="async", executor=_trace_executor)
@db_session_retry_locked
def insert_trace(trace: FilterTrace) -> None:
    """Insert a trace into the database.

    This function inserts a given trace into the database by encoding it
    and associating it with the corresponding block and transaction hash.

    Args:
        trace: The trace to be inserted.

    See Also:
        - :func:`y._db.entities.insert`
        - :class:`evmspec.FilterTrace`
    """
    get_block = _get_get_block()
    kwargs = {
        "block": get_block(trace.blockNumber, sync=True),
        "hash": trace.transactionHash,
        "raw": msgspec.json.encode(trace),
    }
    for dct in [trace, *trace.values()]:
        if "from" in dct:
            kwargs["from_address"] = dct["from"]
        if "to" in dct:
            kwargs["to_address"] = dct["to"]
    insert(type=Trace, **kwargs)


class TraceCache(DiskCache[dict, TraceCacheInfo]):
    """Cache for storing and retrieving trace data.

    This class provides methods to load metadata, check cache status,
    select cached traces, and update cache metadata.

    Examples:
        >>> cache = TraceCache(from_addresses=["0x123"], to_addresses=["0x456"])
        >>> cache.load_metadata(chain, "0x123", "0x456")
    """

    __slots__ = "from_addresses", "to_addresses"

    def __init__(self, from_addresses: List[str], to_addresses: List[str]):
        """Initialize TraceCache with cleaned from and to addresses.

        Args:
            from_addresses: List of from addresses to filter traces. These addresses are cleaned and converted.
            to_addresses: List of to addresses to filter traces. These addresses are cleaned and converted.

        Examples:
            >>> cache = TraceCache(from_addresses=["0x123"], to_addresses=["0x456"])
            >>> print(cache.from_addresses)
            ['0x0000000000000000000000000000000000000123']
            >>> print(cache.to_addresses)
            ['0x0000000000000000000000000000000000000456']

        See Also:
            - :func:`y._db.common._clean_addresses`
        """
        self.from_addresses = _clean_addresses(from_addresses)
        self.to_addresses = _clean_addresses(to_addresses)

    def load_metadata(
        self, chain: Chain, from_address: Optional[str], to_address: Optional[str]
    ) -> Optional[TraceCacheInfo]:
        """Load metadata for the given chain and addresses.

        Args:
            chain: The blockchain chain.
            from_address: The from address.
            to_address: The to address.

        Returns:
            The trace cache information if available.

        See Also:
            - :class:`y._db.entities.TraceCacheInfo`
        """
        return TraceCacheInfo.get(
            chain=chain, from_address=str(from_address), to_address=str(to_address)
        )

    def _is_cached_thru(self, from_block: int) -> int:
        """Check if traces are cached through a specific block.

        Args:
            from_block: The starting block number.

        Returns:
            The maximum block number cached.

        See Also:
            - :meth:`y._db.common.DiskCache.is_cached_thru`
        """
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

    def _select(self, from_block: int, to_block: int) -> List[dict]:
        """Select cached traces within a block range.

        Args:
            from_block: The starting block number.
            to_block: The ending block number.

        Returns:
            A list of cached traces.

        See Also:
            - :meth:`y._db.common.DiskCache.select`
        """
        from y._db.utils import utils as db

        return [
            msgspec.json.decode(trace)
            for trace in pony.orm.select(
                trace.raw
                for trace in Trace
                if trace.block.chain == db.get_chain(sync=True)
                and (not self.from_addresses or trace.address in self.from_addresses)
                and (not self.to_addresses or trace.address in self.to_addresses)
                and trace.block.number >= from_block
                and trace.block.number <= to_block
            )
        ]

    def _set_metadata(self, from_block: int, done_thru: int) -> None:
        """Set cache metadata for a block range.

        Args:
            from_block: The starting block number.
            done_thru: The ending block number.

        See Also:
            - :meth:`y._db.common.DiskCache.set_metadata`
        """
        from y._db.utils import utils as db

        chain = db.get_chain(sync=True)
        should_commit = False
        if self.to_addresses and self.from_addresses:
            for from_address in self.from_addresses:
                for to_address in self.to_addresses:
                    if info := TraceCacheInfo.get(
                        chain=chain,
                        from_address=msgspec.json.encode([from_address]),
                        to_address=msgspec.json.encode([to_address]),
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
                            from_address=msgspec.json.encode([from_address]),
                            to_address=msgspec.json.encode([to_address]),
                        )
                        should_commit = True
        elif self.from_addresses:
            for from_address in self.from_addresses:
                if info := TraceCacheInfo.get(
                    chain=chain,
                    from_address=msgspec.json.encode([from_address]),
                    to_address=msgspec.json.encode([]),
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
                        from_address=msgspec.json.encode([from_address]),
                        to_address=msgspec.json.encode([]),
                    )
                    should_commit = True
        elif self.to_addresses:
            for to_address in self.to_addresses:
                if info := TraceCacheInfo.get(
                    chain=chain,
                    from_address=msgspec.json.encode([]),
                    to_address=msgspec.json.encode([to_address]),
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
                        from_address=msgspec.json.encode([]),
                        to_address=msgspec.json.encode([to_address]),
                    )
                    should_commit = True
        elif info := TraceCacheInfo.get(
            chain=chain,
            from_address=msgspec.json.encode([]),
            to_address=msgspec.json.encode([]),
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
                from_address=msgspec.json.encode([]),
                to_address=msgspec.json.encode([]),
            )
            should_commit = True

        if should_commit:
            pony.orm.commit()
            _logger_debug(
                "cached %s %s thru %s",
                self.from_addresses,
                self.to_addresses,
                done_thru,
            )


class TraceFilter(Filter[dict, TraceCache]):
    """Filter for processing and caching traces.

    This class provides methods to filter traces based on from and to addresses,
    and to fetch traces within a specified block range.

    Examples:
        >>> trace_filter = TraceFilter(from_addresses=["0x123"], to_addresses=["0x456"], from_block=100)
        >>> async for trace in trace_filter.traces(to_block=200):
        ...     print(trace)
    """

    insert_to_db = insert_trace
    __slots__ = "from_addresses", "to_addresses"

    def __init__(
        self,
        from_addresses: List[str],
        to_addresses: List[str],
        from_block: int,
        *,
        chunk_size: int = BATCH_SIZE,
        chunks_per_batch: Optional[int] = None,
        semaphore: Optional[dank_mids.BlockSemaphore] = None,
        executor: Optional[AsyncThreadPoolExecutor] = None,
        is_reusable: bool = True,
        verbose: bool = False,
    ):
        """Initialize TraceFilter with addresses and block range.

        Args:
            from_addresses: List of from addresses to filter traces.
            to_addresses: List of to addresses to filter traces.
            from_block: The starting block number.
            chunk_size: The size of each chunk for processing.
            chunks_per_batch: The number of chunks per batch.
            semaphore: Semaphore for controlling concurrency.
            executor: Executor for asynchronous operations.
            is_reusable: Whether the filter is reusable.
            verbose: Whether to enable verbose logging.
        """
        self.from_addresses = from_addresses
        self.to_addresses = to_addresses
        super().__init__(
            from_block,
            chunk_size=chunk_size,
            chunks_per_batch=chunks_per_batch,
            semaphore=semaphore,
            executor=executor,
            is_reusable=is_reusable,
            verbose=verbose,
        )

    @property
    def cache(self) -> TraceCache:
        """Get the trace cache associated with this filter.

        Returns:
            The trace cache.

        See Also:
            - :class:`TraceCache`
        """
        if self._cache is None:
            self._cache = TraceCache(self.from_addresses, self.to_addresses)
        return self._cache

    def traces(self, to_block: Optional[int]) -> AsyncIterator[dict]:
        """Get an asynchronous iterator over traces up to a specified block.

        Args:
            to_block: The ending block number.

        Yields:
            Traces within the specified block range.

        See Also:
            - :meth:`_objects_thru`
        """
        return self._objects_thru(block=to_block)

    async def _fetch_range(self, from_block: int, to_block: int) -> List[dict]:
        """Fetch traces within a block range.

        Args:
            from_block: The starting block number.
            to_block: The ending block number.

        Returns:
            A list of traces within the specified block range.

        Raises:
            NotImplementedError: If the trace fetching method is not implemented.

        See Also:
            - :meth:`dank_mids.web3.provider.make_request`
        """
        try:
            return await dank_mids.web3.provider.make_request("TraceFilter", {})
        except NotImplementedError:
            tasks = a_sync.map(self._trace_block, range(from_block, to_block))
            results = {block: traces async for block, traces in tasks.map()}
            return list(concat(results[i] for i in range(from_block, to_block)))

    async def _trace_block(self, block: int) -> List[dict]:
        """Trace a specific block for transactions.

        Args:
            block: The block number to trace.

        Returns:
            A list of traces for the specified block.

        See Also:
            - :meth:`dank_mids.web3.provider.make_request`
        """
        return [
            trace
            for trace in await dank_mids.web3.provider.make_request("TraceBlock", block)
            if (not self.from_addresses or trace_is_from(self.from_addresses))
            and (not self.to_addresses or trace_is_to(self.to_addresses, trace))
        ]


trace_is_from = lambda addresses, trace: any(
    "from" in x and x["from"] in addresses for x in (trace, trace.values())
)
"""Check if a trace is from any of the specified addresses.

Args:
    addresses: List of addresses to check against.
    trace: The trace to check.

Returns:
    True if the trace is from any of the specified addresses, False otherwise.

Examples:
    >>> trace = {"from": "0x123"}
    >>> trace_is_from(["0x123", "0x456"], trace)
    True
"""

trace_is_to = lambda addresses, trace: any(
    "to" in x and x["to"] in addresses for x in (trace, trace.values())
)
"""Check if a trace is to any of the specified addresses.

Args:
    addresses: List of addresses to check against.
    trace: The trace to check.

Returns:
    True if the trace is to any of the specified addresses, False otherwise.

Examples:
    >>> trace = {"to": "0x456"}
    >>> trace_is_to(["0x123", "0x456"], trace)
    True
"""
