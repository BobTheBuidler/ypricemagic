import logging
from typing import List, Union

from brownie import chain, convert
from eth_typing.evm import Address, BlockNumber
from joblib.parallel import Parallel, delayed

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
from ypricemagic.price_modules.uniswap.uniswap import uniswap
from ypricemagic.utils.cache import memory
from ypricemagic.utils.contracts import Contract

logger = logging.getLogger(__name__)



@memory.cache()
def get_price(token_address: Union[str,Address,Contract], block: Union[BlockNumber,int,None]=None, fail_quietly:bool=False, silent:bool=False) -> float:
    token_address = convert.to_address(str(token_address))
    try: return _get_price(token_address, block=block, fail_quietly=fail_quietly, silent=silent)
    except RecursionError: raise PriceError(f'could not fetch price for {_symbol(token_address)} {token_address}')


def get_prices(token_addresses: List[Union[str,Address,Contract]], block: Union[BlockNumber,int,None]=None, silent: bool=False):
    return Parallel(4,'threading')(delayed(get_price)(token_address, block, fail_quietly=True) for token_address in token_addresses)

    
def _get_price(token: Union[str,Address,Contract], block: Union[BlockNumber,int,None]=None, fail_quietly:bool=False, silent:bool=False):
    logger.debug(f"[chain{chain.id}] token: {token}")
    logger.debug("unwrapping %s", token)

    price = _exit_early_for_known_tokens(token, block=block)
    if not price: price = uniswap.try_for_price(token, block=block)
    if not price: price = balancer.get_price(token, block=block)
    return price


def _exit_early_for_known_tokens(token_address: str, block=None):

    bucket = _check_bucket(token_address)

    price = None

    if bucket == 'atoken':                  price = aave.get_price(token_address, block=block)
    elif bucket == 'balancer pool':         price = balancer.get_price(token_address, block)
    elif bucket == 'belt lp':               price = belt.get_price(token_address, block)

    elif bucket == 'chainlink feed':        price = chainlink.chainlink.get_price(token_address, block)
    elif bucket == 'compound':              price = compound.compound.get_price(token_address, block=block)
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

            

    

    
    

    
    


    
    
    

    
    

    
            
            
            
            
            
            
            
        
    
    
        
