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

## Test Patterns

- `@async_test` decorator for async tests (from tests/fixtures.py)
- `@mainnet_only` for Ethereum mainnet-specific tests
- Hardcoded block numbers for deterministic results
- Fantom-only tests: `@pytest.mark.skip(reason="Fantom-only")`
