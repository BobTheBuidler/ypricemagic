import logging
import os

from brownie import chain

import y
from y.prices.stable_swap.curve import CurveRegistry, curve

y_logger = logging.getLogger("y")
y_logger.setLevel(logging.DEBUG)
y_logger.addHandler(logging.StreamHandler())

curve: CurveRegistry


def main():
    """Main function to debug a specific Curve pool.

    This script checks if a specified token address corresponds to a Curve pool.
    It requires setting the `BAD` environment variable to specify the token address to debug.
    Optionally, the `BLOCK` environment variable can be set to specify the block number.

    Raises:
        ValueError: If the `BAD` environment variable is not set.

    Examples:
        To debug a Curve pool, set the environment variables and run the script:

        .. code-block:: bash

            export BAD=<pool_address>
            export BLOCK=<block_number>  # Optional
            python debug-curve.py

        If `BLOCK` is not specified, the script will use the current block height.

    See Also:
        - :mod:`y.prices.stable_swap.curve` for more details on Curve pool interactions.
    """
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
