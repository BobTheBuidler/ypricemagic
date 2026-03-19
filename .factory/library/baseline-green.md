# Baseline Test Results

**What belongs here:** Test baseline established on the clean-rebuild branch.

---

## Test Environment

- Python 3.12.12 via `.venv`
- RPC: Ethereum mainnet node at `http://10.11.12.43:8545`
- Command: `PYTEST_ADDOPTS="-p no:pytest_ethereum" BROWNIE_NETWORK=mainnet .venv/bin/pytest -W ignore -s --tb=short -v`

## Key Findings

### INTERNALERROR from mypyc build artifacts (FIXED)

Brownie's test runner (`brownie/test/managers/runner.py`) tries to hash all files in `build/` via `_get_ast_hash()`. When mypyc build artifacts (`.o` object files in `build/temp.*`) exist, brownie fails with `UnicodeDecodeError` because it tries to decode binary files as UTF-8.

**Fix:** Clean up `build/temp.*`, `build/bdist.*`, `build/lib.*` before running tests. Added to `.gitignore`, `init.sh`, and `Makefile`.

### Concurrent test execution failures (pre-existing, NOT fixed)

`pytest-asyncio-cooperative` runs tests concurrently within a single event loop. When running the full suite (1000+ tests), many tests fail due to shared async state, event loop contention, and RPC connection competition. These same tests **pass when run individually** or in smaller batches.

- Full suite (concurrent): ~641 failed, ~411 passed, ~31 skipped
- Chainlink file alone: 5 failed, 229 passed, 74 skipped
- Constants/time/dank subset: 11 passed

This is a known limitation of the test infrastructure, not actual code bugs.

### Pre-existing test failures (per-file individual runs)

**tests/prices/test_chainlink.py (5 failures):**
- `test_chainlink_latest[0xa693B19d...]` - ContractLogicError: Polymath POLY Chainlink aggregator deprecated on-chain
- `test_chainlink_latest[0x459086F2...]` - ContractLogicError: renFIL Chainlink aggregator deprecated on-chain
- `test_chainlink_latest[0x1C5db575...]` - ContractLogicError: Token's Chainlink aggregator deprecated on-chain
- `test_chainlink_before_registry[0x1C5db575...]` - Same token, same issue
- `test_chainlink_before_feed` - YFI returns price (32445.38) at block before feed deployment; another pricing source resolves it

**tests/classes/test_erc20.py (1 failure):**
- `test_erc20_at_block[0x57Ab1E02...-5761012]` - sUSD at very early block; pre-existing proxy issue

These failures are all caused by on-chain state changes (deprecated contracts) or very old block edge cases, not by our dependency changes.

## Verification Notes

- Tests that pass individually confirm no new failures from our dep changes
- The 11-test quick subset (constants, time, dank_import_guard) always passes
- Chainlink feed resolution and price lookups work correctly for active feeds
- ERC20 properties work correctly for current tokens at recent blocks
