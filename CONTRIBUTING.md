
## y.stuck? logger

ypricemagic wraps many long-running async coroutines with `y._decorators.stuck_coro_debugger`, which is a thin wrapper around `a_sync.debugging.stuck_coro_debugger`. That wrapper uses a dedicated logger named `y.stuck?`.

What it does:
- It only runs when the logger is enabled for DEBUG.
- After a coroutine has been running for 5 minutes, it logs `module.function still executing after Xm with args ... kwargs ...` every 5 minutes until completion.

Enable it locally when debugging slow RPCs or stuck price fetches:
```python
import logging

logging.basicConfig(level=logging.INFO)
logging.getLogger("y.stuck?").setLevel(logging.DEBUG)
```

If you add new async RPC or price-fetching functions that might stall, prefer `@stuck_coro_debugger` from `y._decorators` so this logger stays consistent across the codebase.

## a_sync and dank_mids conventions

a_sync:
- Use `@a_sync.a_sync(default="sync")` for user-facing helpers (e.g., `y.prices.magic.get_price/get_prices`, `y.utils.multicall.*`) and `default="async"` for DB/worker functions that run on explicit executors (e.g., `y._db.utils.token`, `y._db.utils.traces`).
- Prefer `a_sync_ttl_cache` from `y.utils.cache` for TTL caching and `@memory.cache` for disk-backed caching. Keep TTLs aligned with `ENVS.CACHE_TTL` unless there is a specific reason.
- Use `@a_sync.aka.property` / `@a_sync.aka.cached_property` for async properties on `ASyncGenericBase`/`ASyncGenericSingleton` classes (e.g., `y.classes.common`, `y.prices.gearbox`, `y.prices.band`).
- Use `cgather`, `igather`, `a_sync.map`, and `a_sync.as_completed` for batching and concurrency (e.g., `y.utils.events`, `y.prices.magic`, `y.utils.multicall`).
- Use a_sync primitives (`ProcessingQueue`, `SmartProcessingQueue`, `ThreadsafeSemaphore`, `AsyncThreadPoolExecutor`, `PruningThreadPoolExecutor`) to keep concurrency bounded and predictable (e.g., `y._db.common`, `y._db.utils.token`, `y.contracts`).

dank_mids:
- `y.contracts.Contract` extends `dank_mids.Contract`. Prefer `.coroutine` for async calls (batched by dank_mids).
- Use `dank_mids.eth` for RPC (block numbers, get_code, get_logs, get_block_timestamp) instead of raw web3 where possible (e.g., `y.time`, `y.utils.events`).
- Use `dank_mids.BlockSemaphore` for block-based throttling (e.g., `y._db.common`, `y.utils.events`, `y.prices.utils.ypriceapi`).
- Keep the checksum monkey patch: `dank_mids.brownie_patch.call.to_checksum_address = y.convert.to_address` (see `y.monkey_patches`).

## Adding new protocols

I will add info to this document over time. For now, it will be sparse. Very sparse.

First thing you want to do when adding support for a new token is determine what is actually is.

Is it a LP token? 

If yes:
    - Check the methods on the LP token. Does it have 'token0', 'token1', and 'getAmountOut'? If yes, it sounds like a uni v2 fork. Look to see if you can find a router address and a factory address for the protocol. Does the router have method 'getAmountsOut' and does the factory emit 'PairCreated' events? If so, you're looking at a uni fork. You should add the factory and router address to y/prices/dex/uniswap/v2_forks.py

If no:
    - I'll write out a process when we get here
