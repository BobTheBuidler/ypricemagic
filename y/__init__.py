import os

from brownie import network

from y import time
from y.constants import dai, usdc, wbtc, weth
from y.contracts import Contract, has_method, has_methods
from y.erc20 import decimals, totalSupply, totalSupplyReadable
from y.exceptions import (CalldataPreparationError, CallReverted,
                          ContractNotVerified, MessedUpBrownieContract,
                          NetworkNotSpecified, NonStandardERC20,
                          NotABalancerV2Pool, NotAUniswapV2Pool, PriceError,
                          UnsupportedNetwork)
from y.networks import Network
from y.prices import magic
from y.prices.magic import (get_price, get_price_async, get_prices,
                            get_prices_async)
from y.utils.dank_mids import dank_w3
from y.utils.multicall import fetch_multicall
from y.utils.raw_calls import balanceOf as balanceOf
from y.utils.raw_calls import balanceOf_async, raw_call

__all__ = [
    ### you can reach the below functions, classes, and variables using ###
    ###  `y.__name__` or `from y import __name__`.  ###

    # contract stuff
    'Contract',
    'has_method',
    'has_methods',

    # network stuff
    'Network',

    # magic
    'magic',

    # prices
    'get_price',
    'get_prices',

    # constants
    'weth',
    'dai',
    'usdc',
    'wbtc',

    # multicall
    'fetch_multicall',

    # raw calls
    'decimals',
    'symbol',
    'balanceOf',
    'balanceOfReadable',
    'totalSupply',
    'totalSupplyReadable',
    'raw_call',

    # time
    'time',
]

if not network.is_connected():
    if 'BROWNIE_NETWORK_ID' not in os.environ:
        raise NetworkNotSpecified('In order to use pricemagic outside of a brownie project directory, you will need to set $BROWNIE_NETWORK_ID environment variable with the id of your preferred brownie network connection.')
    network.connect(os.environ['BROWNIE_NETWORK_ID'])
