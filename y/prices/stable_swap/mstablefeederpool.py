import logging
from typing import Optional

import a_sync
from a_sync import cgather

from y import ENVIRONMENT_VARIABLES as ENVS
from y import convert
from y.classes.common import ERC20
from y.contracts import Contract, has_methods
from y.datatypes import AnyAddressType, Block, UsdPrice
from y.prices import magic

logger = logging.getLogger(__name__)


@a_sync.a_sync(default="sync", cache_type="memory", ram_cache_ttl=5 * 60)
async def is_mstable_feeder_pool(address: AnyAddressType) -> bool:
    """
    Check if a given address is an mStable Feeder Pool.

    This function verifies if the contract at the specified address implements
    the methods required for an mStable Feeder Pool, specifically `getPrice()((uint256,uint256))`
    and `mAsset()(address)`.

    Args:
        address: The address to check.

    Examples:
        >>> await is_mstable_feeder_pool("0x1234567890abcdef1234567890abcdef12345678")
        True

    Returns:
        True if the address is an mStable Feeder Pool, False otherwise.

    See Also:
        - :func:`y.contracts.has_methods`
    """
    return await has_methods(
        address, ("getPrice()((uint,uint))", "mAsset()(address)"), sync=False
    )


@a_sync.a_sync(default="sync")
async def get_price(
    token: AnyAddressType,
    block: Optional[Block] = None,
    skip_cache: bool = ENVS.SKIP_CACHE,
) -> UsdPrice:
    """
    Get the price of an mStable Feeder Pool token in USD.

    This function calculates the price of a given mStable Feeder Pool token by
    fetching the price ratio and the underlying mAsset price, then combining
    them to get the USD price.

    Args:
        token: The token address to get the price for.
        block: The block number to query. Defaults to the latest block.
        skip_cache: If True, skip using the cache while fetching price data.

    Examples:
        >>> await get_price("0x1234567890abcdef1234567890abcdef12345678")
        UsdPrice(1.23)

    Returns:
        The price of the token in USD.

    See Also:
        - :class:`y.datatypes.UsdPrice`
        - :func:`y.prices.magic.get_price`
    """
    address = await convert.to_address_async(token)
    contract = await Contract.coroutine(address)
    ratio, masset, scale = await cgather(
        contract.getPrice.coroutine(block_identifier=block),
        contract.mAsset.coroutine(block_identifier=block),
        ERC20._get_scale_for(address),
    )
    ratio = ratio[0] / scale
    underlying_price = await magic.get_price(
        masset, block, skip_cache=skip_cache, sync=False
    )
    return UsdPrice(underlying_price * ratio)
