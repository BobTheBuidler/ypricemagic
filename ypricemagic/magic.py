import logging

from .utils.cache import memory
from brownie import chain
from . import aave, chainlink, compound, constants, uniswap

logger = logging.getLogger(__name__)


class PriceError(Exception):
    pass


@memory.cache()
def get_price(token, block=None):
    token = str(token)
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
        from . import balancer, cream, curve, piedao, tokensets, yearn

        if token == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE":
            token = str(constants.weth)

        # we can exit early with known tokens
        if token in chainlink.feeds:
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

        elif balancer.is_balancer_pool(token):
            price = balancer.get_price(token, block=block)
            logger.debug("balancer pool -> %s", price)

        elif tokensets.is_token_set(token):
            price = tokensets.get_price(token, block=block)
            logger.debug("token set -> %s", price)

        elif piedao.is_pie(token):
            price = piedao.get_price(token, block=block)
            logger.debug("piedeo -> %s", price)

        
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
        # NOTE let's improve before we use
        #if price is None and (not block or block >= 11153725): # NOTE: First block of curve registry
        #    price = curve.get_token_price(token, block=block)
        #    logger.debug("curve -> %s", price)

        if price is None:
            price = balancer.get_price(token, block=block)
            logger.debug("balancer -> %s", price)

        if price is None:
            logger.error("failed to get price for %s", token)

        if price is None:
            raise PriceError(f'could not fetch price for {token}')

    if chain.id == 56: # binance smart chain

        if token == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE":
            token = str(constants.wbnb)

        # we can exit early with known tokens
        if token in chainlink.feeds:
            price = chainlink.get_price(token, block=block)
            logger.debug("chainlink -> %s", price)

        elif compound.is_compound_market(token):
            price = compound.get_price(token, block=block)
            logger.debug("compound -> %s", price)

        elif uniswap.is_uniswap_pool(token):
            price = uniswap.lp_price(token, block=block)
            logger.debug("uniswap pool -> %s", price)

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

    if chain.id == 137: # polygon

        if token == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE":
            token = str(constants.wmatic)

        # we can exit early with known tokens
        if aave.is_atoken(token):
            price = aave.get_price(token, block=block)
            logger.debug("atoken -> %s", price)

        if compound.is_compound_market(token):
            price = compound.get_price(token, block=block)
            logger.debug("compound -> %s", price)

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

    return price
