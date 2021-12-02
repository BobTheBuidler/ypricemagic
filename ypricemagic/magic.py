import logging

from eth_typing.evm import Address, BlockNumber

from .utils.cache import memory
from typing import Union
from brownie import chain, multicall, convert, Contract
from . import aave, chainlink, compound, constants, curve, mstablefeederpool, uniswap, yearn

logger = logging.getLogger(__name__)


class PriceError(Exception):
    pass


@memory.cache()
def get_price(token: Union[str,Address,Contract], block: Union[BlockNumber,int,None]=None, silent: bool=False) -> float:
    token = str(token)
    token = convert.to_address(token)
    logging.debug(f"token: {token}")
    logging.debug(f"chainid: {chain.id}")
    #    # NOTE: Special handling required for some proxy tokens
    #    if token in constants.PROXIES: # snx
    #        logger.info('Replacing proxy address with implementation address')
    #        token = constants.PROXIES[token]
    
    logger.debug("unwrapping %s", token)
    price = None

    if token in constants.STABLECOINS:
        logger.debug("stablecoin -> %s", 1)
        return 1

    if chain.id == 1: # eth mainnet
        from . import balancer, cream, gelato, mooniswap, piedao, tokensets, wsteth
        multicall(address='0x5BA1e12693Dc8F9c48aAD8770482f4739bEeD696')

        if token == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE":
            token = str(constants.weth)

        # we can exit early with known tokens
        if wsteth.is_wsteth(token):
            price = wsteth.get_price(token, block=block)
            logger.debug("wsteth -> %s", price)

        elif token in chainlink.feeds:
            price = chainlink.get_price(token, block=block)
            logger.debug("chainlink -> %s", price)

        elif aave.is_atoken(token):
            price = aave.get_price(token, block=block)
            logger.debug("atoken -> %s", price)

        elif cream.is_creth(token):
            price = cream.get_price_creth(token, block)
            logger.debug("atoken -> %s", price)

        elif yearn.is_yearn_vault(token):
            price = yearn.get_price(token, block=block)
            logger.debug("yearn -> %s", price)

        elif curve.is_curve_lp_token(token):
            price = curve.get_pool_price(token, block=block)
            logger.debug("curve lp -> %s", price)

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

        elif balancer.is_balancer_pool(token):
            price = balancer.get_price(token, block=block)
            logger.debug("balancer pool -> %s", price)

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

        # NOTE let's improve before we use
        #if price is None and (not block or block >= 11153725): # NOTE: First block of curve registry
        #    price = curve.get_token_price(token, block=block)
        #    logger.debug("curve -> %s", price)

        if price is None:
            price = balancer.get_price(token, block=block)
            logger.debug("balancer -> %s", price)

    if chain.id == 56: # binance smart chain
        from . import belt, ellipsis, ib, mooniswap

        if token == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE":
            token = str(constants.wbnb)

        # we can exit early with known tokens
        if token in chainlink.feeds:
            price = chainlink.get_price(token, block=block)
            logger.debug("chainlink -> %s", price)

        elif belt.is_belt_lp(token):
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

        elif yearn.is_yearn_vault(token):
            price = yearn.get_price(token, block=block)
            logger.debug("yearn -> %s", price)

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

        if token == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE":
            token = str(constants.wmatic)

        # we can exit early with known tokens
        if token in chainlink.feeds:
            price = chainlink.get_price(token, block=block)
            logger.debug("chainlink -> %s", price)

        elif aave.is_atoken(token):
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

        elif yearn.is_yearn_vault(token):
            price = yearn.get_price(token, block=block)
            logger.debug("yearn -> %s", price)

        elif curve.is_curve_lp_token(token):
            price = curve.get_pool_price(token, block=block)
            logger.debug("curve lp -> %s", price)

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
        from . import balancer, froyo

        if token == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE":
            token = str(constants.wftm)
        
        # we can exit early with known tokens
        if token in chainlink.feeds:
            price = chainlink.get_price(token, block=block)
            logger.debug("chainlink -> %s", price)

        elif yearn.is_yearn_vault(token):
            price = yearn.get_price(token, block=block)
            logger.debug("yearn -> %s", price)

        elif curve.is_curve_lp_token(token):
            price = curve.get_pool_price(token, block=block)
            logger.debug("curve lp -> %s", price)

        elif uniswap.is_uniswap_pool(token):
            price = uniswap.lp_price(token, block)
            logger.debug("uniswap -> %s", price)

        elif balancer.is_balancer_pool(token):
            price = balancer.get_price(token, block=block)
            logger.debug("balancer pool -> %s", price)

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

        if price is None:
            price = balancer.get_price(token, block=block)
            logger.debug("balancer -> %s", price)

    if price is None and silent is False:
        logger.error("failed to get price for %s", token)

    if price is None:
        raise PriceError(f'could not fetch price for {token}')

    return price
