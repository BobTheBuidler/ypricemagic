
## Adding new protocols

I will add info to this document over time. For now, it will be sparse. Very sparse.

First thing you want to do when adding support for a new token is determine what is actually is.

Is it a LP token? 

If yes:
    - Check the methods on the LP token. Does it have 'token0', 'token1', and 'getAmountOut'? If yes, it sounds like a uni v2 fork. Look to see if you can find a router address and a factory address for the protocol. Does the router have method 'getAmountsOut' and does the factory emit 'PairCreated' events? If so, you're looking at a uni fork. You should add the factory and router address to y/prices/dex/uniswap/v2_forks.py

If no:
    - I'll write out a process when we get here