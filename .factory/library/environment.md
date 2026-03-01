# Environment

Environment variables, external dependencies, and setup notes.

**What belongs here:** Required env vars, external API keys/services, dependency quirks, platform-specific notes.
**What does NOT belong here:** Service ports/commands (use `.factory/services.yaml`).

---

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `ETHERSCAN_TOKEN` | Etherscan API key for fetching contract ABIs. Stored in `.env` (gitignored). |
| `BROWNIE_NETWORK` | Brownie network name to connect to (use `mainnet`). |

## Archive Node

- Ethereum mainnet archive node at `http://10.11.12.43:8545`
- Configured via: `brownie networks modify mainnet host=http://10.11.12.43:8545`

## macOS Semaphore Workaround

`dank_mids` patches `concurrent.futures.process.EXTRA_QUEUED_CALLS` to 50,000, which exceeds macOS `SEM_VALUE_MAX` (32,767). All pytest invocations must apply the semaphore clamp workaround before importing dank_mids. See `services.yaml` test commands for the pattern.

## Python Version

- Required: `>=3.10,<3.14`
- Venv uses Python 3.12.12

## Package Management

- This repo uses `setup.py` + `requirements.txt` / `requirements-dev.txt`
- Install via: `.venv/bin/python -m pip install -e . -r requirements-dev.txt`
- `setuptools<82` required for brownie/web3 `pkg_resources` compatibility
- `click` may need explicit install (required by `y._db.exceptions`)
