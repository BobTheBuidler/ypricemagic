import logging
from decimal import Decimal
from typing import Optional

import a_sync
from a_sync import igather

from y import ENVIRONMENT_VARIABLES as ENVS
from y import convert
from y.classes.common import ERC20
from y.contracts import has_methods
from y.datatypes import AnyAddressType, Block, UsdPrice
from y.prices import magic
from y.utils import gather_methods

logger = logging.getLogger(__name__)


@a_sync.a_sync(default="sync", ram_cache_ttl=5 * 60)
async def is_ib_token(token: AnyAddressType) -> bool:
    """
    Determines if the given token address is an Iron Bank token.

    Args:
        token: The address of the token to check.

    Returns:
        True if the token is an Iron Bank token, False otherwise.

    Example:
        >>> is_ib = is_ib_token("0x41c84c0e2EE0b740Cf0d31F63f3B6F627DC6b393")
        >>> print(is_ib)
        True

    See Also:
        - :func:`y.contracts.has_methods`
    """
    return await has_methods(
        token,
        (
            "debtShareToVal(uint)(uint)",
            "debtValToShare(uint)(uint)",
            "token()(address)",
            "totalToken()(uint)",
            "totalSupply()(uint)",
        ),
        sync=False,
    )


@a_sync.a_sync(default="sync")
async def get_price(
    token: AnyAddressType,
    block: Optional[Block] = None,
    skip_cache: bool = ENVS.SKIP_CACHE,
) -> UsdPrice:
    """
    Calculates the price of an Iron Bank token.

    Args:
        token: The address of the Iron Bank token.
        block (optional): The block number to query. Defaults to the latest block.
        skip_cache (optional): Whether to skip the cache when fetching prices. Defaults to :obj:`ENVS.SKIP_CACHE`.

    Returns:
        The price of the Iron Bank token in USD.

    Example:
        >>> price = get_price("0x41c84c0e2EE0b740Cf0d31F63f3B6F627DC6b393", block=14_000_000)
        >>> print(f"{price:.6f}")
        1.234567  # The price of the Iron Bank token in USD

    Note:
        This function calculates the price by retrieving the total balance and total supply of the Iron Bank token,
        scaling them appropriately, and then calculating the share price. The share price is then multiplied by the
        price of the underlying asset obtained from :func:`y.prices.magic.get_price`.

    See Also:
        - :func:`y.convert.to_address_async`
        - :func:`y.prices.magic.get_price`
    """
    address = await convert.to_address_async(token)
    token, total_bal, total_supply = await gather_methods(
        address, ("token", "totalToken", "totalSupply"), block=block
    )
    token_scale, pool_scale = await igather(map(ERC20._get_scale_for, (token, address)))
    total_bal /= Decimal(token_scale)
    total_supply /= Decimal(pool_scale)
    share_price = total_bal / total_supply
    token_price = await magic.get_price(token, block, skip_cache=skip_cache, sync=False)
    return share_price * token_price
