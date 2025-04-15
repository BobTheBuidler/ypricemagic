import logging
from decimal import Decimal
from typing import Optional

import a_sync
from a_sync import cgather

from y import ENVIRONMENT_VARIABLES as ENVS
from y.constants import CONNECTED_TO_MAINNET
from y.contracts import Contract
from y.datatypes import Address, Block
from y.prices import magic

logger = logging.getLogger(__name__)

KP3R = "0x1cEB5cB57C4D4E2b2433641b95Dd330A33185A44"
RKP3R = "0xEdB67Ee1B171c4eC66E6c10EC43EDBbA20FaE8e9"


def is_rkp3r(address: Address) -> bool:
    """
    Check if the given address is the RKP3R token on the Ethereum Mainnet.

    Args:
        address: The address to check.

    Returns:
        True if the address is RKP3R on Mainnet, False otherwise.

    Examples:
        >>> is_rkp3r("0xEdB67Ee1B171c4eC66E6c10EC43EDBbA20FaE8e9")
        True
        >>> is_rkp3r("0x1cEB5cB57C4D4E2b2433641b95Dd330A33185A44")
        False
    """
    return CONNECTED_TO_MAINNET and address == RKP3R


@a_sync.a_sync(default="sync")
async def get_price(
    address: Address, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE
) -> Decimal:
    """
    Get the discounted price of the RKP3R token based on the underlying KP3R token price.

    Note that the supplied ``address`` parameter is provided only for interface consistency and is ignored.
    The function always uses the constant KP3R address to retrieve the price via
    :func:`~y.prices.magic.get_price` and then applies a discount (obtained via
    :func:`~y.prices.rkp3r.get_discount`) to compute the final RKP3R price.

    Args:
        address: Ignored. Provided solely for interface consistency.
        block: The block number to query the price at.
        skip_cache: Whether to skip the cache when retrieving the price.

    Returns:
        The discounted price of the RKP3R token.

    Examples:
        >>> # Example when using the RKP3R address (address parameter is ignored)
        >>> price = await get_price("0xEdB67Ee1B171c4eC66E6c10EC43EDBbA20FaE8e9")
        >>> print(price)
        Decimal('123.45')
        >>>
        >>> # Example when using any other token address (it is ignored in the calculation)
        >>> price = await get_price("0xSomeOtherAddress")
        >>> print(price)
        Decimal('123.45')

    See Also:
        - :func:`~y.prices.magic.get_price`
        - :func:`~y.prices.rkp3r.get_discount`
    """
    price, discount = await cgather(
        magic.get_price(KP3R, block=block, skip_cache=skip_cache, sync=False),
        get_discount(block),
    )
    return Decimal(price) * (100 - discount) / 100


async def get_discount(block: Optional[Block] = None) -> Decimal:
    """
    Retrieve the discount percentage for the RKP3R token from its contract.

    This function queries the discount value stored in the RKP3R token contract at the specified block.

    Args:
        block: The block number at which to query the discount.

    Returns:
        The discount as a percentage.

    Examples:
        >>> discount = await get_discount()
        >>> print(discount)
        Decimal('5.0')

    See Also:
        - :class:`~y.contracts.Contract`
    """
    rkp3r = await Contract.coroutine(RKP3R)
    discount = Decimal(await rkp3r.discount.coroutine(block_identifier=block))
    logger.debug("discount: %s", discount)
    return discount
