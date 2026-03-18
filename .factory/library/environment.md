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

## Branch Structure

- `clean-rebuild`: main working branch, based on `upstream/master`
- `abandoned-master`: old fork master preserved for reference
- `upstream/master`: BobTheBuidler/ypricemagic upstream
- Reference old code: `git show abandoned-master:<path>`

## macOS Notes

- dank_mids fork (`SatoshiAndKin/dank_mids`) is used to work around macOS SEM_VALUE_MAX semaphore limits
- Platform guard in pyproject.toml ensures correct dependency resolution
