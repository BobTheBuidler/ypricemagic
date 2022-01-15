import os

from brownie import network
from y.constants import dai, usdc, wbtc, weth
from y.contracts import Contract
from y.networks import Network

from ypricemagic.utils.multicall import fetch_multicall
from ypricemagic.utils.raw_calls import (_balanceOf, _balanceOfReadable,
                                         _decimals, _symbol, _totalSupply,
                                         _totalSupplyReadable)

__all__ = [
    ### you can reach the below functions, classes, and variables using ###
    ###  `ypricemagic.__name__` or `from ypricemagic import __name__`.  ###

    # contract stuff
    'Contract',

    # network stuff
    'Network',

    # constants
    'weth',
    'dai',
    'usdc',
    'wbtc',

    # multicall
    'fetch_multicall',

    # raw calls
    '_decimals',
    '_symbol',
    '_balanceOf',
    '_balanceOfReadable',
    '_totalSupply',
    '_totalSupplyReadable',
]

if not network.is_connected():
    try:
        network_name = os.environ['BROWNIE_NETWORK_ID']
    except KeyError:
        raise KeyError('In order to use pricemagic outside of a brownie project directory, you will need to set $BROWNIE_NETWORK_ID environment variable with the id of your preferred brownie network connection.')
    network.connect(network_name)


