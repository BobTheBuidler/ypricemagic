import logging
from typing import Union

from brownie import chain, convert, multicall
from eth_typing.evm import Address, BlockNumber

from ypricemagic import _symbol
from ypricemagic.constants import STABLECOINS, WRAPPED_GAS_COIN
from ypricemagic.exceptions import PriceError
from ypricemagic.networks import Network
from ypricemagic.price_modules import (aave, belt, compound, cream, ellipsis,
                                       froyo, gelato, ib, mooniswap,
                                       mstablefeederpool, piedao, tokensets,
                                       wsteth, yearn)
from ypricemagic.price_modules.balancer.balancer import balancer
from ypricemagic.price_modules.chainlink import chainlink
from ypricemagic.price_modules.curve import curve
from ypricemagic.price_modules.uniswap.v2 import uniswap
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

    price = _exit_early_for_known_tokens(token, block=block)
    if price: return price
    
    # a few more attempts to fetch a price a token
    if chain.id == Network.Mainnet: # eth mainnet
        multicall(address='0x5BA1e12693Dc8F9c48aAD8770482f4739bEeD696')

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

    if chain.id == Network.BinanceSmartChain:

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

    if chain.id == Network.Polygon:

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

    if chain.id == Network.Fantom:
        
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

    # let's try a few more things
    if price is None:
        price = balancer.get_price(token, block=block)
        logger.debug("balancer -> %s", price)

    if price is None and silent is False:
        logger.error("failed to get price for %s", token)

    if price is None:
        raise PriceError(f'could not fetch price for {token}')

    return price


def _exit_early_for_known_tokens(token_address: str, block=None):

    bucket = _check_bucket(token_address)

    price = None

    if bucket == 'atoken':                  price = aave.get_price(token_address, block=block)
    elif bucket == 'balancer pool':         price = balancer.get_price(token_address, block)
    elif bucket == 'belt lp':               price = belt.get_price(token_address, block)

    elif bucket == 'chainlink feed':        price = chainlink.chainlink.get_price(token_address, block)
    elif bucket == 'compound':              price = compound.get_price(token_address, block=block)
    elif bucket == 'creth':                 price = cream.get_price_creth(token_address, block)

    elif bucket == 'curve lp token':        price = curve.get_price(token_address, block)
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

    return price if price else None


@memory.cache()
def _check_bucket(token_address: str):

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

            

    

    
    

    
    


    
    
    

    
    

    
            
            
            
            
            
            
            
        
    
    
        
