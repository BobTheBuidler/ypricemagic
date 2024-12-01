import logging
from typing import Optional

import a_sync
from brownie import chain

from y import convert
from y.datatypes import AnyAddressType, Block, UsdPrice
from y.networks import Network
from y.utils.raw_calls import raw_call

logger = logging.getLogger(__name__)

POOLS = {
    Network.BinanceSmartChain: {
        "0x86aFa7ff694Ab8C985b79733745662760e454169": "0xF16D312d119c13dD27fD0dC814b0bCdcaAa62dfD",  # Belt.fi bDAI/bUSDC/bUSDT/bBUSD
        "0x9cb73F20164e399958261c289Eb5F9846f4D1404": "0xAEA4f7dcd172997947809CE6F12018a6D5c1E8b6",  # 4Belt
    },
}.get(chain.id, {})


def is_belt_lp(token: AnyAddressType) -> bool:
    """Check if a token is a Belt LP token.

    Args:
        token: The address of the token to check.

    Returns:
        True if the token is a Belt LP token, False otherwise.

    Examples:
        >>> is_belt_lp("0x86aFa7ff694Ab8C985b79733745662760e454169")
        True
        >>> is_belt_lp("0x0000000000000000000000000000000000000000")
        False

    See Also:
        :data:`POOLS` for the list of recognized Belt LP tokens.
    """
    address = convert.to_address(token)
    return address in POOLS


@a_sync.a_sync(default="sync")
async def get_price(token: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
    """Get the price of a Belt LP token in USD.

    This function retrieves the virtual price of a Belt LP token from its associated pool
    and converts it to a USD price.

    Args:
        token: The address of the Belt LP token.
        block: The block number at which to fetch the price. Defaults to the latest block.

    Raises:
        KeyError: If the token is not found in the :data:`POOLS` dictionary.

    Examples:
        >>> await get_price("0x86aFa7ff694Ab8C985b79733745662760e454169")
        UsdPrice(1.23456789)
        >>> await get_price("0x9cb73F20164e399958261c289Eb5F9846f4D1404", block=12345678)
        UsdPrice(1.23456789)

    See Also:
        :func:`is_belt_lp` to check if a token is a Belt LP token.
    """
    address = await convert.to_address_async(token)
    pool = POOLS[address]
    virtual_price = await raw_call(
        pool, "get_virtual_price()", output="int", block=block, sync=False
    )
    return UsdPrice(virtual_price / 10**18)
