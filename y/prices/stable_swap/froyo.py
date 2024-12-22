import logging
from typing import Optional

import a_sync

from y import convert
from y.constants import CHAINID
from y.datatypes import AnyAddressType, Block, UsdPrice
from y.networks import Network
from y.utils.raw_calls import raw_call

logger = logging.getLogger(__name__)

POOL = "0x83E5f18Da720119fF363cF63417628eB0e9fd523"


def is_froyo(token: AnyAddressType) -> bool:
    """
    Check if a given token is the Froyo token on the Fantom network.

    Args:
        token: The token address to check.

    Returns:
        True if the token is the Froyo token on Fantom, False otherwise.

    Examples:
        >>> is_froyo("0x4f85Bbf3B0265DCEd4Ec72ebD0358ccCf190F1B3")
        True
        >>> is_froyo("0x0000000000000000000000000000000000000000")
        False

    See Also:
        - :func:`y.convert.to_address` for address conversion.
        - :class:`y.networks.Network` for network identification.
    """
    address = convert.to_address(token)
    return (
        CHAINID == Network.Fantom
        and address == "0x4f85Bbf3B0265DCEd4Ec72ebD0358ccCf190F1B3"
    )


@a_sync.a_sync(default="sync")
async def get_price(
    token: AnyAddressType, block: Optional[Block] = None
) -> Optional[UsdPrice]:
    """
    Get the USD price of the Froyo pool token on the Fantom network.

    This function retrieves the virtual price of the Froyo pool token if the provided
    token address matches the Froyo pool address on the Fantom network. The price is
    returned as a :class:`y.datatypes.UsdPrice` object.

    Args:
        token: The token address to get the price for.
        block: The block number to query the price at, defaults to the latest block.

    Returns:
        The USD price of the Froyo pool token, or None if the token is not the Froyo pool.

    Examples:
        >>> await get_price("0x83E5f18Da720119fF363cF63417628eB0e9fd523")
        UsdPrice(1.23456789)
        >>> await get_price("0x0000000000000000000000000000000000000000")
        None

    See Also:
        - :func:`y.utils.raw_calls.raw_call` for making raw contract calls.
        - :class:`y.datatypes.UsdPrice` for the price representation.
    """
    if token != POOL:
        return None
    virtual_price = await raw_call(
        POOL, "get_virtual_price()", block=block, output="int", sync=False
    )
    return UsdPrice(virtual_price / 10**18)
