from collections.abc import Callable, Iterable
from decimal import Decimal
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
from y.datatypes import AnyAddressType, Block, Pool, PriceResult, PriceStep, UsdPrice
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
    amount: Decimal | int | float | None = None,
) -> PriceResult | None: ...


@overload
async def get_price(
    token_address: AnyAddressType,
    block: Block | None = None,
    *,
    fail_to_None: bool = False,
    skip_cache: bool = ENVS.SKIP_CACHE,
    ignore_pools: tuple[Pool, ...] = (),
    silent: bool = False,
    amount: Decimal | int | float | None = None,
) -> PriceResult: ...


@a_sync.a_sync(default="sync")
async def get_price(
    token_address: AnyAddressType,
    block: Block | None = None,
    *,
    fail_to_None: bool = False,
    skip_cache: bool = ENVS.SKIP_CACHE,
    ignore_pools: tuple[Pool, ...] = (),
    silent: bool = False,
    amount: Decimal | int | float | None = None,
) -> PriceResult | None:
    """
    Get the price of a token in USD.

    Args:
        token_address: The address of the token to price. The function accepts hexadecimal strings, Brownie Contract objects, and integers as shorthand for addresses.
        block (optional): The block number at which to get the price. If None, uses the latest block.
        fail_to_None (optional): If True, return None instead of raising a :class:`~yPriceMagicError` on failure. Defaults to False.
        skip_cache (optional): If True, bypass the cache and fetch the price directly. Defaults to :obj:`ENVS.SKIP_CACHE`.
        ignore_pools (optional): A tuple of pool addresses to ignore when fetching the price.
        silent: If True, suppress error logging. Defaults to False.
        amount: The amount of tokens to quote in human-readable units (e.g. 1000 = 1000 tokens).
            When provided, the price accounts for price impact on DEX sources. The returned
            price is still per-unit (USD per token). Defaults to None (spot price for 1 token).

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
        >>> # Get price with price impact for selling 1000 tokens:
        >>> price = get_price("0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e", 12345678, amount=1000)

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
            amount=amount,
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
    amounts: Iterable[Decimal | int | float | None] | None = None,
) -> list[PriceResult | None]: ...


@overload
async def get_prices(
    token_addresses: Iterable[AnyAddressType],
    block: Block | None = None,
    *,
    fail_to_None: bool = False,
    skip_cache: bool = ENVS.SKIP_CACHE,
    silent: bool = False,
    amounts: Iterable[Decimal | int | float | None] | None = None,
) -> list[PriceResult]: ...


@a_sync.a_sync(default="sync")
async def get_prices(
    token_addresses: Iterable[AnyAddressType],
    block: Block | None = None,
    *,
    fail_to_None: bool = False,
    skip_cache: bool = ENVS.SKIP_CACHE,
    silent: bool = False,
    amounts: Iterable[Decimal | int | float | None] | None = None,
) -> list[PriceResult | None]:
    """
    Get prices for multiple tokens in USD.

    This function is optimized for parallel execution and should be preferred over
    :func:`get_price` when querying prices in bulk.

    Args:
        token_addresses: An iterable of token addresses to price.
        block (optional): The block number at which to get the prices. If None, defaults to the latest block.
        fail_to_None (optional): If True, return None for tokens whose price couldn't be determined. Defaults to False.
        skip_cache (optional): If True, bypass the cache and fetch prices directly. Defaults to :obj:`ENVS.SKIP_CACHE`.
        silent (optional): If True, suppress error logging and any progress indicators. Defaults to False.
        amounts: An iterable of per-token amounts (in human-readable units) parallel to
            ``token_addresses``. When provided, each price accounts for price impact on DEX
            sources. The returned prices are still per-unit. Defaults to None (spot prices).

    Returns:
        A list of token prices in USD, in the same order as the input :samp:`token_addresses`.

    Examples:
        >>> from y import get_prices
        >>> prices = get_prices(["0x123...", "0x456..."], block=12345678)
        >>> # With per-token amounts for price impact:
        >>> prices = get_prices(["0x123...", "0x456..."], block=12345678, amounts=[1000, 500])

    See Also:
        :func:`get_price` and :func:`map_prices`
    """
    if amounts is not None:
        block_number = block or await dank_mids.eth.block_number
        return list(
            await igather(
                get_price(
                    t,
                    block_number,
                    fail_to_None=fail_to_None,
                    skip_cache=skip_cache,
                    silent=silent,
                    amount=a,
                    sync=False,
                )
                for t, a in zip(token_addresses, amounts)
            )
        )
    return await map_prices(
        token_addresses,
        block or await dank_mids.eth.block_number,
        fail_to_None=fail_to_None,
        skip_cache=skip_cache,
        silent=silent,
    ).values(pop=True)


@overload
def map_prices(
    token_addresses: Iterable[_TAddress],
    block: Block,
    *,
    fail_to_None: Literal[True],
    skip_cache: bool = ENVS.SKIP_CACHE,
    silent: bool = False,
    amount: Decimal | int | float | None = None,
) -> a_sync.TaskMapping[_TAddress, PriceResult | None]: ...


@overload
def map_prices(
    token_addresses: Iterable[_TAddress],
    block: Block,
    *,
    fail_to_None: bool = False,
    skip_cache: bool = ENVS.SKIP_CACHE,
    silent: bool = False,
    amount: Decimal | int | float | None = None,
) -> a_sync.TaskMapping[_TAddress, PriceResult]: ...


def map_prices(
    token_addresses: Iterable[_TAddress],
    block: Block,
    *,
    fail_to_None: bool = False,
    skip_cache: bool = ENVS.SKIP_CACHE,
    silent: bool = False,
    amount: Decimal | int | float | None = None,
) -> a_sync.TaskMapping[_TAddress, PriceResult | None]:
    """
    Map token addresses to their prices asynchronously.

    Args:
        token_addresses: An iterable of token addresses to price.
        block (optional): The block number at which to get the prices.
        fail_to_None (optional): If True, map tokens whose price couldn't be determined to None. Defaults to False.
        skip_cache (optional): If True, bypass the cache and fetch prices directly. Defaults to :obj:`ENVS.SKIP_CACHE`.
        silent (optional): If True, suppress error logging. Defaults to False.
        amount: A uniform amount of tokens (in human-readable units) to use for each price query.
            When provided, prices account for price impact on DEX sources. Defaults to None.

    Returns:
        A :class:`~a_sync.TaskMapping` object mapping token addresses to their USD prices.

    Examples:
        >>> from y import map_prices
        >>> task_map = map_prices(["0xabc...", "0xdef..."], 12345678)
        >>> results = await task_map.values(pop=True)
        >>> print(results)
        [1.234, 2.345]

    See Also:
        :func:`get_prices`
    """
    return a_sync.map(
        get_price,
        token_addresses,
        block=block,
        fail_to_None=fail_to_None,
        skip_cache=skip_cache,
        silent=silent,
        amount=amount,
    )


def __vttl_cache(get_price):
    """
    A decorator that caches price results in a VTTLCache with per-key TTL.

    Spot prices (amount=None) use :obj:`ENVS.CACHE_TTL` while amount-based
    prices use the shorter :obj:`ENVS.AMOUNT_CACHE_TTL`.

    Args:
        get_price: The async function to be cached.

    Returns:
        A wrapped version of the input function with VTTLCache caching.
    """
    from cachebox import VTTLCache

    _cache = VTTLCache(maxsize=ENVS.PRICE_CACHE_MAXSIZE)

    @wraps(get_price)
    async def cache_wrap(
        token: ChecksumAddress,
        block: BlockNumber,
        *,
        fail_to_None: bool = False,
        skip_cache: bool = ENVS.SKIP_CACHE,
        ignore_pools: tuple[Pool, ...] = (),
        silent: bool = False,
        amount: Decimal | int | float | None = None,
    ) -> PriceResult | None:
        if skip_cache:
            return await get_price(
                token,
                block,
                fail_to_None=fail_to_None,
                skip_cache=skip_cache,
                ignore_pools=ignore_pools,
                silent=silent,
                amount=amount,
            )

        key = (token, block, fail_to_None, skip_cache, ignore_pools, silent, amount)
        try:
            return _cache[key]
        except KeyError:
            pass

        result = await get_price(
            token,
            block,
            fail_to_None=fail_to_None,
            skip_cache=skip_cache,
            ignore_pools=ignore_pools,
            silent=silent,
            amount=amount,
        )
        if result is not None:
            ttl = ENVS.AMOUNT_CACHE_TTL if amount is not None else ENVS.CACHE_TTL
            _cache.insert(key, result, ttl=ttl)
        return result

    cache_wrap.cache = _cache
    return cache_wrap


def __cache(get_price: Callable[_P, _T]) -> Callable[_P, _T]:
    """
    A decorator to cache the results of the get_price function.

    Args:
        get_price: The function to be cached.

    Returns:
        A wrapped version of the input function with caching functionality.
    """

    @wraps(get_price)
    async def cache_wrap(
        token: ChecksumAddress,
        block: BlockNumber,
        *,
        fail_to_None: bool = False,
        skip_cache: bool = ENVS.SKIP_CACHE,
        ignore_pools: tuple[Pool, ...] = (),
        silent: bool = False,
        amount: Decimal | int | float | None = None,
    ) -> PriceResult | None:
        from y._db.utils import price as db

        # Only use disk cache for unit prices (amount=None)
        # NOTE: db.get_price returns Decimal, wrap in PriceResult with empty path
        if amount is None and not skip_cache and (price := await db.get_price(token, block)):
            cache_logger.debug("disk cache -> %s", price)
            # DB cache stores only the price value, not the derivation path
            return PriceResult(price=UsdPrice(price), path=[])
        result = await get_price(
            token,
            block=block,
            fail_to_None=fail_to_None,
            ignore_pools=ignore_pools,
            silent=silent,
            amount=amount,
        )
        if result and amount is None and not skip_cache:
            # Extract .price from PriceResult for DB storage
            db.set_price(token, block, result.price)
        return result

    return cache_wrap


@stuck_coro_debugger
@a_sync.a_sync(default="async")
@__vttl_cache
@__cache
async def _get_price(
    token: ChecksumAddress,
    block: BlockNumber,
    *,
    fail_to_None: bool = False,
    skip_cache: bool = ENVS.SKIP_CACHE,
    ignore_pools: tuple[Pool, ...] = (),
    silent: bool = False,
    amount: Decimal | int | float | None = None,
) -> PriceResult | None:  # sourcery skip: remove-redundant-if
    """
    Internal function to get the price of a token.

    This function implements the core logic for fetching token prices.

    Args:
        token: The address of the token to price.
        block: The block number at which to get the price.
        fail_to_None: If True, return None instead of raising an exception on failure.
        skip_cache: If True, bypass the cache and fetch the price directly.
        ignore_pools: A tuple of pool addresses to ignore when fetching the price.
        silent: If True, suppress error logging.
        amount: The amount of tokens (human-readable units) to use for DEX quotes.

    Returns:
        A PriceResult containing the price and derivation path, or None if the price
        couldn't be determined and fail_to_None is True.
    """
    if token == ZERO_ADDRESS:
        logger = get_price_logger(
            token, block, symbol="[ZERO_ADDRESS]", extra="magic", start_task=True
        )
        _fail_appropriately(logger, "[ZERO_ADDRESS]", fail_to_None, silent)
        return None

    try:
        # We do this to cache the symbol for later, otherwise some repr woudl break
        symbol = await ERC20(token, asynchronous=True).symbol
    except NonStandardERC20:
        symbol = None

    logger = get_price_logger(token, block, symbol=symbol, extra="magic", start_task=True)
    logger.debug("fetching price for %s", symbol)
    try:
        # Track source info for PriceStep construction
        raw_price = None
        source = None
        pool = None

        # Try API first
        price_or_none, api_source = await _get_price_from_api(token, block, logger)
        if price_or_none is not None:
            raw_price = price_or_none
            source = api_source

        # Try bucket functions (known token types)
        if raw_price is None:
            price_or_none, bucket_name = await _exit_early_for_known_tokens(
                token,
                block=block,
                ignore_pools=ignore_pools,
                skip_cache=skip_cache,
                logger=logger,
            )
            if price_or_none is not None:
                raw_price = price_or_none
                source = bucket_name

        # Try DEXes
        if raw_price is None:
            price_or_none, dex_info = await _get_price_from_dexes(
                token, block, ignore_pools, skip_cache, logger, amount=amount
            )
            if price_or_none is not None:
                raw_price = price_or_none
                source = dex_info.get("source") if dex_info else None
                pool = dex_info.get("pool") if dex_info else None

        if raw_price:
            # If a bucket function returned a PriceResult (from a recursive get_price call),
            # extract the numeric price for sense_check
            numeric_price = raw_price.price if isinstance(raw_price, PriceResult) else raw_price
            await utils.sense_check(token, block, numeric_price)
        else:
            _fail_appropriately(logger, symbol, fail_to_None, silent)

        logger.debug("%s price: %s", symbol, raw_price)

        if raw_price:  # checks for the erroneous 0 value we see once in a while
            if isinstance(raw_price, PriceResult):
                # Bucket returned a PriceResult with its own path — use it directly
                return raw_price
            # Wrap raw price into PriceResult with path
            price_step = PriceStep(
                source=source or "unknown",
                input_token=str(token),
                output_token="USD",
                pool=pool,
                price=float(raw_price),
            )
            return PriceResult(price=UsdPrice(raw_price), path=[price_step])
    finally:
        logger.close()


@stuck_coro_debugger
async def _exit_early_for_known_tokens(
    token_address: ChecksumAddress,
    block: BlockNumber,
    logger: Logger,
    skip_cache: bool = ENVS.SKIP_CACHE,
    ignore_pools: tuple[Pool, ...] = (),
) -> tuple[UsdPrice | float | PriceResult | None, str | None]:  # sourcery skip: low-code-quality
    """
    Attempt to get the price for known token types without having to fully load everything.

    This function checks if the token is of a known type (e.g., atoken, balancer pool, etc.)
    and attempts to get its price using type-specific methods.

    Args:
        token_address: The address of the token to price.
        block: The block number at which to get the price.
        logger: A logger instance for recording debug information.
        skip_cache: If True, bypass the cache and fetch the price directly.
        ignore_pools: A tuple of pool addresses to ignore when fetching the price.

    Returns:
        A tuple of (price, bucket_name) if the price can be determined early, or (None, None) otherwise.
        The price may be a PriceResult (from recursive get_price calls in bucket functions),
        a plain UsdPrice/float, or None.
        The bucket_name string (e.g., 'chainlink feed', 'atoken', 'curve lp') is used to build the PriceStep.
    """
    bucket = await utils.check_bucket(token_address, sync=False)

    price = None

    if bucket == "atoken":
        price = await aave.get_price(token_address, block=block, skip_cache=skip_cache, sync=False)

    elif bucket == "balancer pool":
        price = await balancer_multiplexer.get_price(
            token_address, block, skip_cache=skip_cache, sync=False
        )

    elif bucket == "basketdao":
        price = await basketdao.get_price(token_address, block, skip_cache=skip_cache, sync=False)

    elif bucket == "belt lp":
        price = await belt.get_price(token_address, block, sync=False)

    elif bucket == "chainlink and band":
        price = await chainlink.get_price(token_address, block, sync=False) or await band.get_price(
            token_address, block, sync=False
        )

    elif bucket == "chainlink feed":
        price = await chainlink.get_price(token_address, block, sync=False)

    elif bucket == "compound":
        price = await compound.get_price(
            token_address, block=block, skip_cache=skip_cache, sync=False
        )

    elif bucket == "convex":
        price = await convex.get_price(token_address, block, skip_cache=skip_cache, sync=False)

    elif bucket == "creth":
        price = await creth.get_price_creth(token_address, block, skip_cache=skip_cache, sync=False)

    elif bucket == "curve lp":
        price = await curve.get_price(token_address, block, skip_cache=skip_cache, sync=False)

    elif bucket == "ellipsis lp":
        price = await ellipsis.get_price(
            token_address, block=block, skip_cache=skip_cache, sync=False
        )

    elif bucket == "froyo":
        price = await froyo.get_price(token_address, block=block, sync=False)

    elif bucket == "gearbox":
        price = await gearbox.get_price(
            token_address, block=block, skip_cache=skip_cache, sync=False
        )

    elif bucket == "gelato":
        price = await gelato.get_price(
            token_address, block=block, skip_cache=skip_cache, sync=False
        )

    elif bucket == "generic amm":
        price = await generic_amm.get_price(
            token_address, block=block, skip_cache=skip_cache, sync=False
        )

    elif bucket == "ib token":
        price = await ib.get_price(token_address, block=block, skip_cache=skip_cache, sync=False)

    elif bucket == "mooniswap lp":
        price = await mooniswap.get_pool_price(
            token_address, block=block, skip_cache=skip_cache, sync=False
        )

    elif bucket == "mstable feeder pool":
        price = await mstablefeederpool.get_price(
            token_address, block=block, skip_cache=skip_cache, sync=False
        )

    elif bucket == "one to one":
        price = await one_to_one.get_price(token_address, block, skip_cache=skip_cache, sync=False)

    elif bucket == "pendle lp":
        price = await pendle.get_lp_price(token_address, block, skip_cache=skip_cache, sync=False)

    elif bucket == "piedao lp":
        price = await piedao.get_price(
            token_address, block=block, skip_cache=skip_cache, sync=False
        )

    elif bucket == "popsicle":
        price = await popsicle.get_price(
            token_address, block=block, skip_cache=skip_cache, sync=False
        )

    elif bucket == "reserve":
        price = await reserve.get_price(
            token_address, block=block, skip_cache=skip_cache, sync=False
        )

    elif bucket == "rkp3r":
        price = await rkp3r.get_price(token_address, block, skip_cache=skip_cache, sync=False)

    elif bucket == "saddle":
        price = await saddle.get_price(token_address, block, skip_cache=skip_cache, sync=False)

    elif bucket == "stargate lp":
        price = await stargate.get_price(
            token_address, block=block, skip_cache=skip_cache, sync=False
        )

    elif bucket == "solidex":
        price = await solidex.get_price(token_address, block, skip_cache=skip_cache, sync=False)

    elif bucket == "synthetix":
        price = await synthetix.get_price(token_address, block, sync=False)

    elif bucket == "token set":
        price = await tokensets.get_price(
            token_address, block=block, skip_cache=skip_cache, sync=False
        )

    elif bucket == "uni or uni-like lp":
        price = await UniswapV2Pool(token_address).get_price(
            block=block, skip_cache=skip_cache, sync=False
        )

    elif bucket == "wrapped gas coin":
        price = await get_price(
            constants.WRAPPED_GAS_COIN, block, skip_cache=skip_cache, sync=False
        )

    elif bucket == "wrapped atoken v2":
        price = await aave.get_price_wrapped_v2(
            token_address, block, skip_cache=skip_cache, sync=False
        )

    elif bucket == "wrapped atoken v3":
        price = await aave.get_price_wrapped_v3(
            token_address, block, skip_cache=skip_cache, sync=False
        )

    elif bucket == "wsteth":
        price = await wsteth.wsteth.get_price(block, skip_cache=skip_cache, sync=False)

    elif bucket == "yearn or yearn-like":
        price = await yearn.get_price(
            token_address,
            block,
            skip_cache=skip_cache,
            ignore_pools=ignore_pools,
            sync=False,
        )

    logger.debug("%s -> %s", bucket, price)

    # Return tuple of (price, bucket_name) for PriceResult construction
    # bucket is the source identifier for the pricing path
    return price, bucket


async def _get_price_from_api(
    token: HexAddress,
    block: BlockNumber,
    logger: Logger,
) -> tuple[UsdPrice | None, str | None]:
    """
    Attempt to get the price from the ypricemagic API.

    Args:
        token: The address of the token to price.
        block: The block number at which to get the price.
        logger: A logger instance for recording debug information.

    Returns:
        A tuple of (price, 'ypriceapi') if the price can be fetched from the ypricemagic API,
        or (None, None) otherwise.
    """
    if utils.ypriceapi.should_use and token not in utils.ypriceapi.skip_tokens:
        price = await utils.ypriceapi.get_price(token, block)
        logger.debug("ypriceapi -> %s", price)
        return price, "ypriceapi"
    return None, None


async def _get_price_from_dexes(
    token: ChecksumAddress,
    block: BlockNumber,
    ignore_pools,
    skip_cache: bool,
    logger: Logger,
    amount: Decimal | int | float | None = None,
) -> tuple[UsdPrice | float | None, dict | None]:
    """
    Attempt to get the price from decentralized exchanges.

    This function tries to fetch the price from various DEXes like Uniswap, Curve, and Balancer.

    Args:
        token: The address of the token to price.
        block : The block number at which to get the price.
        ignore_pools: A tuple of pool addresses to ignore when fetching the price.
        skip_cache: If True, bypass the cache and fetch the price directly.
        logger: A logger instance for recording debug information.
        amount: The amount of tokens (human-readable units) to use for quotes.
            When provided, the price accounts for price impact.

    Returns:
        A tuple of (price, source_info) if the price can be determined from DEXes, or (None, None) otherwise.
        The source_info dict contains keys like 'source' (dex name) and optionally 'pool' (pool address).
    """
    # TODO We need better logic to determine whether to use uniswap, curve, balancer. For now this works for all known cases.
    dexes = [uniswap_multiplexer]
    if curve:
        dexes.append(curve)

    # TODO: make a DexABC, include balancer and future dexes
    # TODO:  this would be so cool if a_sync.map could proxy abstractmethods correctly
    # dexes_by_depth = dict(
    #     await DexABC.check_liquidity.map(dexes, token=token, block=block, ignore_pools=ignore_pools).items(pop=True).sort(lambda k, v: v)
    # )
    liquidity_tasks = []
    for dex in dexes:
        kwargs = {"ignore_pools": ignore_pools, "sync": False}
        if dex is uniswap_multiplexer:
            kwargs["amount"] = amount
        liquidity_tasks.append(dex.check_liquidity(token, block, **kwargs))
    liquidity = await igather(liquidity_tasks)
    depth_to_dex: dict[int, object] = dict(zip(liquidity, dexes))
    dexes_by_depth: dict[int, object] = {
        depth: depth_to_dex[depth] for depth in sorted(depth_to_dex, reverse=True) if depth
    }
    if debug_logs_enabled := logger.isEnabledFor(DEBUG):
        log_debug = lambda msg, *args: logger._log(DEBUG, msg, args)

        log_debug("dexes by depth for %s at block %s: %s", token, block, dexes_by_depth)

    for dex in dexes_by_depth.values():
        method = "get_price"
        if hasattr(dex, "get_price_for_underlying"):
            method += "_for_underlying"
        if debug_logs_enabled:
            log_debug("trying %s", dex)
        price = await getattr(dex, method)(
            token,
            block,
            ignore_pools=ignore_pools,
            skip_cache=skip_cache,
            amount=amount,
            sync=False,
        )
        if debug_logs_enabled:
            log_debug("%s -> %s", dex, price)
        if price:
            # Build source_info for PriceStep
            dex_name = getattr(dex, "__name__", str(dex))
            source_info = {"source": dex_name, "pool": None}
            return price, source_info

    if debug_logs_enabled:
        log_debug(
            "no %s %s liquidity found on primary markets",
            await ERC20(token, asynchronous=True).symbol,
            token,
        )

    # If price is 0, we can at least try to see if balancer gives us a price. If not, its probably a shitcoin.
    if price := await balancer_multiplexer.get_price(
        token,
        block=block,
        skip_cache=skip_cache,
        ignore_pools=ignore_pools,
        amount=amount,
        sync=False,
    ):
        if debug_logs_enabled:
            log_debug("balancer -> %s", price)
        source_info = {"source": "balancer", "pool": None}
        return price, source_info

    return None, None


def _fail_appropriately(
    logger: Logger,
    symbol: str,
    fail_to_None: bool,
    silent: bool,
) -> None:
    """
    Handle failure to get a price appropriately.

    This function decides how to handle a failure to get a price based on the input parameters.

    Args:
        logger: A logger instance for recording error information.
        symbol: The symbol of the token whose price couldn't be determined.
        fail_to_None: If True, the function will return silently. If False, it will raise a PriceError.
        silent: If True, suppress error logging.

    Raises:
        PriceError: If fail_to_None is False.
    """
    if not silent:
        logger.warning(f"failed to get price for {symbol}")

    if not fail_to_None:
        raise PriceError(logger, symbol)
