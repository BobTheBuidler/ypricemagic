import logging

import ypricemagic.magic
from cachetools.func import ttl_cache
from y.constants import usdc, weth
from ypricemagic.price_modules.uniswap.protocols import (FACTORY_TO_PROTOCOL,
                                                         TRY_ORDER, UNISWAPS)
from ypricemagic.price_modules.uniswap.v1 import UniswapV1
from ypricemagic.price_modules.uniswap.v2.pool import (NotUniswapPoolV2,
                                                       UniswapPoolV2)
from ypricemagic.price_modules.uniswap.v2.router import UniswapRouterV2
from ypricemagic.utils.raw_calls import _decimals

logger = logging.getLogger(__name__)

# NOTE: If this is failing to pull a price for a token you need, it's likely because that token requires a special swap path.
#       Please add a viable swap path to ..protocols to fetch price data successfully.

class Uniswap:
    def __init__(self) -> None:
        self.routers = {name:UniswapRouterV2(UNISWAPS[name]['router']) for name in UNISWAPS}
        self.factories = [UNISWAPS[name]['factory'] for name in UNISWAPS]
        self._try_order = TRY_ORDER
        self.v1 = UniswapV1()

    def is_uniswap_pool(self, token_address: str) -> bool:
        try: return UniswapPoolV2(token_address).factory in self.factories
        except NotUniswapPoolV2: return False

    def get_price_v1(self, token_address, block=None):
        return self.v1.get_price(token_address, block)
    
    @ttl_cache(ttl=600)
    def lp_price(self, token_address: str, block=None):
        """ Get Uniswap/Sushiswap LP token price. """
        pool = UniswapPoolV2(token_address)
        token0, token1, supply, reserves = pool.get_pool_details(block)
        protocol = FACTORY_TO_PROTOCOL[pool.factory]
        #tokens = [Contract_with_erc20_fallback(token) for token in [pool_details['token0'], pool_details['token1']]]
        #price0 = self.get_price(tokens[0], paired_against=tokens[1], router=router, block=block)
        #price1 = self.get_price(tokens[1], paired_against=tokens[0], router=router, block=block)
        
        price0 = self.get_price(token0, paired_against=token1, protocol=protocol, block=block)
        price1 = self.get_price(token1, paired_against=token0, protocol=protocol, block=block)
        prices = [price0,price1]
        scales = [10 ** _decimals(token,block) for token in [token0, token1]]
        supply = supply / 1e18
        try: balances = [res / scale * price for res, scale, price in zip(reserves, scales, prices)]
        except TypeError: # If can't get price via router, try to get from elsewhere
            if not price0:
                try: price0 = ypricemagic.magic.get_price(token0, block)
                except ypricemagic.magic.PriceError: price0 is None
            if not price1:
                try: price1 = ypricemagic.magic.get_price(token1, block)
                except ypricemagic.magic.PriceError: price1 is None
            prices = [price0,price1]
            balances = [None,None] # [res / scale * price for res, scale, price in zip(reserves, scales, prices)]
            if price0:
                balances[0] = reserves[0] / scales[0] * price0
            if price1:
                balances[1] = reserves[1] / scales[1] * price1
        balances = _extrapolate_balance_if_needed(balances)
        return sum(balances) / supply
    
    @ttl_cache(ttl=36000)
    def get_price(self, token_in, token_out=usdc, protocol=None, block=None, paired_against=weth):
        """
        Calculate a price based on Uniswap Router quote for selling one `token_in`.
        Always uses intermediate WETH pair if `[token_in,weth,token_out]` swap path available.
        """
        if not protocol:
            protocol = self._try_order[0]
        try:
            return self.routers[protocol].get_price(token_in, token_out=token_out, block=block, paired_against=paired_against)
        except ValueError as e:
            if 'execution reverted' in str(e): return None
            else: raise
    
    def try_for_price(self, token_in, token_out=usdc, block=None, paired_against=weth):
        for protocol in self._try_order:
            if protocol == 'uniswap v1':
                price = self.get_price_v1(token_in, block=block)
            else:
                price = self.get_price(
                    token_in, token_out=token_out, block=block, protocol=protocol, paired_against=paired_against)
            if price:
                logger.debug(f"{protocol} -> ${price}")
                return price
        return None



uniswap = Uniswap()

def _extrapolate_balance_if_needed(balances):
    if balances[0] and not balances[1]:
        balances[1] = balances[0]
    if balances[1] and not balances[0]:
        balances[0] = balances[1]
    return balances
