
import logging
import os

from brownie import chain

import y
from y.prices.stable_swap.curve import CurveRegistry, curve

y_logger = logging.getLogger('y')
y_logger.setLevel(logging.DEBUG)
y_logger.addHandler(logging.StreamHandler())

curve: CurveRegistry

def main():
    BAD = os.environ.get("BAD")
    BLOCK = os.environ.get("BLOCK")
    if not BAD:
        raise ValueError("You must specify a token to debug by setting BAD env var")
    if not BLOCK:
        BLOCK = chain.height
        y_logger.warning("no BLOCK specified, using %s", BLOCK)
    if curve.get_pool(BAD, sync=True):
        curve.get_price(BAD, int(BLOCK), sync=True)
    else:
        y_logger.info("%s is not a curve pool", BAD)
    
