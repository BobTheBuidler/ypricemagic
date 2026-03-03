# Validation Contract Review — Cache Bounding Mission

## 1. Missing Assertions

### MISSING-001: `_get_price()` in `y/prices/magic.py` — highest cardinality cache
The #1 OOM risk in the inventory. Keyed by `(token, block)` — extremely high cardinality for historical lookups. Uses `cache_type="memory", ram_cache_ttl=ENVS.CACHE_TTL` with no maxsize. VAL-BOUND-001 covers it generically, but this is the single most dangerous cache and warrants its own assertion.

**Proposed assertion:**
> ### VAL-BOUND-008: _get_price cache bounded
> The `_get_price()` function's cache in `y/prices/magic.py` (previously `cache_type="memory"` with TTL but no maxsize) has a finite `ram_cache_maxsize` limit appropriate for its `(token, block)` key cardinality.
> Evidence: terminal output (inspect code, verify ram_cache_maxsize is set and ≤ 100,000)

### MISSING-002: `get_block_timestamp()` / `get_block_timestamp_async()` in `y/time.py`
The #2 OOM risk. Uses `@a_sync_ttl_cache` which has TTL=1h but NO maxsize. Keyed by block number — millions of entries during historical scans. VAL-INFRA-002 partially covers this (a_sync_ttl_cache gets a default maxsize), but these critical functions need explicit verification.

**Proposed assertion:**
> ### VAL-BOUND-009: Block timestamp caches bounded
> The `get_block_timestamp()`, `get_block_timestamp_async()`, and `get_block_at_timestamp()` caches in `y/time.py` (via `a_sync_ttl_cache`) have a finite maxsize. Each was previously unbounded with block-number keys (millions of possible entries).
> Evidence: terminal output (inspect code, verify maxsize present on all three)

### MISSING-003: `db_session_cached` decorator in `y/_db/decorators.py`
This is a decorator factory that wraps any function with `lru_cache(maxsize=None)`. It's the mechanism that makes `ensure_block()` unbounded. VAL-BOUND-004 covers `ensure_block` specifically, but `db_session_cached` itself needs to be migrated to prevent any current or future function wrapped by it from being unbounded.

**Proposed assertion:**
> ### VAL-MIG-006: db_session_cached wrapper migrated
> The `db_session_cached` wrapper in `y/_db/decorators.py` no longer uses `lru_cache(maxsize=None)`. It uses a bounded cachebox cache or equivalent bounded mechanism, so all functions decorated with it inherit a finite maxsize.
> Evidence: terminal output (read `_db/decorators.py`, verify no `lru_cache(maxsize=None)`)

### MISSING-004: `all_pools_for()` in `y/prices/dex/uniswap/v2.py`
Explicitly `ram_cache_maxsize=None`, HIGH memory impact. Caches full `dict[UniswapV2Pool, Address]` per `token_in`. Each entry is a dict, so memory per entry is large.

**Proposed assertion:**
> ### VAL-BOUND-010: all_pools_for cache bounded
> The `all_pools_for()` method in `y/prices/dex/uniswap/v2.py` (previously `ram_cache_maxsize=None`) has a finite maxsize.
> Evidence: terminal output (inspect code, verify `ram_cache_maxsize` is set)

### MISSING-005: `ensure_token()` in `y/_db/utils/token.py`
Has `ram_cache_maxsize=None` on the a_sync wrapper at line 85. MEDIUM impact — grows with every unique token address. The inner `_ensure_token()` is bounded (maxsize=512) but the outer a_sync cache is unbounded.

**Proposed assertion:**
> ### VAL-BOUND-011: ensure_token a_sync cache bounded
> The `ensure_token()` function in `y/_db/utils/token.py` (previously `ram_cache_maxsize=None` on its `@a_sync` decorator) has a finite `ram_cache_maxsize`.
> Evidence: terminal output (inspect code, verify maxsize set)

### MISSING-006: Singleton `__instances` dicts
`ChecksumASyncSingletonMeta.__instances` in `y/classes/singleton.py` stores every created singleton (ERC20, Contract, UniswapV2Pool, etc.) forever — keyed by address. Two dicts (sync/async). HIGH memory impact. The contract has zero assertions about this.

**Proposed assertion:**
> ### VAL-BOUND-012: Singleton __instances bounded or acknowledged
> The `ChecksumASyncSingletonMeta.__instances` dicts in `y/classes/singleton.py` either (a) use a bounded data structure with eviction, (b) use `WeakValueDictionary` to allow GC, or (c) are explicitly documented as intentionally unbounded with justification (e.g., "singletons must live forever for correctness").
> Evidence: terminal output (inspect code, document decision)

### MISSING-007: Balancer `get_version()` with explicit `ram_cache_ttl=None`
At `y/prices/dex/balancer/balancer.py:215`, `get_version()` has `@a_sync.a_sync(cache_type="memory", ram_cache_ttl=None)` — explicitly no TTL and no maxsize. This means zero eviction. The inventory labels this as HIGH impact.

**Proposed assertion:**
> ### VAL-BOUND-013: Balancer get_version cache bounded
> The `get_version()` method in `y/prices/dex/balancer/balancer.py` (previously `cache_type="memory", ram_cache_ttl=None` — explicitly unbounded) has either a finite maxsize or a TTL.
> Evidence: terminal output (inspect code)

### MISSING-008: mypyc compatibility with cachebox
The repo uses mypyc to compile several modules: `_db/decorators.py`, `convert.py`, `ENVIRONMENT_VARIABLES.py`, `_db/brownie.py`, etc. Some of these modules (decorators.py, convert.py) are directly affected by the cachebox migration. cachebox is a Rust C-extension. No assertion verifies mypyc + cachebox interop.

**Proposed assertion:**
> ### VAL-COMPAT-005: mypyc compilation succeeds with cachebox
> Running `pip install .` (which triggers mypyc compilation) succeeds without errors. The mypyc-compiled modules (`_db/decorators.py`, `convert.py`, `ENVIRONMENT_VARIABLES.py`) correctly interact with cachebox-backed caches at runtime.
> Evidence: terminal output (`pip install .` succeeds, `python -c "import y; print('OK')"` succeeds with compiled extensions)

### MISSING-009: TTL preservation after migration
The contract verifies migration away from cachetools/lru_cache/alru_cache, but never explicitly checks that existing TTL values are preserved. Several caches have critical TTLs:
- `cachetools.func.ttl_cache` in `contracts.py:932` (TTL=1h)
- `cachetools.func.ttl_cache` in `time.py:332` (TTL=300s)
- `@cached(TTLCache(...))` in `_db/utils/price.py:152` (TTL=5min)
- `has_methods()` in `contracts.py:807` (TTL=15min)
- `alru_cache(ttl=TEN_MINUTES)` in `ypriceapi.py` (TTL=10min)

**Proposed assertion:**
> ### VAL-MIG-007: TTL values preserved during migration
> All caches that had explicit TTL values before migration retain equivalent TTL values after migration to cachebox. Specifically verify: `_extract_abi_data()` (1h), `check_node()` (300s), `known_prices_at_block()` (5min), `has_methods()` (15min), `get_chains()`/`chain_supported()` (10min).
> Evidence: terminal output (grep for TTL values in migrated functions, verify they match pre-migration values)

### MISSING-010: `_decimals()` and other `cache_type="memory"` without maxsize
`_decimals()` in `raw_calls.py:67` has `cache_type="memory"` with no maxsize or TTL. Several other MEDIUM-impact caches in the inventory (genericamm, piedao, aave methods, curve methods) also lack maxsize. VAL-BOUND-001 covers these generically but the evidence requirement is too vague to verify them all.

**Proposed (optional — strengthen VAL-BOUND-001 instead):**
See clarification section below.

---

## 2. Assertions Needing Clarification or Stronger Evidence

### VAL-BOUND-001 — too vague to validate systematically
**Current:** "Every `@a_sync(cache_type="memory", ...)` and `@a_sync(ram_cache_ttl=...)` decorator... now has ram_cache_maxsize" / Evidence: "grep for a_sync decorators, verify all have ram_cache_maxsize"

**Problem:** The inventory identifies 30+ such decorators across the codebase. A grep that shows "all have maxsize" doesn't prove nothing was missed. 

**Recommended strengthening:**
> Evidence: Run a script that extracts ALL `@a_sync(...)` decorators with `cache_type="memory"` or `ram_cache_ttl=` across `y/`, counts them, and asserts every one has `ram_cache_maxsize=<N>` where N is a positive integer. Output the count and any failures. Expected count: ≥30 decorators, 0 without maxsize.

### VAL-MIG-001 — ambiguous about bounded lru_cache
**Current:** "No `lru_cache(maxsize=None)` or bare `@lru_cache`... remains in y/"

**Problem:** This conflates two things: (a) removing unbounded `lru_cache(maxsize=None)`, which is critical, and (b) removing bare `@lru_cache` (which defaults to maxsize=128 and is already bounded). The inventory shows `y/_db/utils/utils.py:62` has bare `@lru_cache` with default maxsize=128, which is fine. Should the assertion really require removing *all* lru_cache, including bounded ones?

**Recommended clarification:** Split into two assertions:
1. No `lru_cache(maxsize=None)` remains (critical)
2. Bounded `lru_cache(maxsize=N)` sites are either migrated to cachebox or retained with justification (nice-to-have)

### VAL-MIG-005 — doesn't cover alru_cache with TTL but no maxsize
**Current:** "No `alru_cache(maxsize=None)` remains"

**Problem:** `ypriceapi.py` has `@alru_cache(ttl=TEN_MINUTES)` without maxsize at lines 124 and 142. These technically don't match `maxsize=None` since maxsize isn't specified at all (defaults to None in async_lru). The assertion should also cover `@alru_cache(ttl=...)` without explicit maxsize.

**Recommended:** Broaden to "No alru_cache without explicit finite maxsize remains."

### VAL-ENV-001 — "sensible defaults" is subjective
**Current:** "declares env vars for key cache sizes... with sensible non-zero defaults"

**Problem:** What counts as "sensible"? A validator can't objectively check this.

**Recommended:** Add specific expected default ranges, e.g., "PRICE_CACHE_MAXSIZE defaults to 50,000–500,000" or "all defaults are between 1,000 and 1,000,000."

### VAL-COMPAT-001 — smoke test is too narrow
**Current:** "Running `tests/test_constants.py` via pytest completes with no new failures"

**Problem:** `test_constants.py` is unlikely to exercise any cache behavior. The cache changes affect contracts, prices, time, DB, and DEX modules.

**Recommended:** Run the full test suite (or at minimum tests in `tests/prices/`, `tests/contracts/`, and any test that exercises caching) and verify no *new* failures beyond known pre-existing ones.

### VAL-CROSS-001 — "callable" is insufficient
**Current:** "y.get_price, y.get_prices, and y.Contract are callable"

**Problem:** Functions can be "callable" (importable) but crash when actually called if caches are misconfigured. 

**Recommended:** Add a basic functional check: calling `y.get_price` with a known token/block returns a non-None numeric value (or at minimum doesn't raise a cache-related exception).

### VAL-MIG-002 — needs enumeration of affected files
**Current:** Evidence: "grep for cachebox.cached usage in formerly-lru_cache files"

**Problem:** Without listing which files formerly used lru_cache, a validator can't verify completeness.

**Recommended:** Evidence should cross-reference against the inventory list: `contracts.py`, `_db/decorators.py`, `_db/structs.py`, `_db/brownie.py`, `_db/utils/utils.py`.

---

## 3. Other Gaps and Concerns

### Gap: No assertion about `cachetools` package removal from dependencies
The contract verifies cachetools patterns are replaced (VAL-MIG-003, VAL-MIG-004) but doesn't assert that `cachetools` is removed from `requirements.txt` / `setup.py`. If it stays, someone could reintroduce it.

### Gap: No assertion about `async_lru` package removal
Similarly, after migrating alru_cache, `async_lru` should be removed from dependencies to prevent reintroduction.

### Gap: No assertion about disk caches (Section 3 of inventory)
The inventory identifies joblib.Memory and toolcache disk caches. While these aren't RAM-based and may be out of scope, the contract should explicitly state they're excluded and why.

### Gap: UniswapV3._pools dict (`y/prices/dex/uniswap/v3.py:331`)
A growing dict that's not checksum sets and not `_pools_by_token_cache`. MEDIUM impact. Not covered by any assertion.

### Gap: Compound `lending/compound.py:409` — `ram_cache_maxsize=None` with TTL=5min
Listed in inventory section 2e with "None (default)" for maxsize. Covered generically by VAL-BOUND-001 but as a lending protocol cache with potentially many addresses, worth verifying.

### Gap: Balancer `balancer.py:160` — `ram_cache_maxsize=None` with CACHE_TTL  
Listed in inventory section 2e with "None (default)" for maxsize. Same concern as Compound.

### Concern: The `__cache` decorator on `_get_price()` in magic.py
Line 588 shows `_get_price` is decorated with both `@a_sync.a_sync(...)` and `@__cache`. What is `__cache`? If it's a secondary caching layer, the contract should verify it's also bounded.

### Concern: Race condition during migration
If cachebox caches have different eviction semantics than the originals (e.g., LRU vs FIFO, or different concurrent-access guarantees), the contract should verify behavioral equivalence, not just structural replacement.
