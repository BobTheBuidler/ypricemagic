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
