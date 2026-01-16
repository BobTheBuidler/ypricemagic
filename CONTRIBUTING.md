
## y.stuck? logger

ypricemagic wraps many long-running async coroutines with `y._decorators.stuck_coro_debugger`, which is a thin wrapper around `a_sync.debugging.stuck_coro_debugger`. That wrapper uses a dedicated logger named `y.stuck?`.

What it does:
- It only runs when the logger is enabled for DEBUG.
- After a coroutine has been running for 5 minutes, it logs `module.function still executing after Xm with args ... kwargs ...` every 5 minutes until completion.

Enable it locally when debugging slow RPCs or stuck price fetches:
```python
import logging

logging.basicConfig(level=logging.INFO)
logging.getLogger("y.stuck?").setLevel(logging.DEBUG)
```

If you add new async RPC or price-fetching functions that might stall, prefer `@stuck_coro_debugger` from `y._decorators` so this logger stays consistent across the codebase.

## Adding new protocols

I will add info to this document over time. For now, it will be sparse. Very sparse.

First thing you want to do when adding support for a new token is determine what is actually is.

Is it a LP token? 

If yes:
    - Check the methods on the LP token. Does it have 'token0', 'token1', and 'getAmountOut'? If yes, it sounds like a uni v2 fork. Look to see if you can find a router address and a factory address for the protocol. Does the router have method 'getAmountsOut' and does the factory emit 'PairCreated' events? If so, you're looking at a uni fork. You should add the factory and router address to y/prices/dex/uniswap/v2_forks.py

If no:
    - I'll write out a process when we get here
