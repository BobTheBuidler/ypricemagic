import asyncio
import functools
import logging
from typing import (Callable, Dict, Iterable, List, Literal, 
                    Optional, Tuple, TypeVar, overload)

import a_sync
import dank_mids
from brownie import ZERO_ADDRESS
from brownie.exceptions import ContractNotFound
from typing_extensions import ParamSpec

from y import ENVIRONMENT_VARIABLES as ENVS
from y import constants, convert
from y._decorators import stuck_coro_debugger
from y.classes import ERC20
from y.datatypes import AnyAddressType, Block, Pool, UsdPrice
from y.exceptions import NonStandardERC20, PriceError, yPriceMagicError
from y.prices import band, chainlink, convex, one_to_one, pendle, popsicle, rkp3r, solidex, utils, yearn
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

cache_logger = logging.getLogger(f"{__name__}.cache")


@overload
async def get_price(
    token_address: AnyAddressType,
    block: Optional[Block] = None,
    *,
    fail_to_None: Literal[True],
    skip_cache: bool = ENVS.SKIP_CACHE,
    ignore_pools: Tuple[Pool, ...] = (),
    silent: bool = False,
) -> Optional[UsdPrice]:...

@overload
async def get_price(
    token_address: AnyAddressType,
    block: Optional[Block] = None,
    *,
    fail_to_None: bool = False,
    skip_cache: bool = ENVS.SKIP_CACHE,
    ignore_pools: Tuple[Pool, ...] = (),
    silent: bool = False,
) -> UsdPrice:...

@a_sync.a_sync(default='sync')
async def get_price(
    token_address: AnyAddressType,
    block: Optional[Block] = None,
    *,
    fail_to_None: bool = False,
    skip_cache: bool = ENVS.SKIP_CACHE,
    ignore_pools: Tuple[Pool, ...] = (),
    silent: bool = False,
) -> Optional[UsdPrice]:
    """
    Get the price of a token in USD.

    Args:
        token_address: The address of the token to price.
        block (optional): The block number at which to get the price. If None, uses the latest block.
        fail_to_None (optional): If True, return None instead of raising a :class:`~yPriceMagicError` on failure. Default False.
        skip_cache (optional): If True, bypass the cache and fetch the price directly. Defaults to :obj:`ENVS.SKIP_CACHE`.
        ignore_pools (optional): A tuple of pool addresses to ignore when fetching the price.
        silent (optional): If True, suppress error logging. Default False.

    Returns:
        The price of the token in USD, or None if the price couldn't be determined and fail_to_None is True.

    Raises:
        yPriceMagicError: If the price couldn't be determined and fail_to_None is False.
    
    Note:
        Don't pass an int like `123` into `token_address` please, that's just silly.
        - ypricemagic accepts ints to allow you to pass `y.get_price(0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e)`
            so you can save yourself some keystrokes while testing in a console
        - (as opposed to `y.get_price("0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e")`)
    """
    block = block or await dank_mids.eth.block_number
    token_address = convert.to_address(token_address)
    try:
        return await _get_price(token_address, block, fail_to_None=fail_to_None, ignore_pools=ignore_pools, skip_cache=skip_cache, silent=silent)
    except (ContractNotFound, NonStandardERC20, PriceError) as e:
        symbol = await ERC20(token_address, asynchronous=True).symbol
        if not fail_to_None:
            raise_from = None if isinstance(e, PriceError) else e
            raise yPriceMagicError(e, token_address, block, symbol) from raise_from



@overload
async def get_prices(
    token_addresses: Iterable[AnyAddressType],
    block: Optional[Block] = None,
    *,
    fail_to_None: Literal[True],
    skip_cache: bool = ENVS.SKIP_CACHE,
    silent: bool = False,
) -> List[Optional[UsdPrice]]:...

@overload
async def get_prices(
    token_addresses: Iterable[AnyAddressType],
    block: Optional[Block] = None,
    *,
    fail_to_None: bool = False,
    skip_cache: bool = ENVS.SKIP_CACHE,
    silent: bool = False,
) -> List[UsdPrice]:...

@a_sync.a_sync(default='sync')
async def get_prices(
    token_addresses: Iterable[AnyAddressType],
    block: Optional[Block] = None,
    *,
    fail_to_None: bool = False,
    skip_cache: bool = ENVS.SKIP_CACHE,
    silent: bool = False,
) -> List[Optional[UsdPrice]]:
    """
    Get prices for multiple tokens in USD.

    You should use this function over :func:`get_price` where possible, it is better optimized for parallel execution.

    Args:
        token_addresses: An iterable of token addresses to price.
        block (optional): The block number at which to get the prices. Defaults to the latest block.
        fail_to_None (optional): If True, return None for tokens whose price couldn't be determined. Default False.
        skip_cache (optional): If True, bypass the cache and fetch prices directly. Defaults to :obj:`ENVS.SKIP_CACHE`.
        silent (optional): If True, suppress progress bar and error logging. This kwarg is not currently implemented.

    Returns:
        A list of token prices in USD, in the same order as the input token_addresses.
    """
    return await map_prices(
        token_addresses, 
        block or await dank_mids.eth.block_number, 
        fail_to_None=fail_to_None, 
        skip_cache=skip_cache, 
        silent=silent,
    ).values(pop=True)



@overload
def map_prices(
    token_addresses: Iterable[AnyAddressType],
    block: Block,
    *,
    fail_to_None: Literal[True],
    skip_cache: bool = ENVS.SKIP_CACHE,
    silent: bool = False,
) -> a_sync.TaskMapping[AnyAddressType, Optional[UsdPrice]]:...

@overload
def map_prices(
    token_addresses: Iterable[AnyAddressType],
    block: Block,
    *,
    fail_to_None: bool = False,
    skip_cache: bool = ENVS.SKIP_CACHE,
    silent: bool = False,
) -> a_sync.TaskMapping[AnyAddressType, UsdPrice]:...

def map_prices(
    token_addresses: Iterable[AnyAddressType],
    block: Block,
    *,
    fail_to_None: bool = False,
    skip_cache: bool = ENVS.SKIP_CACHE,
    silent: bool = False,
) -> a_sync.TaskMapping[AnyAddressType, Optional[UsdPrice]]:
    """
    Map token addresses to their prices asynchronously.

    Args:
        token_addresses: An iterable of token addresses to price.
        block (optional): The block number at which to get the prices. Defaults to latest block.
        fail_to_None (optional): If True, map to None for tokens whose price couldn't be determined. Default False.
        skip_cache (optional): If True, bypass the cache and fetch prices directly. Defaults to :obj:`ENVS.SKIP_CACHE`.
        silent (optional): If True, suppress error logging. Default False.

    Returns:
        An :class:`a_sync.TaskMapping` object mapping token addresses to their prices.
    """
    return a_sync.map(
        get_price,
        token_addresses,
        block=block, 
        fail_to_None=fail_to_None, 
        skip_cache=skip_cache, 
        silent=silent, 
    )



def __cache(get_price: Callable[_P, _T]) -> Callable[_P, _T]:
    @functools.wraps(get_price)
    async def cache_wrap(
        token: AnyAddressType, 
        block: Block,
        *,
        fail_to_None: bool = False, 
        skip_cache: bool = ENVS.SKIP_CACHE,
        ignore_pools: Tuple[Pool, ...] = (),
        silent: bool = False
    ) -> Optional[UsdPrice]:
        from y._db.utils import price as db
        if not skip_cache and (price := await db.get_price(token, block)):
            cache_logger.debug('disk cache -> %s', price)
            return price
        price = await get_price(token, block=block, fail_to_None=fail_to_None, ignore_pools=ignore_pools, silent=silent)
        if price and not skip_cache:
            db.set_price(token, block, price)
        return price
    return cache_wrap

@stuck_coro_debugger
@a_sync.a_sync(default="async", cache_type='memory', ram_cache_ttl=ENVS.CACHE_TTL)
@__cache
async def _get_price(
    token: AnyAddressType, 
    block: Block,
    *,
    fail_to_None: bool = False, 
    skip_cache: bool = ENVS.SKIP_CACHE,
    ignore_pools: Tuple[Pool, ...] = (),
    silent: bool = False
    ) -> Optional[UsdPrice]:  # sourcery skip: remove-redundant-if
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

    Returns:
        The price of the token in USD, or None if the price couldn't be determined and fail_to_None is True.
    """
    if token == ZERO_ADDRESS:
        _fail_appropriately(logger, symbol, fail_to_None, silent)
        return None
    
    try:
        # We do this to cache the symbol for later, otherwise some repr woudl break
        symbol = await ERC20(token, asynchronous=True).symbol
    except NonStandardERC20:
        symbol = None

    logger = get_price_logger(token, block, symbol=symbol, extra='magic', start_task=True)
    logger.debug('fetching price for %s', symbol)
    try:
        price = await _get_price_from_api(token, block, logger)
        if price is None:
            price = await _exit_early_for_known_tokens(token, block=block, ignore_pools=ignore_pools, skip_cache=skip_cache, logger=logger)
        if price is None:
            price = await _get_price_from_dexes(token, block, ignore_pools, skip_cache, logger)
        if price:
            await utils.sense_check(token, block, price)
        else:
            _fail_appropriately(logger, symbol, fail_to_None, silent)
        logger.debug("%s price: %s", symbol, price)
        if price:  # checks for the erroneous 0 value we see once in a while
            return price
    finally:
        logger.close()

@stuck_coro_debugger
async def _exit_early_for_known_tokens(
    token_address: str,
    block: Block,
    logger: logging.Logger,
    skip_cache: bool = ENVS.SKIP_CACHE,
    ignore_pools: Tuple[Pool, ...] = (),
    ) -> Optional[UsdPrice]:  # sourcery skip: low-code-quality
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
        The price of the token if it can be determined early, or None otherwise.
    """
    bucket = await utils.check_bucket(token_address, sync=False)

    price = None

    if bucket == 'atoken':                  price = await aave.get_price(token_address, block=block, skip_cache=skip_cache, sync=False)
    elif bucket == 'balancer pool':         price = await balancer_multiplexer.get_price(token_address, block, skip_cache=skip_cache, sync=False)
    elif bucket == 'basketdao':             price = await basketdao.get_price(token_address, block, skip_cache=skip_cache, sync=False)

    elif bucket == 'belt lp':               price = await belt.get_price(token_address, block, sync=False)
    elif bucket == 'chainlink and band':    price = await chainlink.get_price(token_address, block, sync=False) or await band.get_price(token_address, block, sync=False)
    elif bucket == 'chainlink feed':        price = await chainlink.get_price(token_address, block, sync=False)

    elif bucket == 'compound':              price = await compound.get_price(token_address, block=block, skip_cache=skip_cache, sync=False)
    elif bucket == 'convex':                price = await convex.get_price(token_address, block, skip_cache=skip_cache, sync=False)
    elif bucket == 'creth':                 price = await creth.get_price_creth(token_address, block, skip_cache=skip_cache, sync=False)

    elif bucket == 'curve lp':              price = await curve.get_price(token_address, block, skip_cache=skip_cache, sync=False)
    elif bucket == 'ellipsis lp':           price = await ellipsis.get_price(token_address, block=block, skip_cache=skip_cache, sync=False)
    elif bucket == 'froyo':                 price = await froyo.get_price(token_address, block=block, sync=False)

    elif bucket == 'gearbox':               price = await gearbox.get_price(token_address, block=block, skip_cache=skip_cache, sync=False)
    elif bucket == 'gelato':                price = await gelato.get_price(token_address, block=block, skip_cache=skip_cache, sync=False)
    elif bucket == 'generic amm':           price = await generic_amm.get_price(token_address, block=block, skip_cache=skip_cache, sync=False)
    
    elif bucket == 'ib token':              price = await ib.get_price(token_address, block=block, skip_cache=skip_cache, sync=False)
    elif bucket == 'mooniswap lp':          price = await mooniswap.get_pool_price(token_address, block=block, skip_cache=skip_cache, sync=False)
    elif bucket == 'mstable feeder pool':   price = await mstablefeederpool.get_price(token_address,block=block, skip_cache=skip_cache, sync=False)
    
    elif bucket == 'one to one':            price = await one_to_one.get_price(token_address, block, skip_cache=skip_cache, sync=False)
    elif bucket == 'pendle lp':             price = await pendle.get_lp_price(token_address, block, skip_cache=skip_cache, sync=False)
    elif bucket == 'piedao lp':             price = await piedao.get_price(token_address, block=block, skip_cache=skip_cache, sync=False)

    elif bucket == 'popsicle':              price = await popsicle.get_price(token_address, block=block, skip_cache=skip_cache, sync=False)
    elif bucket == 'reserve':               price = await reserve.get_price(token_address, block=block, skip_cache=skip_cache, sync=False)
    elif bucket == 'rkp3r':                 price = await rkp3r.get_price(token_address, block, skip_cache=skip_cache, sync=False)

    elif bucket == 'saddle':                price = await saddle.get_price(token_address, block, skip_cache=skip_cache, sync=False)
    elif bucket == 'solidex':               price = await solidex.get_price(token_address, block, skip_cache=skip_cache, sync=False)
    elif bucket == 'stable usd':            price = 1

    elif bucket == 'synthetix':             price = await synthetix.get_price(token_address, block, sync=False)
    elif bucket == 'token set':             price = await tokensets.get_price(token_address, block=block, skip_cache=skip_cache, sync=False)
    elif bucket == 'uni or uni-like lp':    price = await UniswapV2Pool(token_address).get_price(block=block, skip_cache=skip_cache, sync=False)

    elif bucket == 'wrapped gas coin':      price = await get_price(constants.WRAPPED_GAS_COIN, block, skip_cache=skip_cache, sync=False)
    elif bucket == 'wrapped atoken v2':     price = await aave.get_price_wrapped_v2(token_address, block, skip_cache=skip_cache, sync=False)
    elif bucket == 'wrapped atoken v3':     price = await aave.get_price_wrapped_v3(token_address, block, skip_cache=skip_cache, sync=False)

    elif bucket == 'wsteth':                price = await wsteth.wsteth.get_price(block, skip_cache=skip_cache, sync=False)
    elif bucket == 'yearn or yearn-like':   price = await yearn.get_price(token_address, block, skip_cache=skip_cache, ignore_pools=ignore_pools, sync=False)

    logger.debug("%s -> %s", bucket, price)
    return price

async def _get_price_from_api(token: AnyAddressType, block: Block, logger: logging.Logger):
    """
    Attempt to get the price from the ypricemagic API.

    Args:
        token: The address of the token to price.
        block: The block number at which to get the price.
        logger: A logger instance for recording debug information.

    Returns:
        The price of the token if it can be fetched from the ypricemagic API, or None otherwise.
    """
    if utils.ypriceapi.should_use and token not in utils.ypriceapi.skip_tokens:
        price = await utils.ypriceapi.get_price(token, block)
        logger.debug("ypriceapi -> %s", price)
        return price

async def _get_price_from_dexes(token: AnyAddressType, block: Block, ignore_pools, skip_cache: bool, logger: logging.Logger):
    """
    Attempt to get the price from decentralized exchanges.

    This function tries to fetch the price from various DEXes like Uniswap, Curve, and Balancer.

    Args:
        token: The address of the token to price.
        block : The block number at which to get the price.
        ignore_pools: A tuple of pool addresses to ignore when fetching the price.
        skip_cache: If True, bypass the cache and fetch the price directly.
        logger: A logger instance for recording debug information.

    Returns:
        The price of the token if it can be determined from DEXes, or None otherwise.
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
    liquidity = await asyncio.gather(*[dex.check_liquidity(token, block, ignore_pools=ignore_pools, sync=False) for dex in dexes])
    depth_to_dex: Dict[int, object] = dict(zip(liquidity, dexes))
    dexes_by_depth: Dict[int, object] = {depth: depth_to_dex[depth] for depth in sorted(depth_to_dex, reverse=True) if depth}
    logger.debug('dexes by depth: %s', dexes_by_depth)
    for dex in dexes_by_depth.values():
        method = 'get_price_for_underlying' if hasattr(dex, 'get_price_for_underlying') else 'get_price'
        logger.debug("trying %s", dex)
        price = await getattr(dex, method)(token, block, ignore_pools=ignore_pools, skip_cache=skip_cache, sync=False)
        logger.debug("%s -> %s", dex, price)
        if price:
            return price
    logger.debug('no %s liquidity found on primary markets', token)

    # If price is 0, we can at least try to see if balancer gives us a price. If not, its probably a shitcoin.
    if price := await balancer_multiplexer.get_price(token, block=block, skip_cache=skip_cache, sync=False):
        logger.debug("balancer -> %s", price)
        return price
         
def _fail_appropriately(
    logger: logging.Logger,
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
