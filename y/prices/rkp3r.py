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
    Get the price of the KP3R token and apply a discount to calculate the RKP3R token price.

    This function retrieves the price of the KP3R token and applies a discount
    specific to the RKP3R token.

    Args:
        address: The address of the token.
        block: The block number to query the price at.
        skip_cache: Whether to skip the cache when retrieving the price.

    Returns:
        The discounted price of the RKP3R token.

    Examples:
        >>> await get_price("0xEdB67Ee1B171c4eC66E6c10EC43EDBbA20FaE8e9")
        Decimal('123.45')

    See Also:
        - :func:`y.prices.magic.get_price`
    """
    price, discount = await cgather(
        magic.get_price(KP3R, block=block, skip_cache=skip_cache, sync=False),
        get_discount(block),
    )
    return Decimal(price) * (100 - discount) / 100


async def get_discount(block: Optional[Block] = None) -> Decimal:
    """
    Retrieve the discount for the RKP3R token from the contract.

    Args:
        block: The block number to query the discount at.

    Returns:
        The discount as a percentage.

    Examples:
        >>> await get_discount()
        Decimal('5.0')

    See Also:
        - :class:`y.contracts.Contract`
    """
    rkp3r = await Contract.coroutine(RKP3R)
    discount = Decimal(await rkp3r.discount.coroutine(block_identifier=block))
    logger.debug("discount: %s", discount)
    return discount
