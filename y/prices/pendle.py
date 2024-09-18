
import asyncio
from decimal import Decimal
from typing import Tuple

from a_sync import a_sync
from async_lru import alru_cache

from y import ENVIRONMENT_VARIABLES as ENVS
from y.classes.common import ERC20
from y.contracts import Contract, has_method
from y.datatypes import Address, Block
from y.exceptions import ContractNotVerified


try:
    PENDLE_ORACLE = Contract("0x9a9Fa8338dd5E5B2188006f1Cd2Ef26d921650C2")
except ContractNotVerified:
    PENDLE_ORACLE = None
    
TWAP_DURATION = 1


@a_sync("sync")
async def is_pendle_lp(token: Address) -> bool:
    """
    Determines if the given token address is a Pendle LP token.

    Args:
        token: The address of the token to check.

    Returns:
        True if the token is a Pendle LP token, False otherwise.

    Example:
        >>> is_pendle = is_pendle_lp("0x1b92b5242301ce4a8c73cc3ef0d6dee33a3a5b23")
        >>> print(is_pendle)
        True
    """
    return PENDLE_ORACLE is not None and await has_method(token, 'readTokens()(address,address,address)', sync=False)

@alru_cache(maxsize=None)
async def get_tokens(lp_token: Address) -> Tuple[str, str, str]:
    """
    Retrieves the addresses of the tokens in a Pendle LP token.

    This function is cached to improve performance for repeated calls.

    Args:
        lp_token: The address of the Pendle LP token.

    Returns:
        A tuple containing the addresses of the SY token, PT token, and YT token.

    Example:
        >>> tokens = await get_tokens("0x1b92b5242301ce4a8c73cc3ef0d6dee33a3a5b23")
        >>> print(tokens)
        ('0x...', '0x...', '0x...')  # Addresses of SY, PT, and YT tokens
    """
    lp_token = await Contract.coroutine(lp_token)
    return await lp_token.readTokens

@a_sync("sync")
async def get_lp_price(token: Address, block: Block = None, skip_cache: bool = ENVS.SKIP_CACHE) -> Decimal:
    """
    Calculates the price of a Pendle LP token.

    Args:
        token: The address of the Pendle LP token.
        block (optional): The block number to query. Defaults to the latest block.
        skip_cache (optional): Whether to skip the cache when fetching prices. Defaults to :obj:`ENVS.SKIP_CACHE`.

    Returns:
        The price of the LP token in USD.

    Example:
        >>> price = get_lp_price("0x1b92b5242301ce4a8c73cc3ef0d6dee33a3a5b23", block=14_000_000)
        >>> print(f"{price:.6f}")
        1.234567  # The price of the Pendle LP token in USD

    Note:
        This function uses the Pendle Oracle contract to get the LP to asset rate and then
        calculates the USD price based on the underlying asset's price.
    """
    tokens = await get_tokens(token)
    # NOTE: we might not need this, leave it commented out for now
    #names = await asyncio.gather(*[ERC20(t, asynchronous=True).name for t in tokens])
    #if any("DAI" in name for name in names):
    #    use_asset = True
    #    rate = await PENDLE_ORACLE.getLpToAssetRate.coroutine(token, twap_duration, block_identifier=block)
    #elif any("crvUSD" in name for name in (ERC20(t) for t in tokens)):
    #    use_asset = True
    #    rate = await PENDLE_ORACLE.getLpToAssetRate.coroutine(token, twap_duration, block_identifier=block)
    #else:
    #    use_asset = False
    #    rate = await PENDLE_ORACLE.getLpToAssetRate.coroutine(token, twap_duration, block_identifier=block)
    sy_token, p_token, y_token = tokens
    sy, rate = await asyncio.gather(
        Contract.coroutine(sy_token),
        PENDLE_ORACLE.getLpToAssetRate.coroutine(token, TWAP_DURATION, block_identifier=block),
    )
    _, asset, decimals = await sy.assetInfo
    rate /= Decimal(10**decimals)
    return rate * await ERC20(asset, asynchronous=True).price(block=block, skip_cache=skip_cache)
