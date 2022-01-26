import logging
from typing import Dict

from brownie import convert
from cachetools.func import ttl_cache
from y.decorators import log
from y.exceptions import PriceError, contract_not_verified
from ypricemagic import magic
from ypricemagic.price_modules.uniswap.protocols import UNISWAPS
from ypricemagic.price_modules.uniswap.v1 import UniswapV1
from ypricemagic.price_modules.uniswap.v2.pool import (NotAUniswapV2Pool,
                                                       UniswapPoolV2)
from ypricemagic.price_modules.uniswap.v2.router import UniswapRouterV2
from ypricemagic.utils.multicall import multicall_same_func_no_input
from ypricemagic.utils.raw_calls import _decimals

logger = logging.getLogger(__name__)

# NOTE: If this is failing to pull a price for a token you need, it's likely because that token requires a special swap path.
#       Please add a viable swap path to ..protocols to fetch price data successfully.

class Uniswap:
    def __init__(self) -> None:
        self.routers = {}
        for name in UNISWAPS:
            try: self.routers[name] = UniswapRouterV2(UNISWAPS[name]['router'])
            except ValueError as e:
                if contract_not_verified(e): continue
                else: raise
        self.factories = [UNISWAPS[name]['factory'] for name in UNISWAPS]
        self.v1 = UniswapV1()

    @log(logger)
    def is_uniswap_pool(self, token_address: str) -> bool:
        try: return UniswapPoolV2(token_address).factory in self.factories
        except NotAUniswapV2Pool: return False

    @log(logger)
    def get_price_v1(self, token_address, block=None):
        return self.v1.get_price(token_address, block)
    
    @log(logger)
    @ttl_cache(ttl=600)
    def lp_price(self, token_address: str, block=None):
        """ Get Uniswap/Sushiswap LP token price. """
        pool = UniswapPoolV2(token_address)
        token0, token1, supply, reserves = pool.get_pool_details(block)
        
        price0 = self.get_price(token0, block=block)
        price1 = self.get_price(token1, block=block)
        prices = [price0,price1]
        scales = [10 ** _decimals(token,block) for token in [token0, token1]]
        supply = supply / 1e18
        try: balances = [res / scale * price for res, scale, price in zip(reserves, scales, prices)]
        except TypeError: # If can't get price via router, try to get from elsewhere
            if price0 is None:
                try: price0 = magic.get_price(token0, block)
                except PriceError: pass
            if price1 is None:
                try: price1 = magic.get_price(token1, block)
                except PriceError: pass
            prices = [price0,price1]
            balances = [None,None] # [res / scale * price for res, scale, price in zip(reserves, scales, prices)]
            if price0:
                balances[0] = reserves[0] / scales[0] * price0
            if price1:
                balances[1] = reserves[1] / scales[1] * price1
        balances = _extrapolate_balance_if_needed(balances)
        try: return sum(balances) / supply
        except TypeError as e:
            if "unsupported operand type(s) for +: 'int' and 'NoneType'" in str(e): return None
            else: raise
    
    @log(logger)
    @ttl_cache(ttl=36000)
    def get_price(self, token_in, block=None, protocol=None):
        """
        Calculate a price based on Uniswap Router quote for selling one `token_in`.
        Always finds the deepest swap path for `token_in`.
        """
        if protocol: router = self.routers[protocol]
        else: router = self.deepest_router(token_in, block)

        # if known routers do not support `token_in`
        if router is None: return None

        return router.get_price(token_in, block=block)
    

    def deepest_router(self, token_in: str, block: int = None) -> UniswapRouterV2:
        token_in = convert.to_address(token_in)
        deepest_pool_by_router = self.deepest_routers(token_in, block=block)

        deepest_router = None
        deepest_router_balance = 0
        reserves = multicall_same_func_no_input(deepest_pool_by_router.values(), 'getReserves()((uint112,uint112,uint32))', block=block)
        for router, pool, reserves in zip(deepest_pool_by_router.keys(),deepest_pool_by_router.values(),reserves):
            if reserves is None: continue
            if token_in == router.pools[pool]['token0']: reserve = reserves[0]
            elif token_in == router.pools[pool]['token1']: reserve = reserves[1]
            if reserve > deepest_router_balance: 
                deepest_router = router
                deepest_router_balance = reserve
        return deepest_router
    

    def deepest_routers(self, token_in: str, block: int = None) -> Dict[UniswapRouterV2,str]:
        deepest_routers = {router: router.deepest_pool(token_in, block) for router in self.routers.values()}
        return {router: pool for router, pool in deepest_routers.items() if pool is not None}

uniswap = Uniswap()

@log(logger)
def _extrapolate_balance_if_needed(balances):
    logger.debug('Attempting to extrapolate balance from one side of the pool to the other')
    logger.debug(f'Balances: {balances}')
    if balances[0] and not balances[1]:
        balances[1] = balances[0]
    if balances[1] and not balances[0]:
        balances[0] = balances[1]
    logger.debug(f'Extrapolated balances: {balances}')
    return balances
