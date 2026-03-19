# User Testing

**What belongs here:** Testing surface, validation approach, resource costs.

---

## Validation Surface

This is a Python library with no web UI or CLI beyond the test suite. The test suite IS the validation surface.

- **Surface type:** pytest test suite
- **Tool:** `.venv/bin/pytest` with brownie network connection
- **Setup:** `BROWNIE_NETWORK=mainnet` env var, Ethereum node reachable at http://10.11.12.43:8545

## Validation Concurrency

- **Max concurrent validators:** 1
- **Rationale:** Tests make real RPC calls to a shared Ethereum node. Brownie manages a global network connection. Running multiple test processes concurrently would cause connection conflicts.

## Test Execution Warning

brownie.network.connect() is called at conftest.py import time and blocks for several minutes with no output. Any pytest invocation MUST use fireAndForget + polling to avoid daemon timeout. See AGENTS.md for the pattern.

## Test Patterns

- `@async_test` decorator for async tests (from tests/fixtures.py) -- verify this exists before using
- `@mainnet_only` for Ethereum mainnet-specific tests
- Hardcoded block numbers for deterministic results
- Fantom-only tests: `@pytest.mark.skip(reason="Fantom-only")`
- Per-test timeout: 600s (pyproject.toml)

## Flow Validator Guidance: pytest test suite

**Isolation:** Single validator only. No concurrent test runners against the same brownie node.

**Test file targeting:** For milestone-specific validation, target specific test files with `-k` flag or by filename. For trade-path assertions, target:
- `tests/test_price_result.py` (VAL-PATH-001, VAL-PATH-002)
- `tests/test_trade_path_sources.py` (VAL-PATH-003, VAL-PATH-004)

**Command pattern (MANDATORY fireAndForget):**
```bash
PYTEST_ADDOPTS="-p no:pytest_ethereum" BROWNIE_NETWORK=mainnet .venv/bin/pytest tests/test_price_result.py tests/test_trade_path_sources.py -W ignore -s --tb=short > /tmp/test_run.log 2>&1
```

**Known OK failures (do not count against assertions):**
- NonStandardERC20 for sUSD logged during test runs
- Chainlink aggregator deprecations for POLY and renFIL
- Concurrent test execution timeouts (test infra limitation)
- sUSD at very early block 5761012

**VAL-PATH-005 (upstream tests still pass):** The full suite must pass. Run:
```bash
PYTEST_ADDOPTS="-p no:pytest_ethereum" BROWNIE_NETWORK=mainnet .venv/bin/pytest -W ignore -s --tb=short > /tmp/full_test_run.log 2>&1
```

**Interpretation:** As long as no NEW test failures appear beyond the known pre-existing ones above, the assertion passes.
