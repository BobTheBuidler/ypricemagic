
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
        # eth and eth-like
        "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE", # eth
        weth.address,
        # btc and btc-like
        wbtc.address,
        "0xEB4C2781e4ebA804CE9a9803C67d0893436bB27D", # renbtc
        "0xfe18be6b3bd88a2d2a7f928d00292e7a9963cfc6", # sbtc
        # gold tokens
        "0x4922a015c4407F87432B179bb209e125432E4a2A", # xaut
        # other
        "0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e", # yfi
        "0xD5525D397898e5502075Ea5E830d8914f6F0affe", # meme
        "0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2", # mkr
        "0x9cea2eD9e47059260C97d697f82b8A14EfA61EA5", # punk
        "0x69BbE2FA02b4D90A944fF328663667DC32786385", # punk-basic
        "0x23B608675a2B2fB1890d3ABBd85c5775c51691d5", # socks
    ],
    Network.BinanceSmartChain: [
        # eth and eth-like
        weth.address,
        # btc and btc-like
        wbtc.address,
    ],
    Network.Polygon: [
        # eth and eth-like
        weth.address,
        # btc and btc-like
        wbtc.address,
    ],
    Network.Fantom: [
        # eth and eth-like
        weth.address,
        # btc and btc-like
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
        try: # v2
            token_address = raw_call(token_address, 'token()', output='address')
            if token_address in ACCEPTABLE_HIGH_PRICES: return
        except:
            try: # v1
                token_address = raw_call(token_address, 'want()', output='address')
                if token_address in ACCEPTABLE_HIGH_PRICES: return
            except: pass
    
    elif bucket == 'atoken':
        try: # v2
            token_address = raw_call(token_address, 'UNDERLYING_ASSET_ADDRESS()', output='address')
            if token_address in ACCEPTABLE_HIGH_PRICES: return
        except:
            try: # v1
                token_address = raw_call(token_address, 'underlyingAssetAddress()', output='address')
                if token_address in ACCEPTABLE_HIGH_PRICES: return
            except: pass

    elif bucket == 'compound':
        token_address = raw_call(token_address, 'underlying()', output='address')
        if token_address in ACCEPTABLE_HIGH_PRICES: return

    # proceed with sense check

    price_readable = round(price, 4)
    symbol = _symbol(token_address)
    network = Network.name(chain.id)
    logger.warn(f'unusually high price (${price_readable}) returned for {symbol} {token_address} on {network}. This does not necessarily mean that the price is wrong, but you may want to validate the price for yourself before proceeding.')
