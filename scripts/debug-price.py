import os
from logging import DEBUG, INFO, StreamHandler, getLogger

from brownie import chain

import y
from y.prices.stable_swap.curve import startup_logger

y_logger = getLogger("y")
y_logger.setLevel(DEBUG)
y_logger.addHandler(StreamHandler())
startup_logger.setLevel(INFO)
getLogger("y._db.common").setLevel(INFO)
getLogger("y._db.utils.bulk").setLevel(INFO)
getLogger("y._db.utils.logs").setLevel(INFO)
getLogger("y.classes.common").setLevel(INFO)


def main():
    """
    Main function to debug token price retrieval.

    This script retrieves the price of a specified token at a given block height.
    The token and block height are specified via environment variables.

    Environment Variables:
        BAD: The address of the token to debug. This variable must be set.
             If not set, a ValueError will be raised.
        BLOCK: The block number at which to retrieve the token price. If not specified,
               the current block height is used.

    Raises:
        ValueError: If the BAD environment variable is not set.

    Examples:
        To debug the price of a token with address '0xTokenAddress' at block 1234567:
        ```
        export BAD=0xTokenAddress
        export BLOCK=1234567
        python debug-price.py
        ```

        To debug the price of a token with address '0xTokenAddress' at the current block:
        ```
        export BAD=0xTokenAddress
        python debug-price.py
        ```

    See Also:
        - :func:`y.get_price`: For more details on how the price is retrieved.
    """
    BAD = os.environ.get("BAD")
    BLOCK = os.environ.get("BLOCK")
    if not BAD:
        raise ValueError("You must specify a token to debug by setting `BAD` env var")
    if not BLOCK:
        BLOCK = chain.height
        y_logger.warning("no `BLOCK` specified, using %s", BLOCK)
    y.get_price(BAD, int(BLOCK), skip_cache=True)
