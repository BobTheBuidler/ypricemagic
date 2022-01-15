
import logging
from typing import Union

from brownie import chain
from ypricemagic.constants import weth, wbtc
from ypricemagic.networks import Network
from ypricemagic.utils.raw_calls import _symbol, raw_call

logger = logging.getLogger(__name__)

# This module is far from perfect, but provides an acceptable way to validate some of the prices returned by `get_price`

ACCEPTABLE_HIGH_PRICES = {
    Network.Mainnet: [
        weth.address,
        wbtc.address,
    ],
    Network.BinanceSmartChain: [
        weth.address,
        wbtc.address,
    ],
    Network.Polygon: [
        weth.address,
        wbtc.address,
    ],
    Network.Fantom: [
        weth.address,
        wbtc.address,
    ],
}.get(chain.id, [])

def _sense_check(
    token_address: str, 
    price: float,
    bucket: Union[str, None]
    ):

    # if price is in "normal" range, exit sense check

    if price < 1000:
        return
    
    # if we've already validated that the token should have a high price, exit sense check

    if token_address in ACCEPTABLE_HIGH_PRICES:
        return

    # for some token types, its normal to have a crazy high nominal price
    # we can skip the sense check for those

    if bucket == 'uni or uni-like lp':
        return

    # for wrapped tokens, if the base token is in `ACCEPTABLE_HIGH_PRICES` we can exit the sense check

    elif bucket == 'yearn or yearn-like':
        token_address = raw_call(token_address, 'token()', output='address')
        if token_address in ACCEPTABLE_HIGH_PRICES: return

    # proceed with sense check

    price_readable = round(price, 4)
    symbol = _symbol(token_address)
    network = Network.name(chain.id)
    logger.warn(f'unusually high price (${price_readable}) returned for {symbol} on {network}. This does not necessarily mean that the price is wrong, but you may want to validate the price for yourself before proceeding.')
