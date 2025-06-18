import os
from y.prices.utils.debug import debug_price


def main():
    """
    Main function to debug token price retrieval.

    This script retrieves the price of a specified token at a given block height.
    The token and block height are specified via environment variables.

    Environment Variables:
        BAD: The address of the token to debug. This variable must be set.
        BLOCK: The block number at which to retrieve the token price. If not specified,
               the current block height is used.

    Raises:
        ValueError: If the BAD environment variable is not set.
    """
    BAD = os.environ.get("BAD")
    BLOCK = os.environ.get("BLOCK")
    if not BAD:
        raise ValueError("You must specify a token to debug by setting `BAD` env var")
    block = int(BLOCK) if BLOCK else None
    debug_price(BAD, block)
