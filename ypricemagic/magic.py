import logging
from functools import lru_cache
from typing import Sequence, Union

import brownie
from brownie import convert
from eth_typing.evm import Address, BlockNumber
from hexbytes import HexBytes
from joblib.parallel import Parallel, delayed
from tqdm import tqdm
from y.constants import WRAPPED_GAS_COIN
from y.contracts import Contract
from y.decorators import log
from y.exceptions import PriceError
from y.networks import Network
from y.prices import _sense_check

from ypricemagic.buckets import check_bucket
from ypricemagic.price_modules import *
from ypricemagic.price_modules.aave import aave
from ypricemagic.price_modules.balancer.balancer import balancer
from ypricemagic.price_modules.chainlink.chainlink import chainlink
from ypricemagic.price_modules.compound import compound
from ypricemagic.price_modules.curve import curve
from ypricemagic.price_modules.uniswap.uniswap import uniswap
from ypricemagic.utils.raw_calls import _symbol

logger = logging.getLogger(__name__)


@log(logger)
@lru_cache(maxsize=None)
def get_price(
    token_address: Union[str, Address, brownie.Contract, Contract, int],
        # Don't pass an int like `123` into `token_address` please, that's just silly/
        # ypricemagic accepts ints to allow you to pass `y.get_price(0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e)`
        # so you can save yourself some keystrokes while testing in a console
        # (as opposed to `y.get_price("0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e")` )
    block: Union[BlockNumber, int, None] = None, 
    fail_to_None: bool = False, 
    silent: bool = False
    ) -> float:
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

    # see comments above to see why we do this
    if type(token_address) == int:
        token_address = HexBytes(token_address)

    token_address = convert.to_address(token_address)
    try: return _get_price(token_address, block=block, fail_to_None=fail_to_None, silent=silent)
    except RecursionError:
        if fail_to_None: return None
        else: raise PriceError(f'could not fetch price for {_symbol(token_address)} {token_address} on {Network.printable()}')


def get_prices(
    token_addresses: Sequence[Union[str, Address, brownie.Contract, Contract]],
    block: Union[int, BlockNumber, None] = None,
    fail_to_None: bool = False,
    silent: bool = False,
    dop: int = 4
    ):
    '''
    In every case:
    - if `silent == True`, tqdm will not be used
    - if `silent == False`, tqdm will be used

    When `get_prices` is unable to find a price:
    - if `fail_to_None == True`, ypricemagic will return `None` for that token
    - if `fail_to_None == False`, ypricemagic will raise a PriceError and prevent you from receiving prices for your other tokens
    '''
    if not silent: token_addresses = tqdm(token_addresses)
    return Parallel(dop, 'threading')(delayed(get_price)(token_address, block, fail_to_None=fail_to_None, silent=silent) for token_address in token_addresses)

    
def _get_price(
    token: Union[str, Address, brownie.Contract, Contract], 
    block: Union[int, BlockNumber, None] = None, 
    fail_to_None: bool = False, 
    silent: bool = False
    ):

    symbol = _symbol(token, return_None_on_failure=True)
    token_string = f"{symbol} {token}" if symbol else token

    logger.debug("-------------[ y ]-------------")
    logger.debug(f"Fetching price for...")
    logger.debug(f"Token: {token_string}")
    logger.debug(f"Block: {block or 'latest'}") 
    logger.debug(f"Network: {Network.printable()}")

    price = _exit_early_for_known_tokens(token, block=block)
    if price == 0: return 0 # this happens when a LP token has 0 totalSupply
    if not price: price = uniswap.try_for_price(token, block=block)
    if not price: price = balancer.get_price(token, block=block)
    if not price: _fail_appropriately(token_string, fail_to_None=fail_to_None, silent=silent)
    if price: _sense_check(token, price)
    return price


@log(logger)
def _exit_early_for_known_tokens(
    token_address: str,
    block = None
    ):

    bucket = check_bucket(token_address)

    price = None

    if bucket == 'atoken':                  price = aave.get_price(token_address, block=block)
    elif bucket == 'balancer pool':         price = balancer.get_price(token_address, block)
    elif bucket == 'belt lp':               price = belt.get_price(token_address, block)

    elif bucket == 'chainlink feed':        price = chainlink.get_price(token_address, block)
    elif bucket == 'compound':              price = compound.get_price(token_address, block=block)
    elif bucket == 'creth':                 price = cream.get_price_creth(token_address, block)

    elif bucket == 'curve lp':              price = curve.get_price(token_address, block)
    elif bucket == 'ellipsis lp':           price = ellipsis.get_price(token_address, block=block)
    elif bucket == 'froyo':                 price = froyo.get_price(token_address, block=block)

    elif bucket == 'gelato':                price = gelato.get_price(token_address, block=block)
    elif bucket == 'ib token':              price = ib.get_price(token_address,block=block)
    elif bucket == 'mooniswap lp':          price = mooniswap.get_pool_price(token_address, block=block)

    elif bucket == 'mstable feeder pool':   price = mstablefeederpool.get_price(token_address,block=block)
    elif bucket == 'piedao lp':             price = piedao.get_price(token_address, block=block)
    elif bucket == 'saddle':                price = saddle.get_price(token_address, block)
    elif bucket == 'stable usd':            price = 1

    elif bucket == 'token set':             price = tokensets.get_price(token_address, block=block)
    elif bucket == 'uni or uni-like lp':    price = uniswap.lp_price(token_address, block)
    elif bucket == 'wrapped gas coin':      price = get_price(WRAPPED_GAS_COIN, block)

    elif bucket == 'wsteth':                price = wsteth.wsteth.get_price(block)
    elif bucket == 'yearn or yearn-like':   price = yearn.get_price(token_address, block)

    # if type(price) == list, this will output final price
    if isinstance(price, list):
        price, underlying = price
        logger.debug("peel %s %s", price, underlying)
        price *= get_price(underlying, block=block)

    logger.debug(f"{bucket} -> ${price}")

    return price if price is not None else None

         
def _fail_appropriately(
    token_string: str, 
    fail_to_None: bool = False, 
    silent: bool = False
    ):
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
