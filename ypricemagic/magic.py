import logging
from typing import Union

from brownie import chain, convert, multicall
from eth_typing.evm import Address, BlockNumber

from ypricemagic import _symbol
from ypricemagic.constants import STABLECOINS, WRAPPED_GAS_COIN
from ypricemagic.exceptions import PriceError
from ypricemagic.price_modules import (aave, compound, froyo,
                                       mstablefeederpool, uniswap, yearn)
from ypricemagic.price_modules.balancer.balancer import balancer
from ypricemagic.price_modules.chainlink.chainlink import chainlink
from ypricemagic.price_modules.curve import curve
from ypricemagic.utils.cache import memory
from ypricemagic.utils.contracts import Contract

logger = logging.getLogger(__name__)



@memory.cache()
def get_price(token: Union[str,Address,Contract], block: Union[BlockNumber,int,None]=None, silent: bool=False) -> float:
    token = convert.to_address(str(token))
    try: return _get_price(token, block=block,silent=silent)
    except RecursionError: raise PriceError(f'could not fetch price for {_symbol(token)} {token}')

    
def _get_price(token: Union[str,Address,Contract], block: Union[BlockNumber,int,None]=None,silent: bool=False):
    logger.debug(f"[chain{chain.id}] token: {token}")
    logger.debug("unwrapping %s", token)

    price = None

    if token == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE":
        token = WRAPPED_GAS_COIN

    if token in STABLECOINS:
        logger.debug("stablecoin -> %s", 1)
        return 1
    
    if balancer.is_balancer_pool(token): price = balancer.get_price(token, block)
    elif token in chainlink: price = chainlink.get_price(token, block)
    elif curve and token in curve: price = curve.get_price(token, block)
    
    # these return type(price) == list
    elif yearn.is_yearn_vault(token): price = yearn.get_price(token, block=block)
        
    
    # if type(price) == list, this will output final price
    if isinstance(price, list):
        price, underlying = price
        logger.debug("peel %s %s", price, underlying)
        return price * get_price(underlying, block=block)


    if chain.id == 1: # eth mainnet
        from ypricemagic.price_modules import (cream, gelato, mooniswap,
                                               piedao, tokensets, wsteth)
        multicall(address='0x5BA1e12693Dc8F9c48aAD8770482f4739bEeD696')

        

        # we can exit early with known tokens
        if wsteth.is_wsteth(token):
            price = wsteth.get_price(token, block=block)
            logger.debug("wsteth -> %s", price)

        elif aave.is_atoken(token):
            price = aave.get_price(token, block=block)
            logger.debug("atoken -> %s", price)

        elif cream.is_creth(token):
            price = cream.get_price_creth(token, block)
            logger.debug("atoken -> %s", price)

        elif compound.is_compound_market(token):
            price = compound.get_price(token, block=block)
            logger.debug("compound -> %s", price)

        elif uniswap.is_uniswap_pool(token):
            price = uniswap.lp_price(token, block=block)
            logger.debug("uniswap pool -> %s", price)

        elif mooniswap.is_mooniswap_pool(token):
            price = mooniswap.get_pool_price(token, block=block)
            logger.debug("mooniswap pool -> %s", price)

        elif mstablefeederpool.is_mstable_feeder_pool(token):
            price = mstablefeederpool.get_price(token,block=block)
            logger.debug("mstable feeder pool -> %s", price)

        elif tokensets.is_token_set(token):
            price = tokensets.get_price(token, block=block)
            logger.debug("token set -> %s", price)

        elif piedao.is_pie(token):
            price = piedao.get_price(token, block=block)
            logger.debug("piedeo -> %s", price)

        elif gelato.is_gelato_pool(token):
            price = gelato.get_price(token, block=block)
            logger.debug("gelato -> %s", price)
        
        # peel a layer from [multiplier, underlying]
        if isinstance(price, list):
            price, underlying = price
            logger.debug("peel %s %s", price, underlying)
            return price * get_price(underlying, block=block)

        # a few more attempts to fetch a price a token
        if price is None: # NOTE: 'if not price' returns True if price == 0 but we actually only want to proceed if price == None
            price = uniswap.get_price(token, router="sushiswap", block=block)
            logger.debug("sushiswap -> %s", price)
        
        if price is None:
            price = uniswap.get_price(token, router="uniswap", block=block)
            logger.debug("uniswap -> %s", price)
        
        if price is None:
            price = uniswap.get_price_v1(token, block=block)
            logger.debug("uniswap v1 -> %s", price)

        if price is None:
            price = uniswap.get_price(token, router="shibaswap", block=block)

    if chain.id == 56: # binance smart chain
        from ypricemagic.price_modules import belt, ellipsis, ib, mooniswap

        # we can exit early with known tokens
        if belt.is_belt_lp(token):
            price = belt.get_price(token,block=block)
            logger.debug("belt -> %s", price)

        elif compound.is_compound_market(token):
            price = compound.get_price(token, block=block)
            logger.debug("compound -> %s", price)

        elif uniswap.is_uniswap_pool(token):
            price = uniswap.lp_price(token, block=block)
            logger.debug("uniswap pool -> %s", price)

        elif ib.is_ib_token(token):
            price = ib.get_price(token,block=block)
            logger.debug("ib token -> %s", price)

        elif ellipsis.is_eps_rewards_pool(token):
            price = ellipsis.get_price(token, block=block)
            logger.debug("ellipsis pool -> %s", price)

        elif mooniswap.is_mooniswap_pool(token):
            price = mooniswap.get_pool_price(token, block=block)
            logger.debug("mooniswap pool -> %s", price)

        # peel a layer from [multiplier, underlying]
        if isinstance(price, list):
            price, underlying = price
            logger.debug("peel %s %s", price, underlying)
            return price * get_price(underlying, block=block)
        
        if price is None:
            price = uniswap.get_price(token, router="pancakeswapv2", block=block)
            logger.debug("uniswap -> %s", price)

        if price is None:
            price = uniswap.get_price(token, router="pancakeswapv1", block=block)
            logger.debug("uniswap -> %s", price)
        
        if price is None:
            price = uniswap.get_price(token, router="apeswap", block=block)
            logger.debug("uniswap -> %s", price)

        if price is None:
            price = uniswap.get_price(token, router="wault", block=block)
            logger.debug("uniswap -> %s", price)

        if price is None:
            price = uniswap.get_price(token, router="swapliquidity", block=block)
            logger.debug("uniswap -> %s", price)

        if price is None:
            price = uniswap.get_price(token, router="thugswap", block=block)
            logger.debug("uniswap -> %s", price)

        if price is None:
            price = uniswap.get_price(token, router="mdex", block=block)
            logger.debug("uniswap -> %s", price)

        if price is None:
            price = uniswap.get_price(token, router="bakeryswap", block=block)
            logger.debug("uniswap -> %s", price)

        if price is None:
            price = uniswap.get_price(token, router="nyanswop", block=block)
            logger.debug("uniswap -> %s", price)

        if price is None:
            price = uniswap.get_price(token, router="narwhalswap", block=block)
            logger.debug("uniswap -> %s", price)

        if price is None:
            price = uniswap.get_price(token, router="cafeswap", block=block)
            logger.debug("uniswap -> %s", price)

        if price is None:
            price = uniswap.get_price(token, router="jetswap", block=block)
            logger.debug("uniswap -> %s", price)

        if price is None:
            price = uniswap.get_price(token, router="babyswap", block=block)
            logger.debug("uniswap -> %s", price)

        if price is None:
            price = uniswap.get_price(token, router="annex", block=block)
            logger.debug("uniswap -> %s", price)

        if price is None:
            price = uniswap.get_price(token, router="viralata", block=block)
            logger.debug("uniswap -> %s", price)

        if price is None:
            price = uniswap.get_price(token, router="elk", block=block)
            logger.debug("uniswap -> %s", price)

        if price is None:
            price = uniswap.get_price(token, router="pantherswap", block=block)
            logger.debug("uniswap -> %s", price)

        if price is None:
            price = uniswap.get_price(token, router="complus", block=block)
            logger.debug("uniswap -> %s", price)

    if chain.id == 137: # polygon
        # we can exit early with known tokens

        if aave.is_atoken(token):
            price = aave.get_price(token, block=block)
            logger.debug("atoken -> %s", price)

        elif compound.is_compound_market(token):
            price = compound.get_price(token, block=block)
            logger.debug("compound -> %s", price)

        elif mstablefeederpool.is_mstable_feeder_pool(token):
            price = mstablefeederpool.get_price(token,block=block)
            logger.debug("mstable feeder pool -> %s", price)

        elif uniswap.is_uniswap_pool(token):
            price = uniswap.lp_price(token, block=block)
            logger.debug("uniswap pool -> %s", price)

        # peel a layer from [multiplier, underlying]
        if isinstance(price, list):
            price, underlying = price
            logger.debug("peel %s %s", price, underlying)
            return price * get_price(underlying, block=block)
        
        if price is None:
            price = uniswap.get_price(token, router="quickswap", block=block)
            logger.debug("uniswap -> %s", price)

        if price is None:
            price = uniswap.get_price(token, router="sushi", block=block)
            logger.debug("uniswap -> %s", price)

        if price is None:
            price = uniswap.get_price(token, router="apeswap", block=block)
            logger.debug("uniswap -> %s", price)

        if price is None:
            price = uniswap.get_price(token, router="dfyn", block=block)
            logger.debug("uniswap -> %s", price)

        if price is None:
            price = uniswap.get_price(token, router="wault", block=block)
            logger.debug("uniswap -> %s", price)

        if price is None:
            price = uniswap.get_price(token, router="cometh", block=block)
            logger.debug("uniswap -> %s", price)

        if price is None:
            price = uniswap.get_price(token, router="jetswap", block=block)
            logger.debug("uniswap -> %s", price)

        if price is None:
            price = uniswap.get_price(token, router="polyzap", block=block)
            logger.debug("uniswap -> %s", price)

        if price is None:
            price = uniswap.get_price(token, router="cafeswap", block=block)
            logger.debug("uniswap -> %s", price)

    if chain.id == 250: # fantom
        
        # we can exit early with known tokens

        if uniswap.is_uniswap_pool(token):
            price = uniswap.lp_price(token, block)
            logger.debug("uniswap -> %s", price)

        elif froyo.is_froyo(token):
            price = froyo.get_price(token, block=block)
            logger.debug("froyo -> %s", price)

        # peel a layer from [multiplier, underlying]
        if isinstance(price, list):
            price, underlying = price
            logger.debug("peel %s %s", price, underlying)
            return price * get_price(underlying, block=block)
        
        if price is None:
            price = uniswap.get_price(token, router="sushi", block=block)
            logger.debug("uniswap -> %s", price)

        if price is None:
            price = uniswap.get_price(token, router="spookyswap", block=block)
            logger.debug("uniswap -> %s", price)

        if price is None:
            price = uniswap.get_price(token, router="spiritswap", block=block)
            logger.debug("uniswap -> %s", price)

        if price is None:
            price = uniswap.get_price(token, router="paintswap", block=block)
            logger.debug("uniswap -> %s", price)

        if price is None:
            price = uniswap.get_price(token, router="jetswap", block=block)
            logger.debug("uniswap -> %s", price)

    # if type(price) == list, this will output final price
    if isinstance(price, list):
        price, underlying = price
        logger.debug("peel %s %s", price, underlying)
        return price * get_price(underlying, block=block)

    # let's try a few more things
    if price is None:
        price = balancer.get_price(token, block=block)
        logger.debug("balancer -> %s", price)

    if price is None and silent is False:
        logger.error("failed to get price for %s", token)

    if price is None:
        raise PriceError(f'could not fetch price for {token}')

    return price