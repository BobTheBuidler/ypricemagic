Use this tool to extract historical on-chain price data from an archive node. 

Shoutout to [Banteg](https://github.com/banteg) [(@bantg)](https://twitter.com/bantg) and [nymmrx](https://github.com/nymmrx) [(@nymmrx)](https://twitter.com/nymmrx) for their awesome work on [yearn-exporter](https://github.com/yearn/yearn-exporter) that made this library possible.

To install:
```
pip install ypricemagic
```


**Known Issues**  
Make sure you are using Python >= 3.8 and < 3.11  
If you have a PyYaml Issue with 3.4.1 not installing due to an issue with cython, try the following:  
```
pip install wheel
pip install --no-build-isolation "Cython<3" "pyyaml==5.4.1"
```
then try again
`
pip install ypricemagic
`

To use:
```
from y import get_price
get_price(token,block)
```

Or:
```
from y import get_prices
get_prices(tokens, block)
```

You can also use ypricemagic asynchronously
```
get_price(token, block, sync=False)

You can also import protocol specific modules. For example:
```
from ypricemagic import uniswap
uniswap.get_price(token, block)
```
```
from ypricemagic.compound import get_price
get_price(compoundToken, block)
```
These are not 'supported' per se and are subject to change at any time. But they can come in handy.

Enjoy!
