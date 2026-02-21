from collections.abc import Callable, Iterable
from functools import wraps
from logging import DEBUG, Logger, getLogger
from typing import Literal, TypeVar, overload

import a_sync
import dank_mids
from a_sync import igather
from brownie import ZERO_ADDRESS
from brownie.exceptions import ContractNotFound
from eth_typing import BlockNumber, ChecksumAddress, HexAddress
from typing_extensions import ParamSpec

from y import ENVIRONMENT_VARIABLES as ENVS
from y import constants, convert
from y._decorators import stuck_coro_debugger
from y.classes import ERC20
from y.datatypes import AnyAddressType, Block, Pool, UsdPrice
from y.exceptions import NonStandardERC20, PriceError, yPriceMagicError
from y.prices import (
    band,
    chainlink,
    convex,
    one_to_one,
    pendle,
    popsicle,
    rkp3r,
    solidex,
    utils,
    vbtoken,
    yearn,
)
from y.prices.dex import *
from y.prices.dex.uniswap import UniswapV2Pool, uniswap_multiplexer
from y.prices.eth_derivs import *
from y.prices.gearbox import gearbox
from y.prices.lending import *
from y.prices.stable_swap import *
from y.prices.synthetix import synthetix
from y.prices.tokenized_fund import *
from y.utils.logging import get_price_logger

_P = ParamSpec("_P")
_T = TypeVar("_T")
_TAddress = TypeVar("_TAddress", bound=AnyAddressType)

cache_logger = getLogger(f"{__name__}.cache")


@overload
async def get_price(
    token_address: AnyAddressType,
    block: Block | None = None,
    *,
    fail_to_None: Literal[True],
    skip_cache: bool = ENVS.SKIP_CACHE,
    ignore_pools: tuple[Pool, ...] = (),
    silent: bool = False,
) -> UsdPrice | None: ...


@overload
async def get_price(
    token_address: AnyAddressType,
    block: Block | None = None,
    *,
    fail_to_None: bool = False,
    skip_cache: bool = ENVS.SKIP_CACHE,
    ignore_pools: tuple[Pool, ...] = (),
    silent: bool = False,
) -> UsdPrice: ...


@a_sync.a_sync(default="sync")
async def get_price(
    token_address: AnyAddressType,
    block: Block | None = None,
    *,
    fail_to_None: bool = False,
    skip_cache: bool = ENVS.SKIP_CACHE,
    ignore_pools: tuple[Pool, ...] = (),
    silent: bool = False,
) -> UsdPrice | None:
    """
    Get the price of a token in USD.

    Args:
        token_address: The address of the token to price. The function accepts hexadecimal strings, Brownie Contract objects, and integers as shorthand for addresses.
        block (optional): The block number at which to get the price. If None, uses the latest block.
        fail_to_None (optional): If True, return None instead of raising a :class:`~yPriceMagicError` on failure. Defaults to False.
        skip_cache (optional): If True, bypass the cache and fetch the price directly. Defaults to :obj:`ENVS.SKIP_CACHE`.
        ignore_pools (optional): A tuple of pool addresses to ignore when fetching the price.
        silent: If True, suppress error logging. Defaults to False.

    Returns:
        The price of the token in USD, or None if the price couldn't be determined and fail_to_None is True.

    Raises:
        yPriceMagicError: If the price couldn't be determined and fail_to_None is False.

    Note:
        ypricemagic accepts integers as valid token_address values for convenience.
        For example, you can use :samp:`y.get_price(0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e)` to save keystrokes
        while testing in an interactive console.

    Examples:
        >>> from y import get_price
        >>> price = get_price("0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e", 12345678)
        >>> print(price)

    See Also:
        :func:`get_prices`
    """
    block = int(block or await dank_mids.eth.block_number)
    token_address = await convert.to_address_async(token_address)
    try:
        return await _get_price(
            token_address,
            block,
            fail_to_None=fail_to_None,
            ignore_pools=ignore_pools,
            skip_cache=skip_cache,
            silent=silent,
        )
    except (ContractNotFound, NonStandardERC20, PriceError) as e:
        symbol = await ERC20(token_address, asynchronous=True).symbol
        if not fail_to_None:
            raise_from = None if isinstance(e, PriceError) else e
            raise yPriceMagicError(e, token_address, block, symbol) from raise_from


@overload
async def get_prices(
    token_addresses: Iterable[AnyAddressType],
    block: Block | None = None,
    *,
    fail_to_None: Literal[True],
    skip_cache: bool = ENVS.SKIP_CACHE,
    silent: bool = False,
) -> list[UsdPrice | None]: ...


@overload
async def get_prices(
    token_addresses: Iterable[AnyAddressType],
    block: Block | None = None,
    *,
    fail_to_None: bool = False,
    skip_cache: bool = ENVS.SKIP_CACHE,
    silent: bool = False,
) -> list[UsdPrice]: ...


@a_sync.a_sync(default="sync")
async def get_prices(
    token_addresses: Iterable[AnyAddressType],
    block: Block | None = None,
    *,
    fail_to_None: bool = False,
    skip_cache: bool = ENVS.SKIP_CACHE,
    silent: bool = False,
) -> list[UsdPrice | None]:
    """
    Get the price of each token in an iterable of token addresses.

    Args:
        token_addresses: The iterable of token addresses to price.
        block (optional): The block number at which to get the price. If None, uses the latest block.
        fail_to_None (optional): If True, return None instead of raising a :class:`~yPriceMagicError` on failure. Defaults to False.
        skip_cache (optional): If True, bypass the cache and fetch the price directly. Defaults to :obj:`ENVS.SKIP_CACHE`.
        silent: If True, suppress error logging. Defaults to False.

    Returns:
        A list of token prices corresponding to the input iterable, or None for tokens whose prices could not be determined if fail_to_None is True.

    Raises:
        yPriceMagicError: If the price couldn't be determined for any token and fail_to_None is False.

    Examples:
        >>> prices = get_prices(["0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e", "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C"], 12345678)
        >>> print(prices)

    See Also:
        :func:`get_price`
    """
    block = int(block or await dank_mids.eth.block_number)
    token_addresses = await convert.to_address_async(token_addresses)
    prices = await igather(
        *(
            _get_price(
                token_address,
                block,
                fail_to_None=fail_to_None,
                skip_cache=skip_cache,
                silent=silent,
            )
            for token_address in token_addresses
        ),
        return_exceptions=True,
    )
    return [price if not isinstance(price, Exception) else None for price in prices]


@get_price
@a_sync.a_sync(default="sync", cache_type="memory")
async def _get_price(
    token_address: ChecksumAddress,
    block: Block,
    fail_to_None: bool,
    skip_cache: bool = ENVS.SKIP_CACHE,
    ignore_pools: tuple[Pool, ...] = (),
    silent: bool = False,
) -> UsdPrice | None:
    if block:
        if a_sync.running_loop is None:
            if block > await dank_mids.eth.block_number:
                raise TypeError("Block height cannot be in the future.")
        else:
            if block > await dank_mids.eth.block_number:
                logger = getLogger(__name__)
                logger.warning(
                    "Tried to get a price for %s at future block %s, using latest block %s",  # noqa: E501
                    token_address,
                    block,
                    await dank_mids.eth.block_number,
                )
                block = None

    if token_address in constants.STABLECOINS.values() or token_address == constants.weth:
        return 1

    if token_address == constants.CHAINLINK:
        # chainlink oracles are for other tokens, and are not priced by chainlink feeds.
        # same for chainlink oracles on other networks.
        return None

    if token_address == constants.yusd:
        return 1

    bucket = await utils.check_bucket(token_address, sync=False)

    return await _exit_early_for_known_tokens(
        token_address,
        block,
        bucket,
        fail_to_None,
        ignore_pools,
        skip_cache,
        silent,
    )


@a_sync.a_sync(default="sync", cache_type="memory")
async def _exit_early_for_known_tokens(
    token_address: ChecksumAddress,
    block: Block,
    bucket: str | None = None,
    fail_to_None: bool = False,
    ignore_pools: tuple[Pool, ...] = (),
    skip_cache: bool = ENVS.SKIP_CACHE,
    silent: bool = False,
) -> UsdPrice | None:
    token = None
    if token_address in constants.STABLECOINS.values():
        return 1
    elif token_address == constants.weth:
        return 1

    if bucket == "chainlink feed":
        return await chainlink.get_price(token_address, block, skip_cache=skip_cache, sync=False)
    if bucket == "ib token":
        token = await utils.ib.get_token(token_address)
    if bucket == "atoken":
        token = await atokens.AToken(token_address, asynchronous=True)
    if bucket == "compound":
        token = await compound.CToken(token_address, asynchronous=True)
    if bucket == "solidex":
        token = await solidex.SolidexDepositToken(token_address, asynchronous=True)
    if bucket == "convex":
        token = await convex.CvxDeposit(token_address, asynchronous=True)
    if bucket == "curve":
        token = await curve.CurvePoolToken(token_address, asynchronous=True)
    if bucket == "ib token":
        token = await ib_tokens(token_address, asynchronous=True)
    if bucket == "popsicle":
        token = await popsicle.PopsicleLp(token_address, asynchronous=True)
    if bucket == "rkp3r":
        token = await rkp3r.RetrieveToken(token_address, asynchronous=True)
    if bucket == "yearn":
        token = await yearn.YearnInspiredVault(token_address, asynchronous=True)
    if bucket == "vbtoken":
        return await vbtoken.get_price(token_address, block, skip_cache=skip_cache, sync=False)
    if bucket == "belt":
        token = await belt.BeltPoolToken(token_address, asynchronous=True)
    if bucket == "ellipsis":
        token = await ellipsis.EllipsisPoolToken(token_address, asynchronous=True)
    if bucket == "froyo":
        token = await froyo.FroyoPoolToken(token_address, asynchronous=True)
    if bucket == "mstablefeederpool":
        token = await mstablefeederpool.MStableFeederPool(token_address, asynchronous=True)
    if bucket == "saddle":
        token = await saddle.SaddlePoolToken(token_address, asynchronous=True)
    if bucket == "stargate lp":
        token = await stargate.StargatePool(token_address, asynchronous=True)
    if bucket == "synthetix":
        token = await synthetix.Synth(token_address, asynchronous=True)

    if bucket == "stargate lp":
        return await token.price(block=block, skip_cache=skip_cache, sync=False)
    if bucket == "stargate":
        return await stargate.get_price(token_address, block=block, skip_cache=skip_cache)
    if bucket == "vbtoken":
        # vbTokens should fail closed if pricing fails; do not fall back to dex pricing.
        return None

    if token is not None:
        return await token.price(block, ignore_pools, skip_cache=skip_cache, sync=False)

    return None
