import logging
from typing import Optional

from a_sync import a_sync, cgather

from y import ENVIRONMENT_VARIABLES as ENVS
from y import convert
from y.classes.common import ERC20
from y.constants import CONNECTED_TO_MAINNET, weth
from y.datatypes import AnyAddressType, Block, UsdPrice
from y.prices import magic
from y.utils.raw_calls import raw_call

logger = logging.getLogger(__name__)


def is_creth(token: AnyAddressType) -> bool:
    """Check if a token is crETH.

    Args:
        token: The token address to check.

    Returns:
        True if the token is crETH on the Ethereum Mainnet, False otherwise.

    Example:
        >>> is_creth("0xcBc1065255cBc3aB41a6868c22d1f1C573AB89fd")
        True
    """
    return (
        CONNECTED_TO_MAINNET
        and convert.to_address(token) == "0xcBc1065255cBc3aB41a6868c22d1f1C573AB89fd"
    )


@a_sync(default="sync")
async def get_price_creth(
    token: AnyAddressType,
    block: Optional[Block] = None,
    skip_cache: bool = ENVS.SKIP_CACHE,
) -> UsdPrice:
    """Get the price of crETH in USD.

    This function retrieves the accumulated balance and total supply of crETH,
    divides the total balance by the total supply to calculate the value per token,
    and then multiplies this value by the current WETH price to determine the price
    of crETH in USD.

    Args:
        token: The crETH token address.
        block: The block number to query. Defaults to the latest block.
        skip_cache: If True, skip using the cache while fetching price data.

    Examples:
        >>> await get_price_creth("0xcBc1065255cBc3aB41a6868c22d1f1C573AB89fd")
        1234.56

    See Also:
        - :func:`y.prices.magic.get_price`
        - :class:`y.classes.common.ERC20`
    """
    address = await convert.to_address_async(token)
    total_balance, total_supply, weth_price = await cgather(
        raw_call(address, "accumulated()", output="int", block=block, sync=False),
        ERC20(address, asynchronous=True).total_supply(block),
        magic.get_price(weth, block, skip_cache=skip_cache, sync=False),
    )
    per_share = total_balance / total_supply
    return per_share * weth_price
