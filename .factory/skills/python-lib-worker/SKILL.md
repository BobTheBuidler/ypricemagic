---
name: python-lib-worker
description: Implements features in the ypricemagic Python library with TDD and smoke test verification
---

# Python Library Worker

NOTE: Startup and cleanup are handled by `worker-base`. This skill defines the WORK PROCEDURE.

## When to Use This Skill

Use for features that modify ypricemagic library code (y/ directory) — pool index construction, continuous discovery, pricing changes, and associated test files.

## Work Procedure

1. **Read the feature description** carefully. Read the referenced source files to understand the current implementation before making changes.

2. **Read .factory/library/architecture.md** for the pool loading pipeline architecture. Read .factory/library/environment.md for environment setup details (especially the macOS SemLock workaround).

3. **Write tests first** (TDD). Create test files following existing patterns:
   - Use `@async_test` (or `@pytest.mark.asyncio_cooperative`) decorator
   - Use `@mainnet_only` for chain-specific tests
   - Use hardcoded block numbers for determinism
   - Place in `tests/prices/dex/` alongside existing test files
   - **Structural tests** (no RPC calls, just checking attributes/types/imports) CAN be run locally on Mac
   - **Integration tests** (marked `@mainnet_only` or `@pytest.mark.slow`) are CI-only — do NOT run these locally Just write them.

4. **Implement the feature.** Follow existing code patterns in v2.py / v3.py:
   - Use `@stuck_coro_debugger` on all new async methods
   - Use `a_sync` decorators consistently
   - Use brownie's Address types for address normalization
   - Add `await sleep(0)` every 10k iterations in loops over large collections (yield to event loop)

5. **Write smoke test scripts** when the feature description mentions them. Scripts go in `scripts/` and must:
   - Start with the macOS SemLock monkey-patch (BEFORE any other imports)
   - Use `BROWNIE_NETWORK=mainnet` and `/Users/bryan/code/ypricemagic-server/.venv/bin/python`
   - Call `get_price()` for the tokens specified in the feature description
   - Print prices and wall-clock timing
   - Handle exceptions gracefully (print traceback, don't crash)

6. **Verify your work:**
   - Read through your changes to confirm correctness
   - Grep for removed methods to confirm they're gone
   - Check that no stale imports or references remain
   - Verify the smoke test script has correct structure (if applicable)

7. **Commit** with a descriptive conventional commit message.

## Example Handoff

```json
{
  "salientSummary": "Built inverted index on UniswapRouterV2 as _pool_index cached property. Replaced all_pools_for() O(N) scan with dict lookup. Removed get_pools_via_factory_getpair() and ram_cache decorator. Wrote 8 test cases in test_pool_index.py covering correctness, address normalization, and edge cases.",
  "whatWasImplemented": "Added _pool_index cached property that builds token->pools dict from __pools__ data. Replaced all_pools_for body with index lookup. Removed get_pools_via_factory_getpair method and the two-path logic in get_pools_for. Removed ram_cache_maxsize decorator from all_pools_for since the index provides O(1) lookups that don't need caching. WETH special case kept for now (returns only USDC pool on mainnet) with TODO comment.",
  "whatWasLeftUndone": "",
  "verification": {
    "commandsRun": [
      {"command": "rg 'get_pools_via_factory_getpair' y/", "exitCode": 1, "observation": "Method fully removed, no references remain"},
      {"command": "rg '_pool_index' y/prices/dex/uniswap/v2.py", "exitCode": 0, "observation": "Found in cached_property definition and all_pools_for usage"}
    ],
    "interactiveChecks": []
  },
  "tests": {
    "added": [
      {
        "file": "tests/prices/dex/test_pool_index.py",
        "cases": [
          {"name": "test_index_matches_scan_for_weth", "verifies": "Index returns same pools as O(N) scan for WETH"},
          {"name": "test_index_empty_for_unknown_token", "verifies": "Empty dict for token with no pools"},
          {"name": "test_address_normalization", "verifies": "Checksummed and lowercased addresses return same result"},
          {"name": "test_index_both_sides", "verifies": "Index has entries for both token0 and token1 of each pool"}
        ]
      }
    ]
  },
  "discoveredIssues": []
}
```

## When to Return to Orchestrator

- The feature depends on a V2/V3 code change that hasn't been implemented yet
- The pool loading mechanism behaves unexpectedly (e.g., PoolsFromEvents.is_reusable change breaks the loading pipeline)
- Address normalization issues that require changes across multiple modules
- The WETH special-case decision needs user input (keep vs remove hardcoded pools)
