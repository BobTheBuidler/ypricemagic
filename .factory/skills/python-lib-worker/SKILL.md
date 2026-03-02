---
name: python-lib-worker
description: Implements features in the ypricemagic Python library with TDD and integration testing
---

# Python Library Worker

NOTE: Startup and cleanup are handled by `worker-base`. This skill defines the WORK PROCEDURE.

## When to Use This Skill

Use for features that modify the ypricemagic library: routing logic, type definitions, constants, public API functions, and integration tests.

## Work Procedure

### 1. Understand the Feature

- Read the feature description, preconditions, expectedBehavior, and verificationSteps carefully
- Read the specific source files that will be modified (listed in description or discoverable from the codebase)
- Read `.factory/library/architecture.md` for the price resolution flow and module responsibilities
- Read `.factory/library/environment.md` for environment setup and quirks

### 2. Write Tests First (Red Phase)

- Create or modify integration test files in `tests/` matching the existing pattern
- Tests MUST use the Brownie + archive node setup (real on-chain data, not mocks)
- Follow existing test patterns: `pytest` with `pytest-asyncio-cooperative`
- Write tests that exercise the expected behavior from the feature description
- Run the new tests to confirm they FAIL (red):
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
    'tests/path/to/test_file.py', '-x', '-p', 'no:pytest_ethereum', '-v',
    '--asyncio-task-timeout', '300'
  ]))
  "
  ```
- If tests pass immediately, the test is not testing new behavior — fix the test

### 3. Implement the Feature (Green Phase)

- Make the minimal changes needed to make tests pass
- Follow existing code patterns:
  - Use `a_sync` decorators for async functions
  - Use `igather` for parallel RPC calls
  - Use `ChecksumAddress` / `Address` types from `y.datatypes`
  - Preserve `stuck_coro_debugger` on long-running functions
  - Use `from y.constants import ...` for chain-specific constants
- Keep changes focused — don't refactor unrelated code

### 4. Run Tests (Green Verification)

- Run the new feature-specific tests again — they must PASS now. **You MUST explicitly run the test files you modified or created.** Do not just run the baseline tests.
- Run the full test suite (or relevant subset) to check for regressions:
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
    'tests/', '-x', '-p', 'no:pytest_ethereum', '-W', 'ignore', '-s',
    '--asyncio-task-timeout', '7200'
  ]))
  "
  ```
- Note: pre-existing failures are expected (documented in AGENTS.md). Only NEW failures matter.

### 5. Type Check and Format

- Run mypy: `.venv/bin/python -m mypy y/`
  - This repo uses mypy strict mode. All new public functions need type annotations.
  - **CRITICAL**: Do NOT use `py_compile` for type checking. It only checks syntax. You must use `mypy` to verify types.
- Run black: `.venv/bin/python -m black .`
  - Line length 100, configured in pyproject.toml

### 6. Manual Verification

- For routing changes: verify that a specific token returns a price by running a quick Python script:
  ```bash
  cd /Users/bryan/code/ypricemagic && \
    ETHERSCAN_TOKEN=$(grep ETHERSCAN_TOKEN .env 2>/dev/null | cut -d= -f2) \
    BROWNIE_NETWORK=mainnet \
    TYPEDENVS_SHUTUP=1 \
    .venv/bin/python -c "
  import concurrent.futures.process as cfp
  _orig = cfp._SafeQueue.__init__
  cfp._SafeQueue.__init__ = lambda self, max_size=0, **kw: _orig(self, min(max_size, 32767), **kw)
  import brownie; brownie.network.connect('mainnet')
  from y import get_price
  result = get_price('0x...token_address...', block=18000000)
  print(f'Price: {result}, Type: {type(result).__name__}')
  "
  ```
- Record what you tested and observed

### 7. Finding Test Tokens

When you need tokens that demonstrate specific routing behaviors (e.g., a token with USDT pool but no USDC pool):
- Search Etherscan or use on-chain data to find suitable tokens
- Document the token addresses and why they were chosen in test comments
- Use specific historical blocks where the routing conditions are known to exist
- Prefer tokens on Ethereum mainnet for consistency with the test archive node

## Example Handoff

```json
{
  "salientSummary": "Expanded V3 path generation to include USDT and DAI as intermediary routing tokens alongside WETH. Added 3 integration tests covering USDT-intermediary routing, DAI-intermediary routing, and WETH regression. All 3 new tests pass. mypy clean, black formatted. Verified manually that MIC (0x368B3a58B5f49392e5C9E4C998cb0bB966752E51) now returns a price at block 18000000 via the USDT intermediary path.",
  "whatWasImplemented": "Modified UniswapV3.get_price() in y/prices/dex/uniswap/v3.py to generate multi-hop paths through all ROUTING_TOKENS (WETH, USDC, USDT, DAI) instead of only WETH. Paths are generated as TOKEN→intermediate→USDC for each fee tier and each routing token. Added integration tests in tests/prices/dex/test_v3_multihop.py.",
  "whatWasLeftUndone": "",
  "verification": {
    "commandsRun": [
      {
        "command": "ETHERSCAN_TOKEN=... BROWNIE_NETWORK=mainnet .venv/bin/python -c '...' tests/prices/dex/test_v3_multihop.py -v",
        "exitCode": 0,
        "observation": "3 tests passed: test_usdt_intermediary, test_dai_intermediary, test_weth_regression"
      },
      {
        "command": ".venv/bin/python -m mypy y/prices/dex/uniswap/v3.py",
        "exitCode": 0,
        "observation": "Success: no issues found"
      },
      {
        "command": ".venv/bin/python -m black --check y/prices/dex/uniswap/v3.py",
        "exitCode": 0,
        "observation": "All files formatted correctly"
      }
    ],
    "interactiveChecks": [
      {
        "action": "Ran Python script to get price of MIC (0x368B...) at block 18000000",
        "observed": "Returned UsdPrice($0.00123456), confirming USDT intermediary path works through get_price"
      }
    ]
  },
  "tests": {
    "added": [
      {
        "file": "tests/prices/dex/test_v3_multihop.py",
        "cases": [
          {"name": "test_usdt_intermediary_price", "verifies": "V3 finds price through TOKEN→USDT→USDC path"},
          {"name": "test_dai_intermediary_price", "verifies": "V3 finds price through TOKEN→DAI→USDC path"},
          {"name": "test_weth_direct_regression", "verifies": "WETH→USDC direct price unchanged after expansion"}
        ]
      }
    ]
  },
  "discoveredIssues": []
}
```

## When to Return to Orchestrator

- Cannot find suitable test tokens on the archive node for the required routing pattern
- Existing test failures appear to be caused by the new changes (not pre-existing)
- The routing change requires modifying the `UniswapMultiplexer` dispatch logic (broader change than expected)
- mypy errors that require type system changes beyond the feature scope
- Archive node is unreachable or returning errors
