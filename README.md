Use this tool to extract historical on-chain price data from an archive node. 

Shoutout to [Banteg](https://github.com/banteg) [(@bantg)](https://twitter.com/bantg) and [nymmrx](https://github.com/nymmrx) [(@nymmrx)](https://twitter.com/nymmrx) for their awesome work on [yearn-exporter](https://github.com/yearn/yearn-exporter) that made this library possible.

To install:
```
pip install ypricemagic
```

To use:
```
from ypricemagic import magic
magic.get_price(token,block)
```

Or:
```
from ypricemagic.magic import get_price
get_price(token,block)
```

You can also import protocol specific modules. For example:
```
from ypricemagic import uniswap
uniswap.get_price(token, block)
```
```
from ypricemagic.compound import get_price
get_price(compoundToken, block)
```
