import logging
from typing import List, Optional

from a_sync import a_sync, cgather
from web3.middleware.validation import is_not_null

from y import ENVIRONMENT_VARIABLES as ENVS
from y import convert
from y.classes.common import ERC20
from y.constants import CONNECTED_TO_MAINNET
from y.contracts import has_method, has_methods
from y.datatypes import (
    Address,
    AddressOrContract,
    AnyAddressType,
    Block,
    UsdPrice,
    UsdValue,
)
from y.prices import magic
from y.utils.multicall import multicall_same_func_same_contract_different_inputs

logger = logging.getLogger(__name__)

_GET_TOKEN_INPUTS = tuple(range(8))


@a_sync(default="sync", cache_type="memory", ram_cache_ttl=5 * 60)
async def is_saddle_lp(token_address: AnyAddressType) -> bool:
    """
    Determine if a given token is a Saddle LP token.

    This function checks if the token has specific methods that are characteristic of Saddle LP tokens.

    Args:
        token_address: The address of the token to check.

    Returns:
        True if the token is a Saddle LP token, False otherwise.

    Examples:
        >>> await is_saddle_lp("0x1234567890abcdef1234567890abcdef12345678")
        False

    See Also:
        - :func:`get_pool`
    """
    pool = await get_pool(token_address, sync=False)
    return pool is not None and await has_methods(
        pool,
        ("getVirtualPrice()(uint)", "getA()(uint)", "getAPrecise()(uint)"),
        sync=False,
    )


@a_sync(default="sync", ram_cache_ttl=ENVS.CACHE_TTL)
async def get_pool(token_address: AnyAddressType) -> Address:
    """
    Retrieve the pool address for a given Saddle LP token.

    This function checks for specific token addresses on the Ethereum Mainnet and returns hardcoded pool addresses for those tokens.
    If the token is not one of the known tokens, it attempts to find a pool by checking if the token has a `swap()` method.

    Args:
        token_address: The address of the token to find the pool for.

    Returns:
        The address of the pool if found, otherwise None.

    Examples:
        >>> await get_pool("0xc9da65931ABf0Ed1b74Ce5ad8c041C4220940368")
        '0xa6018520EAACC06C30fF2e1B3ee2c7c22e64196a'

    See Also:
        - :func:`is_saddle_lp`
    """
    token_address = await convert.to_address_async(token_address)
    if CONNECTED_TO_MAINNET:
        # saddle aleth doesn't have swap() function
        if token_address == "0xc9da65931ABf0Ed1b74Ce5ad8c041C4220940368":
            return "0xa6018520EAACC06C30fF2e1B3ee2c7c22e64196a"
        elif token_address == "0xd48cF4D7FB0824CC8bAe055dF3092584d0a1726A":  # saddle d4
            return "0xC69DDcd4DFeF25D8a793241834d4cc4b3668EAD6"
        elif token_address == "0xF32E91464ca18fc156aB97a697D6f8ae66Cd21a3":
            return "0xdf3309771d2BF82cb2B6C56F9f5365C8bD97c4f2"
    pool = await has_method(
        token_address, "swap()(address)", return_response=True, sync=False
    )
    return pool or None


@a_sync(default="sync")
async def get_price(
    token_address: AddressOrContract, block: Optional[Block] = None
) -> UsdPrice:
    """
    Calculate the price of a Saddle LP token in USD.

    This function calculates the price by dividing the total value locked (TVL) by the total supply of the token.

    Args:
        token_address: The address of the token to get the price for.
        block: The block number to query. Defaults to the latest block.

    Examples:
        >>> await get_price("0x1234567890abcdef1234567890abcdef12345678")
        UsdPrice(1.2345)

    See Also:
        - :func:`get_tvl`
    """
    tvl, total_supply = await cgather(
        get_tvl(token_address, block, sync=False),
        ERC20(token_address, asynchronous=True).total_supply_readable(block),
    )
    return UsdPrice(tvl / total_supply)


@a_sync(default="sync")
async def get_tvl(
    token_address: AnyAddressType,
    block: Optional[Block] = None,
    skip_cache: bool = ENVS.SKIP_CACHE,
) -> UsdValue:
    """
    Calculate the total value locked (TVL) in a Saddle LP token pool.

    This function retrieves the pool and tokens concurrently, then uses multicall to get the balances.
    It calculates the TVL by summing the value of each token in the pool.

    Args:
        token_address: The address of the token to get the TVL for.
        block: The block number to query. Defaults to the latest block.
        skip_cache: If True, skip using the cache while fetching price data.

    Examples:
        >>> await get_tvl("0x1234567890abcdef1234567890abcdef12345678")
        UsdValue(123456.78)

    See Also:
        - :func:`get_price`
    """
    tokens: List[ERC20]
    pool, tokens = await cgather(
        get_pool(token_address, sync=False),
        get_tokens(token_address, block, sync=False),
    )
    balances = await multicall_same_func_same_contract_different_inputs(
        pool,
        "getTokenBalance(uint8)(uint)",
        inputs=range(len(tokens)),
        sync=False,
    )
    scales, prices = await cgather(
        ERC20.scale.map(tokens).values(pop=True),
        magic.get_prices(tokens, block, skip_cache=skip_cache, silent=True, sync=False),
    )
    return UsdValue(
        sum(
            balance / scale * price
            for balance, scale, price in zip(balances, scales, prices)
        )
    )


@a_sync(default="sync")
async def get_tokens(
    token_address: AnyAddressType, block: Optional[Block] = None
) -> List[ERC20]:
    """
    Retrieve the list of tokens in a Saddle LP token pool.

    This function retrieves the pool and then uses multicall to get the tokens in the pool.

    Args:
        token_address: The address of the token to get the tokens for.
        block: The block number to query. Defaults to the latest block.

    Examples:
        >>> await get_tokens("0x1234567890abcdef1234567890abcdef12345678")
        [ERC20('0xToken1'), ERC20('0xToken2')]

    See Also:
        - :func:`get_pool`
    """
    pool, tokens = await cgather(
        get_pool(token_address, sync=False),
        multicall_same_func_same_contract_different_inputs(
            pool,
            "getToken(uint8)(address)",
            inputs=_GET_TOKEN_INPUTS,
            block=block,
            return_None_on_failure=True,
            sync=False,
        ),
    )
    return list(map(ERC20, filter(is_not_null, tokens)))
