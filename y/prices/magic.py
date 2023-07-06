import asyncio
import logging
from typing import Iterable, List, NoReturn, Optional

import a_sync
from brownie import ZERO_ADDRESS, chain
from brownie.exceptions import ContractNotFound
from multicall.utils import raise_if_exception_in

from y import ENVIRONMENT_VARIABLES as ENVS
from y import constants, convert
from y.classes.common import ERC20
from y.datatypes import AnyAddressType, Block, UsdPrice
from y.decorators import stuck_coro_debugger
from y.exceptions import NonStandardERC20, PriceError, yPriceMagicError
from y.prices import convex, one_to_one, popsicle, yearn
from y.prices.band import band
from y.prices.chainlink import chainlink
from y.prices.dex import mooniswap
from y.prices.dex.balancer import balancer_multiplexer
from y.prices.dex.genericamm import generic_amm
from y.prices.dex.uniswap import uniswap_multiplexer
from y.prices.dex.uniswap.uniswap import uniswap_multiplexer
from y.prices.dex.uniswap.v3 import uniswap_v3
from y.prices.eth_derivs import creth, wsteth
from y.prices.gearbox import gearbox
from y.prices.lending import ib
from y.prices.lending.aave import aave
from y.prices.lending.compound import compound
from y.prices.stable_swap import (belt, ellipsis, froyo, mstablefeederpool,
                                  saddle)
from y.prices.stable_swap.curve import curve
from y.prices.synthetix import synthetix
from y.prices.tokenized_fund import basketdao, gelato, piedao, tokensets
from y.prices.utils import ypriceapi
from y.prices.utils.buckets import check_bucket
from y.prices.utils.sense_check import _sense_check
from y.utils.dank_mids import dank_w3
from y.utils.logging import _get_price_logger


@a_sync.a_sync(default='sync')
async def get_price(
    token_address: AnyAddressType,
    block: Optional[Block] = None, 
    fail_to_None: bool = False, 
    silent: bool = False
    ) -> Optional[UsdPrice]:
    '''
    Don't pass an int like `123` into `token_address` please, that's just silly.
    - ypricemagic accepts ints to allow you to pass `y.get_price(0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e)`
        so you can save yourself some keystrokes while testing in a console
    - (as opposed to `y.get_price("0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e")`)

    When `get_price` is unable to find a price:
    - If `silent == True`, ypricemagic will print an error message using standard python logging
    - If `silent == False`, ypricemagic will not log any error
    - If `fail_to_None == True`, ypricemagic will return `None`
    - If `fail_to_None == False`, ypricemagic will raise a PriceError
    '''
    block = block or await dank_w3.eth.block_number
    token_address = convert.to_address(token_address)
    try:
        return await _get_price(token_address, block, fail_to_None=fail_to_None, silent=silent)
    except (ContractNotFound, NonStandardERC20, RecursionError, PriceError) as e:
        symbol = await ERC20(token_address, asynchronous=True).symbol
        if not fail_to_None:
            raise yPriceMagicError(e, token_address, block, symbol) from e

@a_sync.a_sync(default='sync')
async def get_prices(
    token_addresses: Iterable[AnyAddressType],
    block: Optional[Block] = None,
    fail_to_None: bool = False,
    silent: bool = False,
    ) -> List[Optional[float]]:
    '''
    A more optimized way to fetch prices for multiple assets at the same block.

    # NOTE silent kwarg is currently disabled.
    In every case:
    - if `silent == True`, tqdm will not be used
    - if `silent == False`, tqdm will be used

    When `get_prices` is unable to find a price:
    - if `fail_to_None == True`, ypricemagic will return `None` for that token
    - if `fail_to_None == False`, ypricemagic will raise a yPriceMagicError
    '''

    if block is None:
        block = chain.height

    prices = await asyncio.gather(
        *[
            get_price(convert.to_address(token), block, fail_to_None=fail_to_None, silent=silent, sync=False)
            for token in token_addresses
        ],
        return_exceptions=True
    )

    if not fail_to_None:
        raise_if_exception_in(prices)
    else:
        for p in prices:
            if isinstance(p, Exception) and not isinstance(p, PriceError):
                raise p
    return prices

@a_sync.a_sync(cache_type='memory', ram_cache_ttl=ENVS.CACHE_TTL)
@stuck_coro_debugger
async def _get_price(
    token: AnyAddressType, 
    block: Block, 
    fail_to_None: bool = False, 
    silent: bool = False
    ) -> Optional[UsdPrice]:  # sourcery skip: remove-redundant-if

    try:
        # We do this to cache the symbol for later, otherwise some repr woudl break
        symbol = await ERC20(token, asynchronous=True).symbol
    except NonStandardERC20:
        symbol = None

    logger = _get_price_logger(token, block, 'magic')
    logger.debug(f'fetching price for {symbol}')
    logger._debugger = asyncio.create_task(_debug_tsk(symbol, logger))

    # Helps to detect stuck code
    try:
        if token == ZERO_ADDRESS:
            _fail_appropriately(logger, symbol, fail_to_None=fail_to_None, silent=silent)
            logger._debugger.cancel()
            return None

        if ypriceapi.should_use and token not in ypriceapi.skip_tokens:
            price = await ypriceapi.get_price(token, block)
            logger.debug(f"ypriceapi -> {price}")
            if price is not None:
                logger.debug(f"{symbol} price: {price}")
                logger._debugger.cancel()
                return price

        price = await _exit_early_for_known_tokens(token, block=block)
        logger.debug(f"early exit -> {price}")
        if price is not None:
            logger.debug(f"{symbol} price: {price}")
            logger._debugger.cancel()
            return price
        
        # TODO We need better logic to determine whether to use univ2, univ3, curve, balancer. For now this works for all known cases.
        # TODO should we use a liuidity-based method to determine this? 
        if price is None and uniswap_v3:
            price = await uniswap_v3.get_price(token, block=block, sync=False)
            logger.debug(f"uniswap v3 -> {price}")

        if price is None:
            price = await uniswap_multiplexer.get_price(token, block=block, sync=False)
            logger.debug(f"uniswap v2 -> {price}")
            
        # NOTE: We want this to go last, to hopefully prevent issues with recursion, ie sdANGLE.
        #       We previously had this before uniswap v3, but sdANGLE would create a recursion error by trying to price ANGLE via curve instead of viable uniswap v2.
        if price is None and curve: 
            price = await curve.get_price_for_underlying(token, block=block, sync=False)
            logger.debug(f"curve -> {price}")

        # If price is 0, we can at least try to see if balancer gives us a price. If not, its probably a shitcoin.
        if price is None or price == 0:
            new_price = await balancer_multiplexer.get_price(token, block=block, sync=False)
            logger.debug(f"balancer -> {price}")
            if new_price:
                logger.debug(f"replacing price {price} with new price {new_price}")
                price = new_price

        if price is None:
            _fail_appropriately(logger, symbol, fail_to_None=fail_to_None, silent=silent)
        if price:
            await _sense_check(token, price)

        logger.debug(f"{symbol} price: {price}")
        # Don't need this anymore
        logger._debugger.cancel()
        return price
    except Exception as e:
        logger._debugger.cancel()
        raise e


async def _exit_early_for_known_tokens(
    token_address: str,
    block: Block
    ) -> Optional[UsdPrice]:  # sourcery skip: low-code-quality

    bucket = await check_bucket(token_address, sync=False)

    price = None

    if bucket == 'atoken':                  price = await aave.get_price(token_address, block=block, sync=False)
    elif bucket == 'balancer pool':         price = await balancer_multiplexer.get_price(token_address, block, sync=False)
    elif bucket == 'basketdao':             price = await basketdao.get_price(token_address, block, sync=False)

    elif bucket == 'belt lp':               price = await belt.get_price(token_address, block, sync=False)
    elif bucket == 'chainlink and band':    price = await chainlink.get_price(token_address, block, sync=False) or await band.get_price(token_address, block, sync=False)
    elif bucket == 'chainlink feed':        price = await chainlink.get_price(token_address, block, sync=False)

    elif bucket == 'compound':              price = await compound.get_price(token_address, block=block, sync=False)
    elif bucket == 'convex':                price = await convex.get_price(token_address,block, sync=False)
    elif bucket == 'creth':                 price = await creth.get_price_creth(token_address, block, sync=False)

    elif bucket == 'curve lp':              price = await curve.get_price(token_address, block, sync=False)
    elif bucket == 'ellipsis lp':           price = await ellipsis.get_price(token_address, block=block, sync=False)
    elif bucket == 'froyo':                 price = await froyo.get_price(token_address, block=block, sync=False)

    elif bucket == 'gearbox':               price = await gearbox.get_price(token_address, block=block, sync=False)
    elif bucket == 'gelato':                price = await gelato.get_price(token_address, block=block, sync=False)
    elif bucket == 'generic amm':           price = await generic_amm.get_price(token_address, block=block, sync=False)
    
    elif bucket == 'ib token':              price = await ib.get_price(token_address, block=block, sync=False)
    elif bucket == 'mooniswap lp':          price = await mooniswap.get_pool_price(token_address, block=block, sync=False)
    elif bucket == 'mstable feeder pool':   price = await mstablefeederpool.get_price(token_address,block=block, sync=False)
    
    elif bucket == 'one to one':            price = await one_to_one.get_price(token_address, block, sync=False)
    elif bucket == 'piedao lp':             price = await piedao.get_price(token_address, block=block, sync=False)
    elif bucket == 'popsicle':              price = await popsicle.get_price(token_address, block=block, sync=False)
    
    elif bucket == 'saddle':                price = await saddle.get_price(token_address, block, sync=False)
    elif bucket == 'stable usd':            price = 1
    elif bucket == 'synthetix':             price = await synthetix.get_price(token_address, block, sync=False)
    
    elif bucket == 'token set':             price = await tokensets.get_price(token_address, block=block, sync=False)
    elif bucket == 'uni or uni-like lp':    price = await uniswap_multiplexer.lp_price(token_address, block, sync=False)
    elif bucket == 'wrapped gas coin':      price = await get_price(constants.WRAPPED_GAS_COIN, block, sync=False)
    
    elif bucket == 'wrapped atoken v2':     price = await aave.get_price_wrapped_v2(token_address, block, sync=False)
    elif bucket == 'wrapped atoken v3':     price = await aave.get_price_wrapped_v3(token_address, block, sync=False)
    elif bucket == 'wsteth':                price = await wsteth.wsteth.get_price(block, sync=False)
    
    elif bucket == 'yearn or yearn-like':   price = await yearn.get_price(token_address, block, sync=False)

    return price

         
def _fail_appropriately(
    logger: logging.Logger,
    symbol: str, 
    fail_to_None: bool = False, 
    silent: bool = False
    ) -> None:
    '''
    dictates how `magic.get_price()` will handle failures

    when `get_price` is unable to find a price:
        if `silent == True`, ypricemagic will print an error message using standard python logging
        if `silent == False`, ypricemagic will not log any error
        if `fail_to_None == True`, ypricemagic will return `None`
        if `fail_to_None == False`, ypricemagic will raise a PriceError
    '''
    if not silent:
        logger.warning(f"failed to get price for {symbol}")

    if not fail_to_None:
        raise PriceError(logger, symbol)

async def _debug_tsk(symbol: str, logger: logging.Logger) -> NoReturn:
    """Prints a log every 1 minute until the creating coro returns"""
    while True:
        await asyncio.sleep(60)
        logger.debug(f"price still fetching for {symbol}")
