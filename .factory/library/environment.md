# Environment

## Python
- Python 3.12 via /Users/bryan/code/ypricemagic-server/.venv
- Install editable: `uv pip install -e /Users/bryan/code/ypricemagic-pool-index --python /Users/bryan/code/ypricemagic-server/.venv/bin/python`
- uv available at /Users/bryan/.local/bin/uv (v0.10.5)

## macOS SemLock Workaround
Required for ANY Python script that imports ypricemagic on macOS:
```python
import concurrent.futures.process as cfp
_orig = cfp._SafeQueue.__init__
cfp._SafeQueue.__init__ = lambda self, max_size=0, **kw: _orig(self, min(max_size, 32767), **kw)
```
This must be at the TOP of any script, before importing brownie/ypricemagic.

## RPC
- Brownie network "mainnet" configured, points to local node at 10.11.12.43:8545
- Connect with: `BROWNIE_NETWORK=mainnet` env var + `brownie.network.connect('mainnet')`

## Database
- SQLite at ~/.ypricemagic/ypricemagic.sqlite (pool event cache)
- Do not delete — contains cached PairCreated/PoolCreated events

## Tests
- Tests do NOT run on Mac (known issue)
- Write tests for CI (Linux), don't attempt to run locally
- Follow existing patterns: @async_test, @mainnet_only, hardcoded blocks
