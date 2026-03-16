# Architecture

## Pool Loading Pipeline

### V2 (y/prices/dex/uniswap/v2.py)
- `UniswapRouterV2.pools` — cached_property that creates `PoolsFromEvents` (is_reusable=True) and loads all PairCreated events via continuous polling. Events task is NOT cancelled after initial load — polling continues indefinitely.
- `PoolsFromEvents` extends `ProcessedEvents` — event scanning + SQLite persistence via PonyORM. `is_reusable=True` means the iterable is not exhausted after initial load.
- `__pools__` — HiddenMethodDescriptor, async accessor for `pools`
- `_pool_index` — `@a_sync.aka.cached_property` that builds `token_address -> {pool: other_token}` dict from `pools_obj._objects` at zero RPC cost. Access `pools_obj._objects` (private list on `_DiskCachedMixin`) to get all loaded pool objects.
- `all_pools_for(token)` — O(1) dict lookup into `_pool_index`. ram_cache decorator removed (index IS the cache and must stay fresh for continuous discovery).
- `get_pools_for(token, block)` — uses index as sole lookup mechanism (get_pools_via_factory_getpair removed). Exception: on chains where `_supports_factory_helper=True`, the factory helper is tried first and returns early on success.
- Background task `_update_index_from_new_pools` — runs continuously via `asyncio.ensure_future()`, polls every **30 seconds** for new pools added to `pools_obj._objects` and adds them to `_pool_index` under both token0 and token1.
- `get_pools_via_factory_getpair()` — **REMOVED** (superseded by the index)
- WETH special case retained: `pools_for_token()` returns only the WETH/USDC pool on Mainnet (not all thousands of WETH pools) for performance. Documented in code comments.

### V3 (y/prices/dex/uniswap/v3.py)
- `UniswapV3.pools` — cached_property returning UniV3Pools instance
- `UniV3Pools` extends `ProcessedEvents` — continuously polls PoolCreated events via _loop()
- `pools_for_token(token, block)` — iterates all pools checking `token in pool`, uses `_BoundedPoolsByTokenCache` (LRU) for caching
- `_BoundedPoolsByTokenCache` — cachebox.LRUCache wrapping token → {deploy_block: [pools]}

### Persistence
- Raw event logs stored in SQLite (PonyORM `Log` table) as msgpack bytes
- `LogCacheInfo` tracks cached_from/cached_thru block numbers
- Pool objects are NOT persisted — decoded from raw logs on restart
- Token0/token1 cached in RAM after pool loading (from event data or RPC call)

### Key Constants
- STABLECOINS: ~5 on mainnet (USDC, USDT, DAI, etc.)
- WRAPPED_GAS_COIN: WETH on mainnet
- ROUTING_TOKENS: ~4 on mainnet (overlap with stablecoins)
- After dedup, ~6 unique candidates for getPair
