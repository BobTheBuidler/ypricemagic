from typing import Optional

import a_sync
from brownie import chain
from eth_typing import ChecksumAddress

from y import ENVIRONMENT_VARIABLES as ENVS
from y.datatypes import Block, UsdPrice
from y.networks import Network
from y.prices import magic

MAPPING = {
    Network.Mainnet: {
        "0x4da27a545c0c5B758a6BA100e3a049001de870f5": "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9",  # stkaave -> aave
        "0x27D22A7648e955E510a40bDb058333E9190d12D4": "0x0cec1a9154ff802e7934fc916ed7ca50bde6844e",  # ppool -> pool
        # TODO: algorithmically get gauges
        "0xcF5136C67fA8A375BaBbDf13c0307EF994b5681D": "0x425BfB93370F14fF525aDb6EaEAcfE1f4e3b5802",  # sdai-usdm-gauge -> sdai-usdm
        "0x590f7e2b211Fa5Ff7840Dd3c425B543363797701": "0x5756bbdDC03DaB01a3900F01Fb15641C3bfcc457",  # YFImkUSD-gauge -> YFImkUSD
    },
}.get(chain.id, {})


def is_one_to_one_token(token_address: ChecksumAddress) -> bool:
    """
    Check if a token address is a one-to-one token.

    Args:
        token_address: The address of the token to check.

    Returns:
        True if the token is a one-to-one token, False otherwise.

    Examples:
        >>> is_one_to_one_token("0x4da27a545c0c5B758a6BA100e3a049001de870f5")
        True

        >>> is_one_to_one_token("0x0000000000000000000000000000000000000000")
        False
    """
    return token_address in MAPPING


@a_sync.a_sync(default="sync")
async def get_price(
    token_address: ChecksumAddress,
    block: Optional[Block] = None,
    skip_cache: bool = ENVS.SKIP_CACHE,
) -> UsdPrice:
    """
    Get the USD price of a one-to-one token by mapping it to its corresponding token.

    This function supports both synchronous and asynchronous execution.

    Args:
        token_address: The address of the token to get the price for.
        block: The block number to get the price at. Defaults to the latest block.
        skip_cache: Whether to skip the cache when fetching the price. Defaults to the value of `ENVS.SKIP_CACHE`.

    Returns:
        The USD price of the token.

    Examples:
        Synchronous usage:
        >>> get_price("0x4da27a545c0c5B758a6BA100e3a049001de870f5")

        Asynchronous usage:
        >>> await get_price("0x4da27a545c0c5B758a6BA100e3a049001de870f5", sync=False)

    See Also:
        - :func:`y.prices.magic.get_price` for the underlying price fetching logic.
    """
    return await magic.get_price(
        MAPPING[token_address], block=block, skip_cache=skip_cache, sync=False
    )
