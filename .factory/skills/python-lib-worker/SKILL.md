---
name: python-lib-worker
description: Implements features in the ypricemagic Python library with TDD and verification
---

# Python Library Worker

NOTE: Startup and cleanup are handled by `worker-base`. This skill defines the WORK PROCEDURE.

## When to Use This Skill

Use for features that modify ypricemagic library code (y/ directory), tests, or project configuration (deps, branch management).

## CRITICAL: Daemon Timeout Prevention

**Any command involving pytest or brownie WILL block for several minutes** during `brownie.network.connect()` (called at conftest.py import time). This triggers daemon inactivity timeout and kills your session.

**You MUST use `fireAndForget=true` for ALL pytest/brownie commands.** Then poll the log file to stay alive:

```
# 1. Launch in background (use a unique log file per run)
# ALWAYS source .env first for ETHERSCAN_TOKEN
Execute(command="set -a && source .env && set +a && PYTEST_ADDOPTS='-p no:pytest_ethereum' BROWNIE_NETWORK=mainnet .venv/bin/pytest tests/test_foo.py -W ignore -s --tb=short > /tmp/test_run_001.log 2>&1", fireAndForget=true)
# Note the PID from output

# 2. Poll every 30s to stay alive AND see progress
Execute(command="sleep 30 && tail -50 /tmp/test_run_001.log")

# 3. Check if process finished
Execute(command="ps -p <PID> > /dev/null 2>&1 && echo RUNNING || echo DONE")

# 4. When DONE, read full results
Read(file_path="/tmp/test_run_001.log")
```

**NEVER run pytest or brownie commands synchronously.** They WILL time out your session.

Also use fireAndForget for `.venv/bin/pip install -e .` (triggers mypyc compilation, can take minutes).

## Work Procedure

1. **Read the feature description** carefully. Understand exactly what needs to change and what the acceptance criteria are.

2. **Read context files:**
   - `.factory/library/architecture.md` for pricing pipeline architecture
   - `.factory/library/environment.md` for environment setup
   - Reference old fork code via `git show abandoned-master:<path>` when the feature description mentions porting from the old fork
   - Reference stale feature branches for implementation guidance via `git show feat/xxx:<path>`. Available: `feat/cachebox-memory-optimization`, `feat/curve-gauges`, `feat/erc4626`, `feat/exotic-tokens`, `feat/priceresult-trade-path-cache-ops`

3. **Check current branch state.** Ensure you're on `clean-rebuild` or a feature branch off it. Create a feature branch: `git checkout -b <feature-name> clean-rebuild`.

4. **Write tests first** (TDD). Create test files following existing patterns:
   - Check `tests/fixtures.py` for available test decorators (`@async_test`, `@mainnet_only`, etc.)
   - Use hardcoded block numbers for determinism
   - Fantom-only tests: `@pytest.mark.skip(reason="Fantom-only")`
   - Tests that don't need RPC can use simple unit test patterns

5. **Implement the feature.** Follow existing code patterns:
   - Use `@stuck_coro_debugger` on all new async pricing/RPC methods
   - Use `a_sync` decorators consistently
   - Use brownie's Address types for address normalization
   - Wrap prices in PriceResult with human-readable source descriptions
   - All caches must be bounded (set `ram_cache_maxsize`)

6. **Verify your work** (using fireAndForget for ALL test commands):
   - Run the specific test file first (fireAndForget + poll pattern)
   - Then run the full suite (fireAndForget + poll pattern, may take 10+ minutes)
   - Use unique log file names per run (e.g., `/tmp/test_targeted.log`, `/tmp/test_full.log`)
   - Grep for removed methods to confirm they're gone
   - Check that no stale imports or references remain

7. **Commit** with a descriptive conventional commit message.

8. **Create PR and squash merge:**
   - `gh pr create --base clean-rebuild --title "<type>: <description>" --body "<summary>"`
   - `gh pr merge --squash`
   - `git checkout clean-rebuild && git pull`

## Example Handoff

```json
{
  "salientSummary": "Ported PriceResult/PriceStep dataclasses from abandoned-master to clean-rebuild. Added float backward-compatibility (__float__, __gt__, __mul__, etc.). Wrote 12 unit tests covering construction, arithmetic, comparison, Decimal compatibility, and boolean truthiness. All upstream tests pass (verified via fireAndForget pytest run, exit code 0).",
  "whatWasImplemented": "PriceResult dataclass in y/datatypes.py with .price and .path attributes. PriceStep dataclass with .token, .price, .source fields. PriceResult supports float(result), result > 0, result * 2 via operator overloads. Decimal(result.price) works, Decimal(result) intentionally raises.",
  "whatWasLeftUndone": "",
  "verification": {
    "commandsRun": [
      {"command": "PYTEST_ADDOPTS='-p no:pytest_ethereum' BROWNIE_NETWORK=mainnet .venv/bin/pytest tests/test_price_result.py -W ignore -s --tb=short (fireAndForget)", "exitCode": 0, "observation": "12 tests passed"},
      {"command": "PYTEST_ADDOPTS='-p no:pytest_ethereum' BROWNIE_NETWORK=mainnet .venv/bin/pytest -W ignore -s --tb=short (fireAndForget)", "exitCode": 0, "observation": "All 47 upstream tests + 12 new tests passed"}
    ],
    "interactiveChecks": []
  },
  "tests": {
    "added": [
      {
        "file": "tests/test_price_result.py",
        "cases": [
          {"name": "test_price_result_construction", "verifies": "PriceResult can be constructed with price and path"},
          {"name": "test_float_compatibility", "verifies": "float(result) returns the price value"},
          {"name": "test_comparison_operators", "verifies": "result > 0, result < 1000, result == result work"},
          {"name": "test_arithmetic", "verifies": "result * 2, result / 2, result + 1 work"},
          {"name": "test_decimal_price_works", "verifies": "Decimal(result.price) succeeds"},
          {"name": "test_decimal_result_raises", "verifies": "Decimal(result) raises TypeError"}
        ]
      }
    ]
  },
  "discoveredIssues": []
}
```

## When to Return to Orchestrator

- The feature depends on code that hasn't been ported yet
- The brownie network connection fails or the RPC node is unreachable
- Test failures in upstream code that are unrelated to the current feature
- Branch merge conflicts that need resolution
- Requirements are ambiguous about what to port vs what to implement fresh
- Daemon timeout keeps killing your session despite using fireAndForget
