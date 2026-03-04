# User Testing

Testing surface, tools, setup steps, and known quirks for validation.

**What belongs here:** How to test the library, testing tools, setup notes, known issues.

---

## Testing Surface

This is a Python library (not a web app). All testing is done via:
- **pytest** integration tests against an Ethereum archive node
- **Python scripts** that call library functions directly

## How to Run Tests

```bash
cd /Users/bryan/code/ypricemagic

# Full test suite (with macOS semaphore workaround)
ETHERSCAN_TOKEN=<token> BROWNIE_NETWORK=mainnet TYPEDENVS_SHUTUP=1 \
  .venv/bin/python -c "
import concurrent.futures.process as cfp
_orig = cfp._SafeQueue.__init__
cfp._SafeQueue.__init__ = lambda self, max_size=0, **kw: _orig(self, min(max_size, 32767), **kw)
import sys; sys.exit(__import__('pytest').main([
  'tests/', '-x', '-p', 'no:pytest_ethereum', '-W', 'ignore', '-s',
  '--asyncio-task-timeout', '7200'
]))
"

# Single test file
ETHERSCAN_TOKEN=<token> BROWNIE_NETWORK=mainnet .venv/bin/pytest tests/prices/dex/test_uniswap.py -x -p no:pytest_ethereum -v
```

## Known Quirks

- First run is slow (~5 min) due to Etherscan ABI fetching for contracts
- Pre-existing test failures exist (ContractLogicError / aggregator assertions) — these are known and acceptable
- `pytest-ethereum` plugin must be disabled (`-p no:pytest_ethereum`) due to incompatible `eth_typing` imports
- macOS requires semaphore workaround (see environment.md)
- Tests require `BROWNIE_NETWORK=mainnet` env var for network connection

## Validation Approach

For each assertion, validators should:
1. Run the specific pytest test that covers the assertion
2. Verify the test passes and the output matches expected behavior
3. For price assertions, verify values are within reasonable ranges (not exact matches, as on-chain data varies)

## Running Specific Test Files

Use this pattern (macOS semaphore workaround required):

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
  'tests/YOUR_TEST_FILE.py', '-p', 'no:pytest_ethereum', '-W', 'ignore',
  '--runslow', '--asyncio-task-timeout', '7200', '-v', '-s'
]))
"
```

## Test Files Mapped to Assertions (Current Mission)

| Test File | Assertions Covered |
|-----------|-------------------|
| `tests/test_price_result.py` | VAL-TYPE-*, VAL-CORE-*, VAL-PATH-*, VAL-CALLER-*, VAL-API-*, VAL-CROSS-001/002/003 |
| `tests/test_vttl_cache.py` | VAL-VTTL-* |
| `tests/test_purge.py` | VAL-PURGE-* |
| `tests/test_cache_bounds.py` | Baseline (pre-existing) |
| `tests/test_constants.py` | Baseline (pre-existing) |

### Previous Mission Test Files (still valid)
| `tests/prices/dex/test_v3_liquidity.py` | VAL-LIQ-001, VAL-LIQ-002, VAL-LIQ-003 |
| `tests/prices/dex/test_v3_multihop.py` | VAL-V3-003, VAL-V3-004, VAL-V3-005 |
| `tests/prices/dex/test_v2_multipool.py` | VAL-V2-001 through VAL-V2-006 |

## Flow Validator Guidance: pytest tests

This is a Python library. "User testing" means running pytest integration tests and
Python scripts against the live archive node at http://10.11.12.43:8545.

**Isolation**: Tests are read-only blockchain queries. No shared mutable state. All
validators can run in parallel safely.

**Timeouts**: V3/V2 slow tests scan PoolCreated events and may take 5-10 minutes per
test. Use `--asyncio-task-timeout 7200` and do not set shorter timeouts.

**When a test doesn't exist for an assertion**: Try to write and run an inline Python
script that directly tests the behavior described in the validation contract.

**Archive node**: Read-only at http://10.11.12.43:8545. Do not send transactions.
