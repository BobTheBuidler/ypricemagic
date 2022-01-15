import os

from brownie import network
from ypricemagic import magic
from ypricemagic.magic import get_price, get_prices
from ypricemagic.utils.multicall import fetch_multicall
from ypricemagic.utils.raw_calls import _balanceOf as balanceOf
from ypricemagic.utils.raw_calls import _balanceOfReadable as balanceOfReadable
from ypricemagic.utils.raw_calls import _symbol as symbol
from ypricemagic.utils.raw_calls import raw_call

from y import time
from y.constants import dai, usdc, wbtc, weth
from y.contracts import Contract
from y.erc20 import decimals, totalSupply, totalSupplyReadable
from y.exceptions import *
from y.networks import Network

__all__ = [
    ### you can reach the below functions, classes, and variables using ###
    ###  `y.__name__` or `from y import __name__`.  ###

    # contract stuff
    'Contract',

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
    try:
        network_name = os.environ['BROWNIE_NETWORK_ID']
    except KeyError:
        raise KeyError('In order to use pricemagic outside of a brownie project directory, you will need to set $BROWNIE_NETWORK_ID environment variable with the id of your preferred brownie network connection.')
    network.connect(network_name)


