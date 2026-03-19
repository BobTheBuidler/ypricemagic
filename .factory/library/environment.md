# Environment

**What belongs here:** Required env vars, external dependencies, setup notes.

---

## Python Environment

- Python 3.12 via `.venv` at `/Users/bryan/code/ypricemagic/.venv`
- All deps installed via `pip install -e .` and `pip install -r requirements-dev.txt`
- Use `.venv/bin/python` and `.venv/bin/pytest` directly (don't rely on system python)

## Brownie Network

- Network name: `mainnet`
- RPC host: `http://10.11.12.43:8545` (local Ethereum mainnet node, likely Erigon)
- Chain ID: 1
- The `BROWNIE_NETWORK=mainnet` env var must be set when running tests

## ETHERSCAN_TOKEN env var

- Required by `y.contracts.Contract` when fetching ABIs for unknown contracts
- Stored in `.env` file at repo root (gitignored)
- Must be sourced before running tests that use contract ABI fetching (e.g., exotic token tests, chainlink tests)
- Command: `set -a && source .env && set +a`
- Tests that DON'T need Etherscan (test_constants.py, test_time.py, test_dank_import_guard.py, test_price_result.py, test_trade_path_sources.py, test_cachebox.py) always pass without it
- Tests that DO need it (test_exotic_tokens.py, most price tests with real token addresses) will fail with `InvalidAPIKeyError` from `_extract_abi_data_async` if not set

## Branch Structure

- `clean-rebuild`: main working branch, based on `upstream/master`
- `abandoned-master`: old fork master preserved for reference
- `upstream/master`: BobTheBuidler/ypricemagic upstream
- Reference old code: `git show abandoned-master:<path>`

## macOS Notes

- dank_mids fork (`SatoshiAndKin/dank_mids`) is used to work around macOS SEM_VALUE_MAX semaphore limits
- Platform guard in pyproject.toml ensures correct dependency resolution
