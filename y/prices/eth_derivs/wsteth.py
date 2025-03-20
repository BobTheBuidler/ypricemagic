import logging
from decimal import Decimal
from typing import Optional

import a_sync
from a_sync import cgather

from y import ENVIRONMENT_VARIABLES as ENVS
from y import convert
from y.constants import CHAINID, CONNECTED_TO_MAINNET, weth
from y.datatypes import AnyAddressType, Block, UsdPrice
from y.networks import Network
from y.prices import magic
from y.utils.raw_calls import raw_call

logger = logging.getLogger(__name__)


class wstEth(a_sync.ASyncGenericBase):
    """
    A class to interact with the wstETH token on Ethereum Mainnet.

    This class provides methods to fetch the price of wstETH in USD, leveraging the `a_sync` library
    to support both synchronous and asynchronous operations.

    Examples:
        Initialize the class with asynchronous behavior:

        >>> wsteth = wstEth(asynchronous=True)
        >>> price = await wsteth.get_price(block=12345678)

        Initialize the class with synchronous behavior:

        >>> wsteth_sync = wstEth(asynchronous=False)
        >>> price_sync = wsteth_sync.get_price(block=12345678)

    See Also:
        - :class:`a_sync.ASyncGenericBase`
    """

    def __init__(self, *, asynchronous: bool = False) -> None:
        """
        Initialize the wstEth class with optional asynchronous behavior.

        Args:
            asynchronous: A boolean indicating if the operations should be asynchronous.

        Attributes:
            address: The address of the wstETH token on the Ethereum Mainnet, or None if not on Mainnet.
            wrapped_for_curve: The address of the wrapped version of wstETH for Curve on the Ethereum Mainnet, or None if not on Mainnet.
        """
        super().__init__()
        self.asynchronous = asynchronous
        try:
            self.address = {
                Network.Mainnet: "0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0"
            }[CHAINID]
            self.wrapped_for_curve = {
                Network.Mainnet: "0xb82CFa4325568748506dC7cF267857Ff1e3b8d39"
            }[CHAINID]
        except KeyError:
            self.address = None

    async def get_price(
        self, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE
    ) -> UsdPrice:
        """
        Fetch the price of wstETH in USD.

        This method retrieves the price of wstETH by calling the `stEthPerToken` method
        on the wstETH contract using :func:`y.utils.raw_calls.raw_call` and fetching the current price
        of WETH using :func:`y.prices.magic.get_price`.

        Args:
            block: The block number at which to fetch the price.
            skip_cache: Whether to skip the cache when fetching the price.

        Examples:
            Fetch the price asynchronously:

            >>> price = await wsteth.get_price(block=12345678)

            Fetch the price synchronously:

            >>> price_sync = wsteth_sync.get_price(block=12345678)

        See Also:
            - :func:`y.utils.raw_calls.raw_call`
            - :func:`y.prices.magic.get_price`
        """
        share_price, weth_price = await cgather(
            raw_call(
                self.address, "stEthPerToken()", output="int", block=block, sync=False
            ),
            magic.get_price(weth, block, skip_cache=skip_cache, sync=False),
        )
        share_price /= Decimal(10**18)
        return UsdPrice(share_price * Decimal(float(weth_price)))


wsteth = wstEth(asynchronous=True)

if CONNECTED_TO_MAINNET:
    _WSTETH_ADDRS = (wsteth.address, wsteth.wrapped_for_curve)


def is_wsteth(address: AnyAddressType) -> bool:
    """
    Check if a given address is wstETH or its wrapped version for Curve on Ethereum Mainnet.

    This function verifies the network ID to ensure it is operating on the Ethereum Mainnet
    before performing the address comparison.

    Args:
        address: The address to check.

    Examples:
        Check if an address is wstETH:

        >>> is_wsteth("0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0")
        True

        Check if an address is not wstETH:

        >>> is_wsteth("0x0000000000000000000000000000000000000000")
        False

    See Also:
        - :class:`wstEth`
    """
    return CONNECTED_TO_MAINNET and convert.to_address(address) in _WSTETH_ADDRS
