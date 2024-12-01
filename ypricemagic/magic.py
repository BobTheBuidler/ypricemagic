import logging
from typing import Optional

from y import magic
from y.datatypes import AnyAddressType, Block, UsdPrice

logger = logging.getLogger(__name__)


def get_price(token: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
    """
    Retrieve the USD price of a given token at a specific block.

    This function serves as a wrapper around `y.magic.get_price` and provides a warning
    about the migration from `ypricemagic` to `y`. The `y` module offers the same functionality
    with additional features.

    .. warning::
        `ypricemagic` is in the process of being migrated to `y`.
        `y` can do all of the same old stuff you expect, plus some new stuff you may or may not need.
        This method still works for now, but will be removed soon.
        Please update your scripts to use `y.magic.get_price(token, block)`.

    Args:
        token: The address of the token to get the price for.
        block: The block number to get the price at. If not provided, the latest block is used.

    Examples:
        >>> from ypricemagic.magic import get_price
        >>> price = get_price("0x6B175474E89094C44Da98b954EedeAC495271d0F")
        >>> print(price)

        >>> price_at_block = get_price("0x6B175474E89094C44Da98b954EedeAC495271d0F", block=12345678)
        >>> print(price_at_block)

    See Also:
        - :func:`y.magic.get_price` for the recommended function to use.
    """
    logger.warning(
        "ypricemagic is in the process of being migrated to y."
        "y can do all of the same old stuff you expect, plus some new stuff you may or may not need."
        "This method still works for now, but will be removed soon."
        "Please update your scripts to use `y.magic.get_price(token, block)`."
    )
    return magic.get_price(token, block)
