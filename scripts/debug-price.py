
import logging
import os

from brownie import chain

from y import get_price,ERC20, Network


def main():
    bad = os.environ.get("BAD")
    block = os.environ.get("BLOCK")
    if not bad:
        raise ValueError("You must specify a token to debug by setting BAD env var")
    if block:
        block = int(block)
    else:
        block = chain.height
        print('No block specified, using {block}')

    print(f"Debugging price for {ERC20(bad).symbol} {bad} on {Network.name()} at block {block}")

    logger = logging.getLogger('y')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    if not bool(os.environ.get('SHOW_EVENTS')):
        logger = logging.getLogger('y.prices.dex.uniswap.v2.Pools').setLevel(logging.INFO)
        logger = logging.getLogger('y.prices.dex.uniswap.v3.Pools').setLevel(logging.INFO)
        logger = logging.getLogger('y.prices.dex.uniswap.velodrome.Pools').setLevel(logging.INFO)
    get_price(bad, int(block))
