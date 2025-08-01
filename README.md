## Summary
Use this tool to extract historical on-chain price data from an archive node.

ypricemagic is built to work seamlessly with both sync and async Python codebases using the [ez-a-sync framework](https://github.com/BobTheBuidler/ez-a-sync).

## Requirements
- Python 3.9 or higher.
- At least 16GB of RAM.

## Prerequisites
- First, you will need to bring your own archive node. This can be one you run yourself, or one from one of the common providers (Tenderly, Alchemy, QuickNode, etc.)
- You will also need an auth token for [Etherscan](https://etherscan.io/)'s API. Follow their [guide](https://docs.etherscan.io/etherscan-v2/getting-an-api-key) to get your key, and set env var `ETHERSCAN_TOKEN` with its value.

## Installation
ypricemagic is published on [PyPI](https://pypi.org/). Simply install it just as you would any other library.
```
pip install ypricemagic
```

## Network Configuration
ypricemagic utilizes the Brownie framework for Ethereum smart contract interactions. As such, it's essential that users configure a Brownie network to use their chosen RPC. Ensure you have access to an Ethereum node (e.g., through Infura or Alchemy) and add the provided API endpoint to your Brownie network configuration.

Refer to the [Brownie documentation on network management](https://eth-brownie.readthedocs.io/en/stable/network-management.html) for detailed guidance on setting up your networks. This setup is critical, as without it, ypricemagic will not be able to communicate with your RPC. 

## Usage

There are 2 main entrypoints to ypricemagic, 
[y.get_price](https://bobthebuidler.github.io/ypricemagic/source/y.html#y.get_price) and [y.get_prices](https://bobthebuidler.github.io/ypricemagic/source/y.html#y.get_prices).

```python
from y import get_price
price = get_price(token,block)

# OR

from y import get_prices
prices = get_prices(tokens, block)
```

You can also use ypricemagic asynchronously:
```python
price = await get_price(token, block, sync=False)

# OR

prices = await get_prices(tokens, block, sync=False)
```

See the [docs](https://bobthebuidler.github.io/ypricemagic) for more usage information.

## Extras
You can also import protocol specific modules. For example:
```python
from ypricemagic import uniswap
uniswap.get_price(token, block)
```
```python
from ypricemagic.compound import get_price
get_price(compoundToken, block)
```
These are not 'supported' per se and are subject to change at any time. But they can come in handy. The [not-very-organized docs site](https://bobthebuidler.github.io/ypricemagic) will be your friend here.

Enjoy!


### Shoutouts
Shoutout to [Banteg](https://github.com/banteg) [(@bantg)](https://twitter.com/bantg) and [nymmrx](https://github.com/nymmrx) [(@nymmrx)](https://twitter.com/nymmrx) for their awesome work on [yearn-exporter](https://github.com/yearn/yearn-exporter) that made this library possible.
