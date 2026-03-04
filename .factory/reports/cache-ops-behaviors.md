# Cache Operations — User-Visible Behaviors Enumeration

## Sub-feature 1: Amount-based TTL Differentiation on `_get_price`

### Current State (what exists today)

1. **Decorator chain on `_get_price`** (magic.py:581-583):
   ```python
   @stuck_coro_debugger
   @a_sync.a_sync(default="async", cache_type="memory", ram_cache_ttl=ENVS.CACHE_TTL, ram_cache_maxsize=ENVS.PRICE_CACHE_MAXSIZE)
   @__cache
   async def _get_price(token, block, *, fail_to_None, skip_cache, ignore_pools, silent, amount)
   ```
   - The `a_sync` memory cache uses ALL parameters as key, including `amount`.
   - `ram_cache_ttl` = `ENVS.CACHE_TTL` (default: 3600s = 1 hour).
   - `ram_cache_maxsize` = `ENVS.PRICE_CACHE_MAXSIZE` (default: 100,000).
   - This is a single TTL for all entries regardless of whether `amount` is None (spot) or a value (amount-based).

2. **`__cache` disk layer** (magic.py:540-578):
   - Only caches to disk (pony ORM DB) when `amount is None` (spot queries).
   - Amount-based queries (amount != None) skip disk cache entirely.
   - On cache hit from disk, returns early without calling the underlying price function.

3. **Env vars** (ENVIRONMENT_VARIABLES.py):
   - `YPRICEMAGIC_CACHE_TTL`: int, default=3600 — used for in-memory TTL
   - `YPRICEMAGIC_PRICE_CACHE_MAXSIZE`: int, default=100,000 — maxsize for in-memory cache
   - `YPRICEMAGIC_SKIP_CACHE`: bool, default=False — bypass caching entirely
   - No env var exists for amount-specific TTL.

### Proposed Change: VTTLCache Integration

#### What changes

| Aspect | Before | After |
|---|---|---|
| In-memory cache type | `a_sync` built-in LRU+TTL (via `cache_type="memory"`) | `cachebox.VTTLCache` managed by a custom decorator |
| TTL for spot queries (amount=None) | `ENVS.CACHE_TTL` (1 hour) | `ENVS.CACHE_TTL` (1 hour) — unchanged |
| TTL for amount-based queries | Same as spot (1 hour) | `ENVS.AMOUNT_CACHE_TTL` (new env var, shorter) |
| Maxsize | `ENVS.PRICE_CACHE_MAXSIZE` (100,000) | `ENVS.PRICE_CACHE_MAXSIZE` (100,000) — unchanged |
| Decorator chain | `@a_sync.a_sync(cache_type="memory", ...)` | `@a_sync.a_sync(default="async")` + custom `@__vttl_cache` |

#### Behavior: VTTLCache per-key TTL

**Critical API finding**: `cachebox.VTTLCache` (v5.2.2) has per-key TTL via `cache.insert(key, value, ttl=...)`. The `__setitem__` method (`cache[key] = value`) creates entries with **no expiry** (infinite TTL), even if a `ttl` is passed to the constructor. The `@cachebox.cached` decorator uses `__setitem__`, so it **cannot** be used directly with VTTLCache for per-key TTL differentiation. A custom caching wrapper is required.

#### New env var

- **Name**: `YPRICEMAGIC_AMOUNT_CACHE_TTL`
- **Type**: `int` (seconds)
- **Default**: Suggested 300 (5 minutes) — amount-based prices are more volatile since they reflect slippage/liquidity at a point in time
- **Semantics**: TTL applied to in-memory cache entries where `amount is not None`

#### User-visible behaviors to assert

1. **B-VTTL-001**: Spot queries (`amount=None`) are cached in memory with TTL = `ENVS.CACHE_TTL` (default 3600s).
2. **B-VTTL-002**: Amount-based queries (`amount != None`) are cached in memory with TTL = `ENVS.AMOUNT_CACHE_TTL` (default 300s, or chosen value).
3. **B-VTTL-003**: The in-memory cache respects `ENVS.PRICE_CACHE_MAXSIZE` as the maximum number of entries.
4. **B-VTTL-004**: After `AMOUNT_CACHE_TTL` seconds, an amount-based cache entry is evicted; a subsequent call with the same args re-fetches.
5. **B-VTTL-005**: After `CACHE_TTL` seconds, a spot cache entry is evicted; a subsequent call with the same args re-fetches (but may hit disk cache).
6. **B-VTTL-006**: The `__cache` disk layer behavior is unchanged — only spot queries (amount=None) are stored/retrieved from disk.
7. **B-VTTL-007**: `skip_cache=True` bypasses both in-memory and disk cache (existing behavior, must be preserved).
8. **B-VTTL-008**: The `stuck_coro_debugger` decorator is preserved on `_get_price`.
9. **B-VTTL-009**: `YPRICEMAGIC_AMOUNT_CACHE_TTL` env var is declared in `y/ENVIRONMENT_VARIABLES.py` with `verbose=False`.
10. **B-VTTL-010**: Different `(token, block, amount)` tuples produce separate cache entries (cache key includes amount).
11. **B-VTTL-011**: Same `(token, block)` with `amount=None` and `amount=100` are separate cache entries with different TTLs.
12. **B-VTTL-012**: The VTTLCache is thread-safe (cachebox caches are Rust-backed and thread-safe by design).

---

## Sub-feature 2: DB Purge Utility

### Current State

- No purge functionality exists. There is only `delete_sqlite()` in `y/_db/__init__.py` which deletes the entire SQLite file.
- `y/_db/utils/price.py` has `set_price` and `get_price` but no delete operations for Price entities.
- The `Price` entity (entities.py) has:
  - `block`: Required(Block) — Block has `chain`, `number`, `timestamp` (Optional datetime)
  - `token`: Required(Token) — Token inherits from Contract→Address, has `chain` and `address` (str, 42)
  - `price`: Required(Decimal, 38, 18)
  - PrimaryKey is `(block, token)`
- `known_prices_at_block()` is cached with `@cachebox.cached(cachebox.TTLCache(1_000, ttl=5*60))` — this is an in-memory cache of DB-fetched prices per block.

### Proposed Module: `y/_db/utils/purge.py`

#### Function signatures and behaviors

##### 1. `purge_prices_by_token(address: ChecksumAddress) -> int`

| Aspect | Detail |
|---|---|
| What it deletes | All `Price` rows where `token.address == address` and `token.chain.id == CHAINID` |
| Return value | Count of deleted rows |
| Edge cases | |
| — Nonexistent token | Returns 0, no error |
| — Token exists but no prices | Returns 0 |
| — Wrapped gas coin alias | Should handle `constants.EEE_ADDRESS` → `constants.WRAPPED_GAS_COIN` mapping (consistent with `get_price`/`set_price`) |

**Behaviors to assert:**
- **B-PURGE-001**: Deletes all Price rows for the given token address on the current chain.
- **B-PURGE-002**: Returns the count of deleted rows.
- **B-PURGE-003**: Returns 0 for a nonexistent token (no error raised).
- **B-PURGE-004**: Handles EEE_ADDRESS → WRAPPED_GAS_COIN substitution.

##### 2. `purge_prices_by_block_range(start_block: BlockNumber, end_block: BlockNumber) -> int`

| Aspect | Detail |
|---|---|
| What it deletes | All `Price` rows where `block.number >= start_block` and `block.number <= end_block` and `block.chain.id == CHAINID` |
| Return value | Count of deleted rows |
| Edge cases | |
| — start_block > end_block | Should return 0 or raise ValueError (design decision) |
| — Empty range (no prices in range) | Returns 0 |
| — Range with no blocks in DB | Returns 0, no error |
| — Single block (start == end) | Deletes all prices at that one block |

**Behaviors to assert:**
- **B-PURGE-005**: Deletes all Price rows within the inclusive block range on the current chain.
- **B-PURGE-006**: Returns the count of deleted rows.
- **B-PURGE-007**: Returns 0 if no prices exist in the range (no error).
- **B-PURGE-008**: start_block == end_block deletes prices at exactly that block.
- **B-PURGE-009**: start_block > end_block raises ValueError (or returns 0 — pick one).

##### 3. `purge_prices_by_date_range(start_date: datetime, end_date: datetime) -> int`

| Aspect | Detail |
|---|---|
| What it deletes | All `Price` rows where `block.timestamp >= start_date` and `block.timestamp <= end_date` and `block.chain.id == CHAINID` |
| Return value | Count of deleted rows |
| Edge cases | |
| — start_date > end_date | Should return 0 or raise ValueError |
| — Blocks with no timestamp | `Block.timestamp` is `Optional(datetime, lazy=True)` — blocks without timestamps will NOT match and are skipped |
| — Empty date range | Returns 0 |
| — Timezone handling | Design decision: naive datetime vs aware datetime |

**Behaviors to assert:**
- **B-PURGE-010**: Deletes all Price rows whose block timestamp falls within [start_date, end_date] on the current chain.
- **B-PURGE-011**: Returns the count of deleted rows.
- **B-PURGE-012**: Returns 0 if no prices exist in the date range (no error).
- **B-PURGE-013**: Blocks with NULL/missing timestamps are not deleted.
- **B-PURGE-014**: start_date > end_date raises ValueError (or returns 0 — pick one).

#### In-memory cache invalidation on purge

There are **three** in-memory caches that could hold stale data after a purge:

1. **`known_prices_at_block` cache** (`_db/utils/price.py:151`):
   - `@cachebox.cached(cachebox.TTLCache(1_000, ttl=5*60))`
   - Keyed by `block_number`. Returns `dict[ChecksumAddress, Decimal]` for that block.
   - After purging prices for a token or block range, this cache may return stale data for up to 5 minutes.
   - **Invalidation options**:
     - (a) Call `known_prices_at_block.cache_clear()` after purge (blunt but safe)
     - (b) Selectively delete affected keys from `known_prices_at_block.cache` (if the cachebox.cached decorator exposes it)
     - (c) Do nothing — let TTL expire naturally (5 minutes)

2. **`_get_price` a_sync memory cache** (magic.py:582):
   - Currently `a_sync.a_sync(cache_type="memory", ...)` — an internal LRU+TTL cache.
   - After the VTTLCache migration, this would be a VTTLCache instance.
   - Keyed by `(token, block, fail_to_None, skip_cache, ignore_pools, silent, amount)`.
   - **Invalidation**: Harder to access from a DB utility. Options:
     - (a) Expose a `clear_price_cache()` function from magic.py
     - (b) Accept stale in-memory data until TTL expires
     - (c) Document that purge only affects DB; in-memory cache expires naturally

3. **`ProcessingQueue` for `set_price`** (`_db/utils/price.py`):
   - Pending writes in the queue might re-insert purged data.
   - **Mitigation**: Document that purge should be called when no active price fetching is happening, or drain the queue first.

**Behaviors to assert:**
- **B-PURGE-015**: After purge, `known_prices_at_block` cache is invalidated (fully cleared or selectively).
- **B-PURGE-016**: Purge function documents behavior regarding the in-memory `_get_price` cache (either invalidates it or explicitly states it doesn't).
- **B-PURGE-017**: Purge functions use `@db_session` decorator (consistent with existing DB operations in the codebase).
- **B-PURGE-018**: Purge functions use `@retry_locked` decorator (consistent with existing DB write operations).

---

## Testing Considerations

### VTTLCache TTL behavior (without RPC calls)

- **YES, testable without RPC**: Create a VTTLCache, insert entries with different TTLs, `time.sleep()`, verify expiration.
- Pattern from `test_cache_bounds.py:TestTTLCache` already demonstrates this with `cachebox.TTLCache`.
- For VTTLCache, test that `cache.insert(key, val, ttl=short)` expires before `cache.insert(key2, val2, ttl=long)`.

### Suggested test cases

| Test ID | Description | Requires RPC? |
|---|---|---|
| T-VTTL-01 | VTTLCache per-key TTL works: short TTL expires, long TTL persists | No |
| T-VTTL-02 | VTTLCache maxsize eviction works | No |
| T-VTTL-03 | VTTLCache thread safety with concurrent insert/get | No |
| T-VTTL-04 | Custom cache wrapper correctly selects TTL based on amount param | No |
| T-VTTL-05 | `AMOUNT_CACHE_TTL` env var is respected | No (monkeypatch env) |
| T-VTTL-06 | Spot and amount entries with same (token, block) coexist | No |
| T-PURGE-01 | purge_by_token deletes correct rows | No (in-memory SQLite) |
| T-PURGE-02 | purge_by_token returns 0 for nonexistent token | No |
| T-PURGE-03 | purge_by_block_range with valid range | No |
| T-PURGE-04 | purge_by_block_range with empty range | No |
| T-PURGE-05 | purge_by_block_range with inverted range | No |
| T-PURGE-06 | purge_by_date_range with valid range | No |
| T-PURGE-07 | purge_by_date_range skips blocks without timestamp | No |
| T-PURGE-08 | purge invalidates known_prices_at_block cache | No |
| T-PURGE-09 | EEE_ADDRESS → WRAPPED_GAS_COIN substitution in purge | No |

### Important VTTLCache API caveat for tests

`cachebox.VTTLCache.__setitem__` creates entries with **NO expiry** (infinite TTL). Only `cache.insert(key, value, ttl=X)` sets per-key TTL. The `@cachebox.cached` decorator uses `__setitem__`, so it CANNOT be used with VTTLCache for per-key TTL. Tests must verify the custom wrapper uses `insert()`, not `__setitem__`.

---

## Files Involved

| File | Role |
|---|---|
| `y/prices/magic.py` | Replace `a_sync` memory cache with VTTLCache-backed custom decorator |
| `y/ENVIRONMENT_VARIABLES.py` | Add `AMOUNT_CACHE_TTL` env var |
| `y/_cache.py` | Potentially add VTTLCache factory function |
| `y/_db/utils/purge.py` | New module with purge functions |
| `y/_db/utils/price.py` | Cache invalidation hook for `known_prices_at_block` |
| `tests/test_cache_bounds.py` | Extend with VTTLCache and purge tests |
