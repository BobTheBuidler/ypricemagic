# ypricemagic Cache & Memory Inventory

## Environment Variables (y/ENVIRONMENT_VARIABLES.py)

| Variable | Default | Description |
|---|---|---|
| `CACHE_TTL` | 3600 (1h) | Global TTL for in-memory caches |
| `CONTRACT_CACHE_TTL` | = CACHE_TTL | TTL for Contract singleton cache |
| `CHECKSUM_CACHE_MAXSIZE` | 100,000 | Max entries in checksum LRU cache |

---

## Complete Cache Inventory

### 1. UNBOUNDED CACHES (can grow forever — highest OOM risk)

#### 1a. `lru_cache(maxsize=None)` — fully unbounded, no eviction

| File | Line | Function/Method | Memory Impact | Notes |
|---|---|---|---|---|
| `y/contracts.py` | 1148 | `_get_explorer_api_key()` | **Low** | Only a handful of unique (url, silent) combos |
| `y/_db/decorators.py` | 121 | `db_session_cached` wrapper | **HIGH** | Wraps any function with `lru_cache(maxsize=None)`. Used by `ensure_block()` in `_db/utils/utils.py` — one entry per block number. Over millions of blocks this is unbounded. |
| `y/_db/structs.py` | 34 | `_make_snake()` | **Low** | Only ~20 unique camelCase keys |
| `y/_db/brownie.py` | 139 | `_get_select_statement()` | **Low** | maxsize=None but only 1 unique call |
| `y/_db/utils/utils.py` | 62 | `@lru_cache` (no args = maxsize=128) | **Low** | Standard default |

#### 1b. `alru_cache(maxsize=None)` — async unbounded

| File | Line | Function/Method | Memory Impact | Notes |
|---|---|---|---|---|
| `y/prices/pendle.py` | 46 | Module-level function | **MEDIUM** | Grows with unique token addresses |
| `y/prices/solidex.py` | 80 | Module-level function | **MEDIUM** | Grows with unique addresses |
| `y/prices/chainlink.py` | 239 | `Feed.scale()` | **Low** | One entry per chainlink feed |

#### 1c. `a_sync(ram_cache_maxsize=None)` — unbounded a_sync caches

| File | Line | Function/Method | Memory Impact | Notes |
|---|---|---|---|---|
| `y/_db/utils/logs.py` | 185 | `get_topic_dbid()` | **Low** | Limited by number of unique event topics |
| `y/_db/utils/token.py` | 85 | `ensure_token()` | **MEDIUM** | Grows with every unique token address |
| `y/_db/utils/utils.py` | 106 | `ensure_block()` (via `db_session_cached` + `a_sync(ram_cache_maxsize=None)`) | **HIGH** | One entry per block number — millions of entries for historical data |
| `y/prices/dex/uniswap/v1.py` | 48 | Method | **MEDIUM** | Grows with unique addresses |
| `y/prices/dex/uniswap/v2.py` | 201 | `UniswapV2Pool.get_token_out()` | **MEDIUM** | Has TTL but no maxsize — grows with pool count |
| `y/prices/dex/uniswap/v2.py` | 695 | `all_pools_for()` | **HIGH** | Caches full pool→token mapping per token_in address, each entry is a dict |

#### 1d. `cache_type="memory"` without maxsize — unbounded a_sync memory caches

| File | Line | Function/Method | Memory Impact | Notes |
|---|---|---|---|---|
| `y/contracts.py` | 215 | `contract_creation_block_async()` | **HIGH** | One entry per contract address queried |
| `y/contracts.py` | 776 | `has_method()` | **HIGH** | Key = (address, method_sig) — very large cardinality |
| `y/contracts.py` | 807 | `has_methods()` | **MEDIUM** | Has TTL (15min) but no maxsize |
| `y/utils/raw_calls.py` | 39 | `_cached_call_fn()` | **HIGH** | Caches any (func, address, block) — cardinality grows with blocks × addresses |
| `y/utils/raw_calls.py` | 67 | `_decimals()` | **MEDIUM** | One per address |
| `y/prices/dex/genericamm.py` | 106 | Method | **MEDIUM** | |
| `y/prices/tokenized_fund/piedao.py` | 19 | Module function | **Low** | |
| `y/prices/lending/aave.py` | 321, 342 | Methods | **MEDIUM** | Two methods, each keyed by (address, block) |
| `y/prices/stable_swap/curve.py` | 650, 672 | Methods | **MEDIUM** | |
| `y/prices/dex/balancer/balancer.py` | 215 | `_get_pool_price()` — TTL=None explicitly | **HIGH** | No eviction at all |
| `y/prices/utils/buckets.py` | 32 | Module function | **Low** | |

---

### 2. BOUNDED CACHES (have maxsize and/or TTL)

#### 2a. `lru_cache` with maxsize

| File | Line | Function/Method | maxsize | Notes |
|---|---|---|---|---|
| `y/convert.py` | 17 | `checksum()` | 100,000 (env) | Critical hot path — monkey-patched globally |
| `y/utils/client.py` | 18 | Function | 1 | Singleton-like |
| `y/_db/utils/_ep.py` | 15, 42 | Two functions | 1 each | Singleton-like |
| `y/_db/utils/token.py` | 102 | `_ensure_token()` | 512 | Reasonable |
| `y/prices/dex/uniswap/v2_forks.py` | 452 | Function | 128 (default) | |

#### 2b. `alru_cache` with maxsize and/or TTL

| File | Line | Function/Method | maxsize | TTL | Notes |
|---|---|---|---|---|---|
| `y/contracts.py` | 1060 | `_extract_abi_data_async()` | 1,000 | 300s | ABI fetching |
| `y/_db/utils/logs.py` | 195 | `get_hash_dbid()` | 10,000 | 600s | Transaction hash DB IDs |
| `y/prices/chainlink.py` | 467 | `Chainlink._get_price()` | 1,000 | CACHE_TTL | |
| `y/utils/client.py` | 50 | Function | 1 | None | Singleton |
| `y/prices/utils/ypriceapi.py` | 104 | Function | 1 | None | Singleton |
| `y/prices/utils/ypriceapi.py` | 124, 142 | Two functions | None (unbounded!) | 10min | **Note: no maxsize** |
| `y/time.py` | 354 | `check_node_async()` | None | 300s | Tiny — always same result |

#### 2c. `ttl_cache` (cachetools.func)

| File | Line | Function/Method | maxsize | TTL | Notes |
|---|---|---|---|---|---|
| `y/contracts.py` | 932 | `_extract_abi_data()` | 1,000 | 1h | Sync ABI fetching |
| `y/time.py` | 332 | `check_node()` | 128 (default) | 300s | |

#### 2d. `@cached(TTLCache(...))` (cachetools)

| File | Line | Function/Method | maxsize | TTL | Notes |
|---|---|---|---|---|---|
| `y/_db/utils/price.py` | 152 | `known_prices_at_block()` | 1,000 | 5min | **Can be large** — each entry is a full dict of address→price for that block |
| `y/_db/utils/contract.py` | 111 | `known_deploy_blocks()` | 1 | 1h | Single snapshot cache |
| `y/_db/utils/token.py` | 411 | `known_tokens()` | 1 | 1h | Single snapshot |
| `y/_db/utils/token.py` | 430 | `known_buckets()` | 1 | 1h | Single snapshot |
| `y/_db/utils/token.py` | 448 | `known_decimals()` | 1 | 1h | Single snapshot |
| `y/_db/utils/token.py` | 468 | `known_symbols()` | 1 | 1h | Single snapshot |
| `y/_db/utils/token.py` | 486 | `known_names()` | 1 | 1h | Single snapshot |

#### 2e. `a_sync(ram_cache_maxsize=N, ram_cache_ttl=...)` — bounded a_sync caches

| File | Line | Function/Method | maxsize | TTL | Notes |
|---|---|---|---|---|---|
| `y/prices/dex/uniswap/v3.py` | 197 | `UniswapV3Pool.check_liquidity()` | 100,000 | 1h | **Large** but bounded |
| `y/prices/dex/uniswap/v3.py` | 248 | `UniswapV3Pool._check_liquidity_token_out()` | 100,000 | 1h | **Large** but bounded |
| `y/prices/dex/uniswap/v3.py` | 605 | `UniswapV3.check_liquidity()` | 100,000 | 1h | **Large** but bounded |
| `y/prices/dex/uniswap/v2.py` | 308 | `UniswapV2Pool.check_liquidity()` | 100,000 | 1h | **Large** but bounded |
| `y/prices/dex/uniswap/v2.py` | 1156 | `UniswapV2Router.check_liquidity()` | 100,000 | 1h | **Large** but bounded |
| `y/prices/dex/uniswap/v2.py` | 1203 | `UniswapV2Router.deepest_pool_for()` | 100,000 | 1h | **Large** but bounded |
| `y/prices/dex/uniswap/v1.py` | 142 | `UniswapV1.check_liquidity()` | 100,000 | 1h | **Large** but bounded |
| `y/prices/stable_swap/curve.py` | 361 | `CurvePool.get_coin_index()` | 10,000 | None | No TTL |
| `y/prices/stable_swap/curve.py` | 448 | `CurvePool.get_balances()` | 5,000 | None | No TTL |
| `y/prices/stable_swap/curve.py` | 546 | `CurvePool.check_liquidity()` | 100,000 | 1h | **Large** |
| `y/prices/dex/balancer/v1.py` | 188 | Method | 10,000 | 10min | |
| `y/prices/dex/balancer/balancer.py` | 160 | Method | None (default) | CACHE_TTL | **No maxsize!** |
| `y/prices/synthetix.py` | 72 | Method | 512 | None | |
| `y/prices/tokenized_fund/tokensets.py` | 107 | Method | 100 | None | |
| `y/prices/lending/aave.py` | 190, 222, 249 | Methods | 256 each | None | |
| `y/prices/lending/compound.py` | 409 | Method | None (default) | 5min | |
| `y/prices/yearn.py` | 233, 321 | Methods | 1,000 each | None | |
| `y/prices/dex/uniswap/v2.py` | 493, 800, 847, 973, 1062 | Methods | 500 each | None | |

#### 2f. `a_sync_ttl_cache` (= `a_sync(ram_cache_ttl=ENVS.CACHE_TTL)` — no maxsize!)

Used in ~20+ locations across the codebase. **Default has TTL=1h but NO maxsize.** This means these caches can grow unbounded within each TTL window:

| File | Usage |
|---|---|
| `y/time.py` | `get_block_timestamp()`, `get_block_timestamp_async()`, `get_block_at_timestamp()` — **HIGH impact: one entry per block** |
| `y/prices/dex/solidly.py` | 2 methods |
| `y/prices/dex/velodrome.py` | 2 methods |
| `y/prices/dex/balancer/v2.py` | 6 methods |
| `y/prices/stable_swap/curve.py` | 1 method |
| `y/prices/stable_swap/stargate.py` | 1 method |
| `y/prices/gearbox.py` | 1 method |
| `y/prices/chainlink.py` | 1 method |
| `y/prices/synthetix.py` | 1 method |
| `y/prices/stable_swap/saddle.py` | 1 function |
| `y/prices/magic.py` | `_get_price()` — **highest cardinality: (token, block)** |

---

### 3. DISK CACHES

| File | Mechanism | Notes |
|---|---|---|
| `y/utils/cache.py` | `joblib.Memory` at `cache/{chain.id}` | Disk-persisted cache for: `contract_creation_block`, `_get_code`, `_get_logs_batch_cached`, `getcode_cache_middleware` |
| `y/utils/cache.py` | `toolcache` (optional) | If installed, disk-caches async functions to `./cache/{chain.id}/{module}/{fn}` |

---

### 4. SINGLETON / INSTANCE CACHES (grow with unique addresses)

| File | Mechanism | Memory Impact | Notes |
|---|---|---|---|
| `y/classes/singleton.py` | `ChecksumASyncSingletonMeta.__instances` dict | **HIGH** | Stores every created singleton instance (ERC20, Contract, UniswapV2Pool, etc.) forever — keyed by address. Two dicts (sync/async). |
| `y/contracts.py` | `Contract` class (extends brownie's `ContractContainer`) | **HIGH** | Contract instances are singletons. Has TTL-based eviction via `_ttl_cache_popper` (default: `CONTRACT_CACHE_TTL` = 1h). Verified contracts are popped after TTL. Unverified ones marked "disabled" (no eviction). |
| `y/contracts.py` | `_contract_locks` (defaultdict of Lock) | **Low** | Cleaned up after use (`pop(address, None)`) |

---

### 5. UNBOUNDED SETS / DICTS (grow-only data structures)

| File | Line | Variable | Memory Impact | Notes |
|---|---|---|---|---|
| `y/convert.py` | 106 | `_is_checksummed: set` | **MEDIUM** | Grows with every unique checksummed address ever seen |
| `y/convert.py` | 107 | `_is_not_checksummed: set` | **MEDIUM** | Grows with every non-checksummed address variant |
| `y/prices/dex/uniswap/v3.py` | 331 | `UniswapV3._pools: dict` | **MEDIUM** | Grows as pools are loaded |
| `y/prices/dex/uniswap/v3.py` | 860 | `UniV3Pools._pools_by_token_cache: DefaultDict[DefaultDict[list]]` | **HIGH** | Nested defaultdict — grows with every (token, block) combo queried |
| `y/prices/stable_swap/stargate.py` | 40-41 | `_factories`, `_factory_pools` dicts | **Low** | Small cardinality |
| `y/prices/gearbox.py` | 79 | `self._dtokens: dict` | **Low** | |
| `y/prices/dex/uniswap/uniswap.py` | 67 | `self.v2_routers = {}` | **Low** | |

---

## Summary: Top OOM Risk Candidates

### Critical (bound these first)

1. **`ensure_block()` in `_db/utils/utils.py`** — `lru_cache(maxsize=None)` + `a_sync(ram_cache_maxsize=None)` — one entry per block number. Processing historical data creates millions of entries.

2. **`a_sync_ttl_cache` used on `get_block_timestamp()` / `get_block_timestamp_async()` in `y/time.py`** — keyed by block number, no maxsize. Historical scans cache millions of timestamps in RAM.

3. **`_get_price()` in `y/prices/magic.py`** — `cache_type="memory"` with TTL but no maxsize. Key is `(token, block)` — extremely high cardinality for historical price lookups.

4. **`contract_creation_block_async()` in `y/contracts.py`** — `cache_type="memory"` with no maxsize or TTL. One entry per unique contract address.

5. **`has_method()` in `y/contracts.py`** — `cache_type="memory"` with no maxsize. Key is `(address, method_signature)` — grows multiplicatively.

6. **`_cached_call_fn()` in `y/utils/raw_calls.py`** — `cache_type="memory"` with no limit. Key is `(func, address, block)` — grows with time.

7. **`ChecksumASyncSingletonMeta.__instances`** — all ERC20, Contract, Pool singletons live forever. No eviction except Contract's TTL popper.

8. **`UniV3Pools._pools_by_token_cache`** — nested defaultdict grows with every (token, block) query.

### High (should bound)

9. **All 100,000-maxsize a_sync caches** in uniswap v2/v3, curve — each can hold 100K entries × ~200-500 bytes = 20-50 MB each. With ~10 such caches, that's 200-500 MB just in liquidity caches.

10. **`all_pools_for()` in uniswap/v2.py** — `ram_cache_maxsize=None`, caches entire pool→token dicts per token.

11. **`_db/utils/price.py` `known_prices_at_block()`** — TTLCache maxsize=1000, but each entry is a full `dict[Address, Decimal]` for that block. 1000 blocks × thousands of prices = very large.

### Medium

12. **`y/convert.py` sets** — `_is_checksummed` and `_is_not_checksummed` — grow with all addresses encountered. Typically tens of thousands of entries.

13. **`_ensure_token()` in _db/utils/token.py** — `lru_cache(maxsize=512)` is fine, but `ensure_token()` wrapper has `ram_cache_maxsize=None`.

### Existing Controls

- `CONTRACT_CACHE_TTL` / `CACHE_TTL` env vars control TTL for many caches
- Contract instances have TTL-based eviction via `_ttl_cache_popper`
- `CHECKSUM_CACHE_MAXSIZE` controls the checksum LRU cache
- Several caches use `ram_cache_ttl` but NO `ram_cache_maxsize`
- **No global cache size monitoring or memory pressure-based eviction exists**

### Recommendations for Bounding

| Cache | Current | Recommended |
|---|---|---|
| `ensure_block()` | maxsize=None | Add `maxsize=500_000` or replace with TTL cache |
| `get_block_timestamp*()` via `a_sync_ttl_cache` | No maxsize | Add `ram_cache_maxsize=500_000` |
| `_get_price()` in magic.py | No maxsize | Add `ram_cache_maxsize=100_000` |
| `contract_creation_block_async()` | No maxsize, no TTL | Add `ram_cache_maxsize=50_000` |
| `has_method()` | No maxsize, no TTL | Add `ram_cache_maxsize=50_000` |
| `_cached_call_fn()` | No maxsize, no TTL | Add `ram_cache_maxsize=50_000, ram_cache_ttl=CACHE_TTL` |
| `all_pools_for()` | maxsize=None | Add `ram_cache_maxsize=10_000` |
| `a_sync_ttl_cache` global decorator | No maxsize | Redefine as `a_sync(ram_cache_maxsize=500_000, ram_cache_ttl=ENVS.CACHE_TTL)` |
| Singleton `__instances` | No eviction | Consider WeakValueDictionary or periodic cleanup |
| `_pools_by_token_cache` | Grows forever | Add LRU eviction or periodic cleanup |
