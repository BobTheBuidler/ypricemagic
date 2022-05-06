import logging
import os
from functools import lru_cache
from typing import Iterable, List, Optional

from brownie import chain
from brownie.exceptions import ContractNotFound
from joblib.parallel import Parallel, delayed
from multicall import Call, Multicall
from tqdm import tqdm
from y import convert
from y.constants import WRAPPED_GAS_COIN
from y.datatypes import UsdPrice
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
from y.prices.utils.buckets import check_bucket
from y.prices.utils.sense_check import _sense_check
from y.typing import AnyAddressType, Block
from y.utils.logging import yLazyLogger
from y.utils.raw_calls import _symbol

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
    block = block or chain.height
    token_address = convert.to_address(token_address)

    try:
        return _get_price(token_address, block, fail_to_None=fail_to_None, silent=silent)
    except (ContractNotFound, NonStandardERC20, RecursionError):
        if fail_to_None:
            return None
        raise PriceError(f'could not fetch price for {_symbol(token_address)} {token_address} on {Network.printable()}')


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

    if block is None:
        block = chain.height

    token_addresses = [convert.to_address(token) for token in token_addresses]

    # First we exit early for known token subtypes. There are too many of these to optimize right now.
    early_exits = Parallel(dop,'threading')(delayed(_exit_early_for_known_tokens)(token, block) for token in tqdm(token_addresses))
    early_exits = {i:price for i, price in enumerate(early_exits) if price is not None}

    # Now lets try a few other things, some optimized for speed and some optimized for shit

    ## CURVE
    if curve:
        try_curve = [i for i in range(len(token_addresses)) if i not in early_exits]
        prices = Parallel(dop, 'threading')(delayed(curve.get_price_for_underlying)(token_addresses[i], block) for i  in tqdm(try_curve))
        for i, price in zip(try_curve, prices):
            if price is not None:
                early_exits[i] = price

    ## UNISWAP V3
    if uniswap_v3:
        try_uni_v3 = [i for i in range(len(token_addresses)) if i not in early_exits]
        prices = Parallel(dop, 'threading')(delayed(uniswap_v3.get_price)(token_addresses[i], block) for i in tqdm(try_uni_v3))
        for i, price in zip(try_uni_v3, prices):
            if price is not None:
                early_exits[i] = price

    ## UNISWAP V2
    try_uni_v2 = [i for i in range(len(token_addresses)) if i not in early_exits]
    prices = uniswap_multiplexer._get_prices([token_addresses[i] for i in try_uni_v2], block, dop=dop)
    for i, price in zip(try_uni_v2, prices):
        if price:
            early_exits[i] = price

    ## UNISWAP V1
    if chain.id == Network.Mainnet:
        try_uni_v1 = [i for i in range(len(token_addresses)) if i not in early_exits]
        prices = Parallel(dop, 'threading')(delayed(uniswap_multiplexer.get_price_v1)(token_addresses[i], block) for i in tqdm(try_uni_v1))
        for i, price in zip(try_uni_v1, prices):
            if price:
                early_exits[i] = price
    
    ## BALANCER
    try_balancer = [i for i in range(len(token_addresses)) if i not in early_exits]
    prices = Parallel(dop, 'threading')(delayed(balancer_multiplexer.get_price)(token_addresses[i], block) for i in tqdm(try_balancer))
    for i, price in zip(try_balancer, prices):
        if price:
            early_exits[i] = price
    
    # Do we need to raise a PriceError?
    if not fail_to_None:
        for i in range(len(token_addresses)):
            if i not in early_exits:
                raise PriceError('dev: fill this in with better deets')
    
    # Fill in missing prices with Nones.
    for i in range(len(token_addresses)):
        if i not in early_exits:
            early_exits[i] = None
    
    # Sense check results.
    for i, price in early_exits.items():
        if price is not None:
            token = token_addresses[i]
            _sense_check(token, price)

    return [early_exits[i] for i in sorted(early_exits.keys())]


@lru_cache(maxsize=None)
def _get_price(
    token: AnyAddressType, 
    block: Block, 
    fail_to_None: bool = False, 
    silent: bool = False
    ) -> Optional[UsdPrice]:

    symbol = _symbol(token, return_None_on_failure=True)
    token_string = f"{symbol} {token}" if symbol else token

    logger.debug("-------------[ y ]-------------")
    logger.debug(f"Fetching price for...")
    logger.debug(f"Token: {token_string}")
    logger.debug(f"Block: {block or 'latest'}") 
    logger.debug(f"Network: {Network.printable()}")

    price = _exit_early_for_known_tokens(token, block=block)
    if price is not None:
        return price

    if price is None and curve:
        price = curve.get_price_for_underlying(token, block=block)
    
    if price is None and uniswap_v3:
        price = uniswap_v3.get_price(token, block=block)

    if price is None:
        price = uniswap_multiplexer.get_price(token, block=block)

    # If price is 0, we can at least try to see if balancer gives us a price. If not, its probably a shitcoin.
    if price is None or price == 0:
        new_price = balancer_multiplexer.get_price(token, block=block)
        if new_price:
            price = new_price

    if price is None:
        _fail_appropriately(token_string, fail_to_None=fail_to_None, silent=silent)
    if price:
        _sense_check(token, price)
    return price


@yLazyLogger(logger)
def _exit_early_for_known_tokens(
    token_address: str,
    block: Block
    ) -> Optional[UsdPrice]:

    bucket = check_bucket(token_address)

    price = None

    if bucket == 'atoken':                  price = aave.get_price(token_address, block=block)
    elif bucket == 'balancer pool':         price = balancer_multiplexer.get_price(token_address, block)
    elif bucket == 'basketdao':             price = basketdao.get_price(token_address, block)

    elif bucket == 'belt lp':               price = belt.get_price(token_address, block)
    elif bucket == 'chainlink feed':        price = chainlink.get_price(token_address, block)
    elif bucket == 'compound':              price = compound.get_price(token_address, block=block)

    elif bucket == 'convex':                price = convex.get_price(token_address,block)
    elif bucket == 'creth':                 price = creth.get_price_creth(token_address, block)
    elif bucket == 'curve lp':              price = curve.get_price(token_address, block)

    elif bucket == 'ellipsis lp':           price = ellipsis.get_price(token_address, block=block)
    elif bucket == 'froyo':                 price = froyo.get_price(token_address, block=block)
    elif bucket == 'gelato':                price = gelato.get_price(token_address, block=block)

    elif bucket == 'generic amm':           price = generic_amm.get_price(token_address, block=block)
    elif bucket == 'ib token':              price = ib.get_price(token_address,block=block)
    elif bucket == 'mooniswap lp':          price = mooniswap.get_pool_price(token_address, block=block)

    elif bucket == 'mstable feeder pool':   price = mstablefeederpool.get_price(token_address,block=block)
    elif bucket == 'one to one':            price = one_to_one.get_price(token_address, block)
    elif bucket == 'piedao lp':             price = piedao.get_price(token_address, block=block)
    elif bucket == 'popsicle':              price = popsicle.get_price(token_address, block=block)

    elif bucket == 'saddle':                price = saddle.get_price(token_address, block)
    elif bucket == 'stable usd':            price = 1
    elif bucket == 'synthetix':             price = synthetix.get_price(token_address, block)

    elif bucket == 'token set':             price = tokensets.get_price(token_address, block=block)
    elif bucket == 'uni or uni-like lp':    price = uniswap_multiplexer.lp_price(token_address, block)
    elif bucket == 'wrapped gas coin':      price = get_price(WRAPPED_GAS_COIN, block)

    elif bucket == 'wsteth':                price = wsteth.wsteth.get_price(block)
    elif bucket == 'yearn or yearn-like':   price = yearn.get_price(token_address, block)

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
