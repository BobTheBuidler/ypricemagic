
import logging
import os

from brownie import chain

import y


def main():
    BAD = os.environ.get("BAD")
    BLOCK = os.environ.get("BLOCK")
    if not BAD:
        raise ValueError("You must specify a token to debug by setting BAD env var")
    if not BLOCK:
        BLOCK = chain.height
        logger.warning("no BLOCK specified, using %s", BLOCK)
        raise ValueError("You must specify a block to debug at by setting BLOCK env var")
    logger = logging.getLogger('y')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    y.get_price(BAD, int(BLOCK), skip_cache=True)
