---
name: python-lib-worker
description: Implements features in the ypricemagic Python library with TDD and code changes
---

# Python Library Worker

NOTE: Startup and cleanup are handled by `worker-base`. This skill defines the WORK PROCEDURE.

## When to Use This Skill

Use for features that modify the ypricemagic library: pricing logic, bucket classification, routing, token type detection, and associated tests.

## Important Context

- **Worktree:** All work happens in `/Users/bryan/code/ypricemagic-pricing` (NOT `/Users/bryan/code/ypricemagic`)
- **Venv:** Shared at `/Users/bryan/code/ypricemagic/.venv` — use absolute path
- **Tests don't run on macOS:** Write tests for CI but don't expect them to pass locally. Validation happens through ypricemagic-server Docker stack.
- **Reference codebase:** `/Users/bryan/code/flashprofits/price_helpers.py` has token classification patterns to match

## Work Procedure

### 1. Understand the Feature

- Read feature description, preconditions, expectedBehavior, verificationSteps
- Read specific source files that will be modified
- Read `.factory/library/architecture.md` for price resolution flow
- Read `.factory/library/environment.md` for environment notes

### 2. Write Tests First (Red Phase)

- Create or modify test files in `tests/` matching existing patterns
- Tests use pytest with `pytest-asyncio-cooperative`
- Follow existing conventions: `@pytest.mark.asyncio_cooperative` decorator
- Write tests that exercise the expected behavior
- Tests may not run locally (macOS) — that's expected. Write them correctly for Linux/Docker.
- If you CAN run a specific test file locally, do so to verify it fails:
  ```bash
  cd /Users/bryan/code/ypricemagic-pricing && \
    ETHERSCAN_TOKEN=$(grep ETHERSCAN_TOKEN .env 2>/dev/null | cut -d= -f2) \
    BROWNIE_NETWORK=mainnet \
    TYPEDENVS_SHUTUP=1 \
    /Users/bryan/code/ypricemagic/.venv/bin/python -c "
  import concurrent.futures.process as cfp
  _orig = cfp._SafeQueue.__init__
  cfp._SafeQueue.__init__ = lambda self, max_size=0, **kw: _orig(self, min(max_size, 32767), **kw)
  import sys; sys.exit(__import__('pytest').main([
    'tests/path/to/test_file.py', '-x', '-p', 'no:pytest_ethereum', '-v',
    '--asyncio-task-timeout', '300'
  ]))
  "
  ```

### 3. Implement the Feature (Green Phase)

- Make minimal changes to make tests pass
- Follow existing code patterns:
  - `a_sync` decorators for async functions
  - `igather` for parallel RPC calls
  - `ChecksumAddress` / `Address` types from `y.datatypes`
  - Preserve `stuck_coro_debugger` on long-running functions
  - `from y.constants import ...` for chain-specific constants
- Keep changes focused — don't refactor unrelated code

### 4. Type Check and Format

- Run mypy: `/Users/bryan/code/ypricemagic/.venv/bin/python -m mypy y/`
- Run black: `/Users/bryan/code/ypricemagic/.venv/bin/python -m black .`

### 5. Manual Verification (if possible)

For pricing changes, try a quick Python script to verify (may work on macOS even if full test suite doesn't):
```bash
cd /Users/bryan/code/ypricemagic-pricing && \
  ETHERSCAN_TOKEN=$(grep ETHERSCAN_TOKEN .env 2>/dev/null | cut -d= -f2) \
  BROWNIE_NETWORK=mainnet \
  TYPEDENVS_SHUTUP=1 \
  /Users/bryan/code/ypricemagic/.venv/bin/python -c "
import concurrent.futures.process as cfp
_orig = cfp._SafeQueue.__init__
cfp._SafeQueue.__init__ = lambda self, max_size=0, **kw: _orig(self, min(max_size, 32767), **kw)
import brownie; brownie.network.connect('mainnet')
from y import get_price
result = get_price('0x...token_address...', block=18000000)
print(f'Price: {result}, Type: {type(result).__name__}')
"
```
If this works, great — record the output. If it fails with macOS-specific errors, note it and move on.

### 6. Create PR (if feature description says to)

- Push changes to the appropriate branch
- Create PR: `gh pr create --base master --title "..." --body "..."`
- Include Summary, Rationale, and Details sections in PR body
- Follow Conventional Commits prefix for PR title

### 7. Finding Test Tokens

When needing tokens that demonstrate specific behaviors:
- Search `/Users/bryan/code/flashprofits/price_helpers.py` for hardcoded addresses of that token type
- Use specific historical blocks where conditions are known
- Document token addresses and rationale in test comments

## Example Handoff

```json
{
  "salientSummary": "Restricted 'stable usd' bucket to USDC only, removed V2 short-circuit for non-USDC stablecoins, and extended V2 paths ending at non-USDC stablecoins with a USDC hop (serial with amount via getAmountsOut, parallel without amount via asyncio.gather). Updated test_stablecoins and test_check_bucket_stablecoins. Added test_mic_resolves_via_usdt. mypy clean, black formatted. Created PR #1.",
  "whatWasImplemented": "Modified buckets.py to restrict 'stable usd' to USDC only. Modified v2.py to restrict return-1 shortcircuit to USDC and extend paths ending at non-USDC stablecoins with USDC hop. Updated tests in test_constants.py and test_buckets.py. Added MIC test.",
  "whatWasLeftUndone": "",
  "verification": {
    "commandsRun": [
      {"command": "mypy y/", "exitCode": 0, "observation": "No type errors"},
      {"command": "black --check .", "exitCode": 0, "observation": "All formatted"},
      {"command": "gh pr create ...", "exitCode": 0, "observation": "PR #1 created"}
    ],
    "interactiveChecks": [
      {"action": "Ran Python script to get USDC price", "observed": "UsdPrice(1.0) with source 'stable usd'"},
      {"action": "Ran Python script to get USDT price", "observed": "UsdPrice(0.9998) with source 'uniswap v2'"}
    ]
  },
  "tests": {
    "added": [
      {
        "file": "tests/test_stablecoin_pricing.py",
        "cases": [
          {"name": "test_usdc_is_one", "verifies": "USDC returns exactly $1"},
          {"name": "test_usdt_real_price", "verifies": "USDT returns real market price"},
          {"name": "test_mic_resolves_via_usdt", "verifies": "MIC resolves through USDT path"}
        ]
      }
    ]
  },
  "discoveredIssues": []
}
```

## When to Return to Orchestrator

- Cannot find suitable test tokens for the required pattern
- Existing test failures appear caused by new changes (not pre-existing)
- The change requires modifying core async infrastructure (a_sync, igather)
- mypy errors requiring type system changes beyond feature scope
- Archive node / brownie network unreachable
- Feature requires changes to ypricemagic-server (wrong worker type)
