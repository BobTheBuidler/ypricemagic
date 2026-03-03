---
name: cache-worker
description: Migrates caches to cachebox and bounds unbounded caches in ypricemagic
---

# Cache Worker

NOTE: Startup and cleanup are handled by `worker-base`. This skill defines the WORK PROCEDURE.

## When to Use This Skill

Use for features that modify caching mechanisms in ypricemagic: replacing functools.lru_cache with cachebox, replacing cachetools with cachebox, adding ram_cache_maxsize to a_sync decorators, bounding data structures, and creating cache configuration infrastructure.

## Key Context

- **cachebox** is a Rust-backed, thread-safe caching library. All cache classes (LRUCache, TTLCache, etc.) are thread-safe by default with no manual locking needed.
- **cachebox API**: `@cachebox.cached(cachebox.LRUCache(maxsize))` for LRU, `@cachebox.cached(cachebox.TTLCache(maxsize, ttl=seconds))` for TTL. Supports both sync and async functions. `maxsize=0` means unbounded.
- **a_sync caches** use `ram_cache_maxsize` and `ram_cache_ttl` parameters on the `@a_sync` decorator. These are internal to the a_sync library — do NOT replace with cachebox. Just add `ram_cache_maxsize=N` where missing.
- Cache size env vars are declared in `y/ENVIRONMENT_VARIABLES.py` using the `typed_envs` library pattern.
- The central cache config module (`y/_cache.py`) provides pre-configured cache factories.

## Work Procedure

### 1. Understand the Feature

- Read the feature description, preconditions, expectedBehavior, and verificationSteps carefully
- Read `.factory/library/architecture.md` and `.factory/library/environment.md`
- Read `.factory/reports/cache-inventory.md` for the full cache inventory
- Identify which specific cache sites this feature targets

### 2. Write Tests First (Red Phase)

- Create or modify test files in `tests/`
- For cache bounding: write tests that verify maxsize is enforced (insert > maxsize entries, assert len == maxsize)
- For thread safety: write tests with concurrent thread access (10+ threads, verify no corruption)
- For migration: write tests that verify cached function behavior is preserved (same inputs produce same outputs)
- For env var configuration: write tests that verify env var overrides work
- Run new tests to confirm they FAIL:
  ```bash
  cd /Users/bryan/code/ypricemagic && \
    BROWNIE_NETWORK=mainnet \
    TYPEDENVS_SHUTUP=1 \
    .venv/bin/python -c "
  import concurrent.futures.process as cfp
  _orig = cfp._SafeQueue.__init__
  cfp._SafeQueue.__init__ = lambda self, max_size=0, **kw: _orig(self, min(max_size, 32767), **kw)
  import sys; sys.exit(__import__('pytest').main([
    'tests/YOUR_TEST_FILE.py', '-x', '-p', 'no:pytest_ethereum', '-v',
    '--timeout', '120'
  ]))
  "
  ```

### 3. Implement the Feature (Green Phase)

**For functools.lru_cache migration:**
```python
# BEFORE:
from functools import lru_cache
@lru_cache(maxsize=None)
def my_func(arg):
    ...

# AFTER:
import cachebox
@cachebox.cached(cachebox.LRUCache(ENVS.SOME_CACHE_MAXSIZE))
def my_func(arg):
    ...
```

**For cachetools migration:**
```python
# BEFORE:
from cachetools import TTLCache
from cachetools import cached
@cached(TTLCache(maxsize=1000, ttl=300), lock=threading.Lock())
def my_func(arg):
    ...

# AFTER:
import cachebox
@cachebox.cached(cachebox.TTLCache(1000, ttl=300))
def my_func(arg):
    ...
```

**For cachetools.func.ttl_cache migration:**
```python
# BEFORE:
from cachetools.func import ttl_cache
@ttl_cache(maxsize=1000, ttl=3600)
def my_func(arg):
    ...

# AFTER:
import cachebox
@cachebox.cached(cachebox.TTLCache(1000, ttl=3600))
def my_func(arg):
    ...
```

**For alru_cache migration:**
```python
# BEFORE:
from async_lru import alru_cache
@alru_cache(maxsize=1000, ttl=300)
async def my_func(arg):
    ...

# AFTER:
import cachebox
@cachebox.cached(cachebox.TTLCache(1000, ttl=300))
async def my_func(arg):
    ...
```

**For a_sync caches (DO NOT replace with cachebox):**
```python
# BEFORE:
@a_sync(cache_type="memory", ram_cache_ttl=ENVS.CACHE_TTL)
async def my_func(arg):
    ...

# AFTER — just add ram_cache_maxsize:
@a_sync(cache_type="memory", ram_cache_ttl=ENVS.CACHE_TTL, ram_cache_maxsize=ENVS.SOME_MAXSIZE)
async def my_func(arg):
    ...
```

**Important patterns to preserve:**
- `stuck_coro_debugger` decorators on async functions must be kept
- `@eth_retry.auto_retry` decorators must be kept
- Function signatures and return types must not change
- TTL values from the old cache must be preserved in the new cache

### 4. Run Tests (Green Verification)

- Run feature-specific tests — they must PASS
- Run the smoke test to check for regressions:
  ```bash
  cd /Users/bryan/code/ypricemagic && \
    ETHERSCAN_TOKEN=$(grep ETHERSCAN_TOKEN .env 2>/dev/null | cut -d= -f2) \
    BROWNIE_NETWORK=mainnet \
    TYPEDENVS_SHUTUP=1 \
    .venv/bin/python -c "
  import concurrent.futures.process as cfp
  _orig = cfp._SafeQueue.__init__
  cfp._SafeQueue.__init__ = lambda self, max_size=0, **kw: _orig(self, min(max_size, 32767), **kw)
  import sys; sys.exit(__import__('pytest').main([
    'tests/test_constants.py', '-x', '-p', 'no:pytest_ethereum', '-W', 'ignore',
    '--timeout', '120'
  ]))
  "
  ```

### 5. Type Check and Format

- Run mypy on modified files: `.venv/bin/python -m mypy --follow-imports=skip --disable-error-code unused-ignore <files>`
- Run black: `.venv/bin/python -m black .`
- Line length 100 per pyproject.toml

### 6. Manual Verification

- Verify the specific caches targeted by this feature are actually bounded:
  ```python
  # Example: verify a cachebox cache has correct maxsize
  .venv/bin/python -c "
  import cachebox
  cache = cachebox.LRUCache(5)
  for i in range(10):
      cache[i] = i
  assert len(cache) == 5, f'Expected 5, got {len(cache)}'
  print('Cache bound verified')
  "
  ```
- For each migrated cache, verify the function still works correctly with a quick call

## Example Handoff

```json
{
  "salientSummary": "Replaced 7 functools.lru_cache sites with cachebox.cached(cachebox.LRUCache(N)) in contracts.py, _db/decorators.py, _db/structs.py, _db/brownie.py, convert.py. Added 4 tests in tests/test_cache_bounds.py covering maxsize enforcement and thread safety. All tests pass. mypy clean on modified files, black formatted.",
  "whatWasImplemented": "Migrated lru_cache in y/contracts.py (_get_explorer_api_key), y/_db/decorators.py (db_session_cached), y/_db/structs.py (_make_snake), y/_db/brownie.py (_get_select_statement), y/convert.py (checksum), y/_db/utils/utils.py, y/_db/utils/token.py to use cachebox.cached(cachebox.LRUCache(maxsize)) with sizes from ENVS. Removed functools.lru_cache imports. Added tests verifying maxsize enforcement and concurrent thread access.",
  "whatWasLeftUndone": "",
  "verification": {
    "commandsRun": [
      {
        "command": ".venv/bin/python -m pytest tests/test_cache_bounds.py -v",
        "exitCode": 0,
        "observation": "4 tests passed: test_lru_eviction, test_thread_safety, test_env_override, test_checksum_cache_bounded"
      },
      {
        "command": ".venv/bin/python -m pytest tests/test_constants.py -x",
        "exitCode": 0,
        "observation": "6 tests passed, no regressions"
      },
      {
        "command": ".venv/bin/python -m mypy --follow-imports=skip y/contracts.py y/_db/decorators.py y/convert.py",
        "exitCode": 0,
        "observation": "No issues found"
      },
      {
        "command": ".venv/bin/python -m black --check y/",
        "exitCode": 0,
        "observation": "All files formatted"
      }
    ],
    "interactiveChecks": [
      {
        "action": "Ran Python script to verify cachebox LRUCache(100) evicts at 101 entries",
        "observed": "len(cache) == 100 after inserting 101 entries. LRU eviction confirmed."
      },
      {
        "action": "Ran 20-thread concurrent access test on cachebox.LRUCache(1000)",
        "observed": "No exceptions, no corruption, final cache size <= 1000"
      }
    ]
  },
  "tests": {
    "added": [
      {
        "file": "tests/test_cache_bounds.py",
        "cases": [
          {"name": "test_lru_eviction", "verifies": "cachebox LRUCache evicts LRU entry at maxsize"},
          {"name": "test_thread_safety", "verifies": "20 concurrent threads don't corrupt cachebox cache"},
          {"name": "test_env_override", "verifies": "Setting env var changes cache maxsize"},
          {"name": "test_checksum_cache_bounded", "verifies": "checksum() cache doesn't exceed maxsize"}
        ]
      }
    ]
  },
  "discoveredIssues": []
}
```

## When to Return to Orchestrator

- cachebox doesn't support a specific caching pattern used in the codebase (e.g., custom key functions that don't work with cachebox)
- mypyc compilation fails with cachebox imports
- A cache migration breaks existing tests in a way that's not straightforward to fix
- The a_sync library's internal cache mechanism doesn't support ram_cache_maxsize on a specific decorator pattern
- A function's behavior changes after cache migration (different results for same inputs)
