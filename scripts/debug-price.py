
import logging
import os

import y

def main():
    BAD = os.environ.get("BAD")
    BLOCK = os.environ.get("BLOCK")
    if not BAD:
        raise ValueError("You must specify a token to debug by setting BAD env var")
    if not BLOCK:
        raise ValueError("You must specify a block to debug at by setting BLOCK env var")
    logger = logging.getLogger('y')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    y.get_price(BAD, int(BLOCK))
