# Environment

Environment variables, external dependencies, and setup notes.

**What belongs here:** Required env vars, external API keys/services, dependency quirks.
**What does NOT belong here:** Service ports/commands (use `.factory/services.yaml`).

---

## Python Environment

- Python 3.12 in venv at `/Users/bryan/code/ypricemagic/.venv` (shared with main repo)
- brownie 1.22.0.dev2 (custom fork)
- web3 6.11.0
- ypricemagic installed in editable mode

## Required Environment Variables

- `ETHERSCAN_TOKEN` — needed for contract ABI fetching (in `.env`)
- `BROWNIE_NETWORK=mainnet` — needed when running any brownie/ypricemagic code
- `TYPEDENVS_SHUTUP=1` — suppresses noisy warnings

## Worktree Setup

- Worktree at `/Users/bryan/code/ypricemagic-pricing` on branch `feat/stablecoin-pricing`
- Main repo at `/Users/bryan/code/ypricemagic` — do NOT modify (another droid's workspace)
- `.env` copied from main repo to worktree by init.sh

## macOS Quirks

- Full pytest suite fails on macOS (some tests, not all)
- Individual Python scripts importing brownie + y DO work
- Validation happens through ypricemagic-server Docker stack, not local tests

## concurrent.futures.process Workaround

macOS has a low default `RLIMIT_NPROC` that causes `_SafeQueue` to fail with large `max_size`. The workaround patches `__init__` to cap at 32767:
```python
import concurrent.futures.process as cfp
_orig = cfp._SafeQueue.__init__
cfp._SafeQueue.__init__ = lambda self, max_size=0, **kw: _orig(self, min(max_size, 32767), **kw)
```
This must be applied BEFORE importing brownie or pytest.
