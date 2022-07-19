import asyncio
import logging
import os
from typing import Iterable, List, Optional

from async_lru import alru_cache
from brownie import chain
from brownie.exceptions import ContractNotFound
from multicall.utils import await_awaitable, raise_if_exception_in
from y import convert
from y.classes.common import ERC20
from y.constants import SEMAPHORE, WRAPPED_GAS_COIN
from y.datatypes import AnyAddressType, Block, UsdPrice
from y.exceptions import NonStandardERC20, PriceError
from y.networks import Network
from y.prices import convex, one_to_one, popsicle, yearn
from y.prices.chainlink import chainlink
from y.prices.dex import mooniswap
from y.prices.dex.balancer import balancer_multiplexer
from y.prices.dex.genericamm import generic_amm
from y.prices.dex.uniswap import uniswap_multiplexer
from y.prices.dex.uniswap.uniswap import uniswap_multiplexer
from y.prices.dex.uniswap.v3 import uniswap_v3
from y.prices.eth_derivs import creth, wsteth
from y.prices.lending import ib
from y.prices.lending.aave import aave
from y.prices.lending.compound import compound
from y.prices.stable_swap import belt, froyo, mstablefeederpool, saddle
from y.prices.stable_swap.curve import curve
from y.prices.synthetix import synthetix
from y.prices.tokenized_fund import basketdao, gelato, piedao, tokensets
from y.prices.utils.buckets import check_bucket_async
from y.prices.utils.sense_check import _sense_check
from y.utils.logging import yLazyLogger

logger = logging.getLogger(__name__)

@yLazyLogger(logger)
def get_price(
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
    return await_awaitable(get_price_async(token_address, block, fail_to_None, silent))

#@yLazyLogger(logger)
async def get_price_async(
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
    block = block or chain.height
    token_address = convert.to_address(token_address)

    try:
        async with SEMAPHORE:
            return await _get_price(token_address, block, fail_to_None=fail_to_None, silent=silent)
    except (ContractNotFound, NonStandardERC20, RecursionError):
        if fail_to_None:
            return None
        raise PriceError(f'could not fetch price for {await ERC20(token_address).symbol_async} {token_address} on {Network.printable()}')

def get_prices(
    token_addresses: Iterable[AnyAddressType],
    block: Optional[Block] = None,
    fail_to_None: bool = False,
    silent: bool = False,
    dop: int = int(os.environ.get('DOP',4))
    ) -> List[Optional[float]]:
    '''
    A more optimized way to fetch prices for multiple assets at the same block.

    # NOTE silent kwarg is currently disabled.
    In every case:
    - if `silent == True`, tqdm will not be used
    - if `silent == False`, tqdm will be used

    When `get_prices` is unable to find a price:
    - if `fail_to_None == True`, ypricemagic will return `None` for that token
    - if `fail_to_None == False`, ypricemagic will raise a PriceError and prevent you from receiving prices for your other tokens
    '''
    return await_awaitable(get_prices_async(token_addresses, block=block, fail_to_None=fail_to_None, silent=silent))

async def get_prices_async(
    token_addresses: Iterable[AnyAddressType],
    block: Optional[Block] = None,
    fail_to_None: bool = False,
    silent: bool = False,
    dop: int = int(os.environ.get('DOP',4))
    ) -> List[Optional[float]]:
    '''
    A more optimized way to fetch prices for multiple assets at the same block.

    # NOTE silent kwarg is currently disabled.
    In every case:
    - if `silent == True`, tqdm will not be used
    - if `silent == False`, tqdm will be used

    When `get_prices` is unable to find a price:
    - if `fail_to_None == True`, ypricemagic will return `None` for that token
    - if `fail_to_None == False`, ypricemagic will raise a PriceError and prevent you from receiving prices for your other tokens
    '''
    if dop:
        logger.warn('Kwarg `dop` was Optional in an old impmentation and will be removed in a future implementation. Please remove `dop` from your code.')

    if block is None:
        block = chain.height

    prices = await asyncio.gather(
        *[
            get_price_async(convert.to_address(token), block, fail_to_None=fail_to_None, silent=silent)
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

@alru_cache(maxsize=None)
async def _get_price(
    token: AnyAddressType, 
    block: Block, 
    fail_to_None: bool = False, 
    silent: bool = False
    ) -> Optional[UsdPrice]:

    try:
        symbol = await ERC20(token).symbol_async
    except NonStandardERC20:
        symbol = None
    token_string = f"{symbol} {token}" if symbol else token

    logger.debug("-------------[ y ]-------------")
    logger.debug(f"Fetching price for...")
    logger.debug(f"Token: {token_string}")
    logger.debug(f"Block: {block or 'latest'}") 
    logger.debug(f"Network: {Network.printable()}")

    price = await _exit_early_for_known_tokens(token, block=block)
    if price is not None:
        return price

    if price is None and curve:
        price = await curve.get_price_for_underlying_async(token, block=block)
    
    if price is None and uniswap_v3:
        price = await uniswap_v3.get_price_async(token, block=block)

    if price is None:
        price = await uniswap_multiplexer.get_price_async(token, block=block)

    # If price is 0, we can at least try to see if balancer gives us a price. If not, its probably a shitcoin.
    if price is None or price == 0:
        new_price = await balancer_multiplexer.get_price_async(token, block=block)
        if new_price:
            price = new_price

    if price is None:
        _fail_appropriately(token_string, fail_to_None=fail_to_None, silent=silent)
    if price:
        await _sense_check(token, price)
    return price


@yLazyLogger(logger)
async def _exit_early_for_known_tokens(
    token_address: str,
    block: Block
    ) -> Optional[UsdPrice]:

    bucket = await check_bucket_async(token_address)

    price = None

    if bucket == 'atoken':                  price = await aave.get_price_async(token_address, block=block)
    elif bucket == 'balancer pool':         price = await balancer_multiplexer.get_price_async(token_address, block)
    elif bucket == 'basketdao':             price = await basketdao.get_price_async(token_address, block)

    elif bucket == 'belt lp':               price = await belt.get_price_async(token_address, block)
    elif bucket == 'chainlink feed':        price = await chainlink.get_price_async(token_address, block)
    elif bucket == 'compound':              price = await compound.get_price_async(token_address, block=block)

    elif bucket == 'convex':                price = convex.get_price(token_address,block)
    elif bucket == 'creth':                 price = await creth.get_price_creth_async(token_address, block)
    elif bucket == 'curve lp':              price = await curve.get_price_async(token_address, block)

    elif bucket == 'ellipsis lp':           price = ellipsis.get_price(token_address, block=block)
    elif bucket == 'froyo':                 price = froyo.get_price(token_address, block=block)
    elif bucket == 'gelato':                price = await gelato.get_price_async(token_address, block=block)

    elif bucket == 'generic amm':           price = await generic_amm.get_price_async(token_address, block=block)
    elif bucket == 'ib token':              price = ib.get_price(token_address,block=block)
    elif bucket == 'mooniswap lp':          price = await mooniswap.get_pool_price_async(token_address, block=block)

    elif bucket == 'mstable feeder pool':   price = await mstablefeederpool.get_price_async(token_address,block=block)
    elif bucket == 'one to one':            price = one_to_one.get_price(token_address, block)
    elif bucket == 'piedao lp':             price = await piedao.get_price_async(token_address, block=block)
    elif bucket == 'popsicle':              price = await popsicle.get_price_async(token_address, block=block)

    elif bucket == 'saddle':                price = await saddle.get_price_async(token_address, block)
    elif bucket == 'stable usd':            price = 1
    elif bucket == 'synthetix':             price = await synthetix.get_price_async(token_address, block)

    elif bucket == 'token set':             price = await tokensets.get_price_async(token_address, block=block)
    elif bucket == 'uni or uni-like lp':    price = await uniswap_multiplexer.lp_price_async(token_address, block)
    elif bucket == 'wrapped gas coin':      price = await get_price_async(WRAPPED_GAS_COIN, block)

    elif bucket == 'wsteth':                price = await wsteth.wsteth.get_price_async(block)
    elif bucket == 'yearn or yearn-like':   price = await yearn.get_price_async(token_address, block)

    return price

         
def _fail_appropriately(
    token_string: str, 
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
        logger.error(f"failed to get price for {token_string} on {Network.printable()}")

    if not fail_to_None:
        raise PriceError(f'could not fetch price for {token_string} on {Network.printable()}')
