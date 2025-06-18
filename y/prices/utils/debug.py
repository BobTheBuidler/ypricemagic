import logging
from typing import Optional

from brownie import chain
import y

# Set up logging similar to scripts/debug-price.py
y_logger = logging.getLogger("y")
y_logger.setLevel(logging.DEBUG)
if not y_logger.hasHandlers():
    y_logger.addHandler(logging.StreamHandler())


def debug_price(token: str, block: Optional[int] = None) -> float:
    """
    Debug token price retrieval.

    Args:
        token (str): The address of the token to debug.
        block (Optional[int]): The block number at which to retrieve the token price.
            If not specified, uses the current block height.

    Returns:
        float: The price of the token at the specified block.

    Raises:
        ValueError: If token is not provided.
    """
    if not token:
        raise ValueError("You must specify a token address to debug.")

    if block is None:
        block = chain.height
        y_logger.warning("No `block` specified, using %s", block)

    price = y.get_price(token, int(block), skip_cache=True)
    y_logger.info("Price for token %s at block %s: %s", token, block, price)
    return price
