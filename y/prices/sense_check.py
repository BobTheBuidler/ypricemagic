
import logging

from brownie import chain
from ypricemagic.constants import weth, wbtc
from ypricemagic.networks import Network
from ypricemagic.price_modules import yearn
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
    price: float
    ):

    if yearn.is_yearn_vault(token_address):
        token_address = raw_call(token_address, 'token()', output='address')

    if price > 1000 and token_address not in ACCEPTABLE_HIGH_PRICES:
        price_readable = round(price, 4)
        symbol = _symbol(token_address)
        network = Network.name(chain.id)
        logger.warn(f'unusually high price (${price_readable}) returned for {symbol} on {network}. This does not necessarily mean that the price is wrong, but you may want to validate the price for yourself before proceeding.')
