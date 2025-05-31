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
    Checks if the given token is the Froyo token on the Fantom network.

    This function converts the input token into a normalized address and then verifies that:
      - The active chain ID equals that of the Fantom network.
      - The normalized token address matches "0x4f85Bbf3B0265DCEd4Ec72ebD0358ccCf190F1B3".

    Note:
      The Froyo token used for identification in this function is hard-coded as
      "0x4f85Bbf3B0265DCEd4Ec72ebD0358ccCf190F1B3" even though the module-level constant POOL is set to
      "0x83E5f18Da720119fF363cF63417628eB0e9fd523". Refer to :func:`~y.convert.to_address` and
      :class:`~y.networks.Network` for more details.

    Args:
        token: An Ethereum address (any valid representation) to check.

    Returns:
        True if the active network is Fantom and the token matches "0x4f85Bbf3B0265DCEd4Ec72ebD0358ccCf190F1B3", False otherwise.

    Examples:
        >>> is_froyo("0x4f85Bbf3B0265DCEd4Ec72ebD0358ccCf190F1B3")
        True
        >>> is_froyo("0x83E5f18Da720119fF363cF63417628eB0e9fd523")
        False
        >>> is_froyo("0x0000000000000000000000000000000000000000")
        False

    See Also:
        :func:`~y.convert.to_address`, :class:`~y.networks.Network`
    """
    return (
        CHAINID == Network.Fantom
        and convert.to_address(token) == "0x4f85Bbf3B0265DCEd4Ec72ebD0358ccCf190F1B3"
    )


@a_sync.a_sync(default="sync")
async def get_price(token: AnyAddressType, block: Optional[Block] = None) -> Optional[UsdPrice]:
    """
    Retrieves the USD price of the Froyo pool token on the Fantom network.

    This asynchronous function uses a raw call to fetch the virtual price of the token,
    but only if the provided token matches the Froyo pool token defined by the module-level constant POOL,
    which is "0x83E5f18Da720119fF363cF63417628eB0e9fd523". If the token does not match, the function
    returns None.

    Note:
      Only a token address matching "0x83E5f18Da720119fF363cF63417628eB0e9fd523" will yield a price.
      See also :func:`~y.utils.raw_calls.raw_call` and :class:`~y.datatypes.UsdPrice` for further details.

    Args:
        token: The Ethereum address of the Froyo pool token.
        block: An optional block number at which to query the price; if omitted, the latest block is used.

    Returns:
        The USD price as a UsdPrice object if the token matches the expected address, otherwise None.

    Examples:
        >>> await get_price("0x83E5f18Da720119fF363cF63417628eB0e9fd523")
        UsdPrice(1.23456789)
        >>> await get_price("0x4f85Bbf3B0265DCEd4Ec72ebD0358ccCf190F1B3")
        None
        >>> await get_price("0x0000000000000000000000000000000000000000")
        None

    See Also:
        :func:`~y.utils.raw_calls.raw_call`, :class:`~y.datatypes.UsdPrice`
    """
    if token != POOL:
        return None
    virtual_price = await raw_call(
        POOL, "get_virtual_price()", block=block, output="int", sync=False
    )
    return UsdPrice(virtual_price / 10**18)
