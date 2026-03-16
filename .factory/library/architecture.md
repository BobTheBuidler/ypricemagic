# Architecture

## Pool Loading Pipeline

### V2 (y/prices/dex/uniswap/v2.py)
- `UniswapRouterV2.pools` — cached_property that creates `PoolsFromEvents`, loads all PairCreated events, gap-fills with `factory.allPairs.map()`, then cancels the events task
- `PoolsFromEvents` extends `ProcessedEvents` — event scanning + SQLite persistence via PonyORM
- `__pools__` — HiddenMethodDescriptor, async accessor for `pools`
- `all_pools_for(token)` — iterates `__pools__` checking token0/token1. Has ram_cache decorator
- `get_pools_via_factory_getpair(token, block)` — O(1) factory.getPair for ~6 well-known candidates
- `get_pools_for(token, block)` — tries FACTORY_HELPER first, then getPair fast path, then falls back to all_pools_for

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
