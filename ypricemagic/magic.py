import logging
from functools import lru_cache
from typing import Sequence, Union

import brownie
from brownie import convert
from eth_typing.evm import Address, BlockNumber
from hexbytes import HexBytes
from joblib.parallel import Parallel, delayed
from tqdm import tqdm
from y.constants import STABLECOINS, WRAPPED_GAS_COIN, NETWORK_STRING
from y.exceptions import PriceError
from y.prices import _sense_check
from y.utils.cache import memory

from y.contracts import Contract
from ypricemagic.utils.raw_calls import _symbol
from ypricemagic.price_modules import (aave, belt, compound, cream, ellipsis,
                                       froyo, gelato, ib, mooniswap,
                                       mstablefeederpool, piedao, tokensets,
                                       wsteth, yearn)
from ypricemagic.price_modules.balancer.balancer import balancer
from ypricemagic.price_modules.chainlink import chainlink
from ypricemagic.price_modules.curve import curve
from ypricemagic.price_modules.uniswap.uniswap import uniswap

logger = logging.getLogger(__name__)


@memory.cache()
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
    except RecursionError: raise PriceError(f'could not fetch price for {_symbol(token_address)} {token_address} on {NETWORK_STRING}')


def get_prices(
    token_addresses: Sequence[Union[str, Address, brownie.Contract, Contract]],
    block: Union[int, BlockNumber, None] = None,
    fail_to_None: bool = True,
    silent: bool = False
    ):
    '''
    In every case:
    - if `silent == True`, tqdm will not be used
    - if `silent == False`, tqdm will be used

    When `get_prices` is unable to find a price:
    - if `fail_to_None == True`, ypricemagic will return `None` for that token
    - if `fail_to_None == False`, ypricemagic will raise a PriceError and prevent you from receiving prices for your other tokens
    '''
    if not silent:
        token_addresses = tqdm(token_addresses)
    return Parallel(4, 'threading')(delayed(get_price)(token_address, block, fail_to_None=fail_to_None, silent=silent) for token_address in token_addresses)

    
def _get_price(
    token: Union[str, Address, brownie.Contract, Contract], 
    block: Union[int, BlockNumber, None] = None, 
    fail_to_None: bool = False, 
    silent: bool = False
    ):
    logger.debug(f"network: {NETWORK_STRING} token: {token}")
    logger.debug("unwrapping %s", token)

    price, bucket = _exit_early_for_known_tokens(token, block=block)
    if price == 0: return 0 # this happens when a LP token has 0 totalSupply
    if not price: price = uniswap.try_for_price(token, block=block)
    if not price: price = balancer.get_price(token, block=block)
    if not price: _fail_appropriately(token, fail_to_None=fail_to_None, silent=silent)
    if price: _sense_check(token, price, bucket)
    return price


def _exit_early_for_known_tokens(
    token_address: str,
    block = None
    ):

    bucket = check_bucket(token_address)

    price = None

    if bucket == 'atoken':                  price = aave.get_price(token_address, block=block)
    elif bucket == 'balancer pool':         price = balancer.get_price(token_address, block)
    elif bucket == 'belt lp':               price = belt.get_price(token_address, block)

    elif bucket == 'chainlink feed':        price = chainlink.chainlink.get_price(token_address, block)
    elif bucket == 'compound':              price = compound.compound.get_price(token_address, block=block)
    elif bucket == 'creth':                 price = cream.get_price_creth(token_address, block)

    elif bucket == 'curve lp':              price = curve.get_price(token_address, block)
    elif bucket == 'ellipsis lp':           price = ellipsis.get_price(token_address, block=block)
    elif bucket == 'froyo':                 price = froyo.get_price(token_address, block=block)

    elif bucket == 'gelato':                price = gelato.get_price(token_address, block=block)
    elif bucket == 'ib token':              price = ib.get_price(token_address,block=block)
    elif bucket == 'mooniswap lp':          price = mooniswap.get_pool_price(token_address, block=block)

    elif bucket == 'mstable feeder pool':   price = mstablefeederpool.get_price(token_address,block=block)
    elif bucket == 'piedao lp':             price = piedao.get_price(token_address, block=block)
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

    return price if price is not None else None, bucket


@lru_cache(maxsize=None)
def check_bucket(
    token_address: Union[str, Address, brownie.Contract, Contract]
    ):

    if type(token_address) != str:
        token_address = str(token_address)

    # these require neither calls to the chain nor contract initialization
    if token_address == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE":       return 'wrapped gas coin'
    elif token_address in STABLECOINS:                                      return 'stable usd'

    elif wsteth.is_wsteth(token_address):                                   return 'wsteth'
    elif cream.is_creth(token_address):                                     return 'creth'
    elif belt.is_belt_lp(token_address):                                    return 'belt lp'
    elif froyo.is_froyo(token_address):                                     return 'froyo'

    # these require contract initialization but no calls
    # TODO initialize the contract here and pass it into the below functions to save init time
    # token_contract = Contract(token_address)
    if balancer.is_balancer_pool(token_address):                            return 'balancer pool'
    elif yearn.is_yearn_vault(token_address):                               return 'yearn or yearn-like'
    elif aave.is_atoken(token_address):                                     return 'atoken' 

    elif ib.is_ib_token(token_address):                                     return 'ib token'
    elif gelato.is_gelato_pool(token_address):                              return 'gelato'
    elif piedao.is_pie(token_address):                                      return 'piedao lp'

    elif tokensets.is_token_set(token_address):                             return 'token set'
    elif ellipsis.is_eps_rewards_pool(token_address):                       return 'ellipsis lp'
    elif mstablefeederpool.is_mstable_feeder_pool(token_address):           return 'mstable feeder pool'

    # these require both calls and contract initializations
    elif uniswap.is_uniswap_pool(token_address):                            return 'uni or uni-like lp'
    elif mooniswap.is_mooniswap_pool(token_address):                        return 'mooniswap lp'
    elif compound.compound.is_compound_market(token_address):               return 'compound'
    elif curve and token_address in curve:                                  return 'curve lp'
    elif token_address in chainlink.chainlink:                              return 'chainlink feed'

         
def _fail_appropriately(
    token_address: str, 
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
    if not silent or not fail_to_None:
        symbol = _symbol(token_address)

    if not silent:
        logger.error(f"failed to get price for {symbol} {token_address} on {NETWORK_STRING}")

    if not fail_to_None:
        raise PriceError(f'could not fetch price for {symbol} {token_address} on {NETWORK_STRING}')
