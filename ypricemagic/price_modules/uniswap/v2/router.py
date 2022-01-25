

import logging
from functools import cached_property
from typing import Dict, List

from brownie import chain, convert, web3
from cachetools.func import ttl_cache
from multicall import Call
from y.constants import STABLECOINS, WRAPPED_GAS_COIN, sushi, usdc, weth
from y.contracts import Contract
from y.decorators import continue_on_revert, log
from y.exceptions import (CantFindSwapPath, ContractNotVerified,
                          NonStandardERC20)
from y.networks import Network
from ypricemagic.price_modules.uniswap.protocols import (ROUTER_TO_FACTORY,
                                                         ROUTER_TO_PROTOCOL,
                                                         special_paths)
from ypricemagic.utils.events import decode_logs, get_logs_asap
from ypricemagic.utils.multicall import multicall_same_func_no_input
from ypricemagic.utils.raw_calls import _decimals

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

class UniswapRouterV2:
    def __init__(self, router_address) -> None:
        self.address = convert.to_address(router_address)
        self.factory = ROUTER_TO_FACTORY[self.address]
        self.label = ROUTER_TO_PROTOCOL[self.address]
        self.special_paths = special_paths(self.address)
        try:
            self.contract
            self._verified = True
        except ContractNotVerified:
            self._verified = False
    
    @cached_property
    @log(logger)
    def contract(self):
        return Contract(self.address)

    @ttl_cache(ttl=36000)
    @log(logger)
    def get_price(self, token_in: str, token_out: str = usdc.address, block: int = None, paired_against: str = weth.address):
        """
        Calculate a price based on Uniswap Router quote for selling one `token_in`.
        Always uses intermediate WETH pair if `[token_in,weth,token_out]` swap path available.
        """

        token_in, token_out = str(token_in), str(token_out)

        if chain.id == Network.BinanceSmartChain and token_out == usdc:
            busd = Contract("0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56")
            token_out = busd

        try: amount_in = 10 ** _decimals(token_in,block)
        except NonStandardERC20: return None

        if str(token_in) in STABLECOINS: return 1

        if str(token_out) in STABLECOINS: path = self.get_path_to_stables(token_in, block)
        else: path = self.smol_brain_path_selector(token_in, token_out, paired_against)

        fees = 0.997 ** (len(path) - 1)
        logger.debug(f'router: {self.label}     path: {path}')
        quote = self.get_quote(amount_in, path, block=block)
        if quote is not None:
            amount_out = quote[-1] / 10 ** _decimals(str(path[-1]),block)
            return amount_out / fees

    @continue_on_revert
    @log(logger)
    def get_quote(self, amount_in: int, path: List[str], block=None):
        if self._verified:
            try: return self.contract.getAmountsOut(amount_in, path, block_identifier=block)
            # TODO figure out how to best handle uni forks with slight modifications
            except ValueError as e:
                if 'Sequence has incorrect length' in str(e): return 
                else: raise

        else: return Call(self.address,['getAmountsOut(uint,address[])(uint[])',amount_in,path],[['amounts',None]],_w3=web3,block_id=block)()['amounts']

    @log(logger)
    def smol_brain_path_selector(self, token_in, token_out, paired_against):
        '''Chooses swap path to use for quote'''

        if str(paired_against) in STABLECOINS and str(token_out) in STABLECOINS:            path = [token_in, paired_against]
        elif weth in (token_in, token_out):                                                 path = [token_in, token_out]
        elif sushi and paired_against == sushi and token_out != sushi:                      path = [token_in,sushi,weth,token_out]
        elif str(token_in) in self.special_paths and str(token_out) in STABLECOINS:         path = self.special_paths[str(token_in)]

        elif chain.id == Network.BinanceSmartChain:
            from y.constants import cake, wbnb
            if WRAPPED_GAS_COIN in (token_in, token_out):                                   path = [token_in, token_out]
            elif cake in (token_in, token_out):                                             path = [token_in, token_out]
            else:                                                                           path = [token_in,wbnb,token_out]
        else:
            if WRAPPED_GAS_COIN in (token_in, token_out):                                   path = [token_in, token_out]
            else:                                                                           path = [token_in, WRAPPED_GAS_COIN, token_out]

        return path
    
    @cached_property
    def pools(self) -> Dict[str,Dict[str,str]]:
        logger.info(f'Fetching pools for {self.label} on {Network.printable()}. If this is your first time using ypricemagic, this can take a while. Please wait patiently...')
        PairCreated = ['0x0d3648bd0f6ba80134a33ba9275ac585d9d315f0ad8355cddefde31afa28d0e9']
        events = decode_logs(get_logs_asap(self.factory, PairCreated))
        return {
            event['pair']: {
                'token0':event['token0'],
                'token1':event['token1']
            }
            for event in events
        }
        
            
    @cached_property
    def pool_mapping(self) -> Dict[str,Dict[str,str]]:
        pool_mapping = {}
        for pool, tokens in self.pools.items():
            token0, token1 = tokens['token0'], tokens['token1']

            try: pool_mapping[token0][pool] = token1
            except KeyError: pool_mapping[token0] = {pool: token1}

            try: pool_mapping[token1][pool] = token0
            except KeyError: pool_mapping[token1] = {pool: token0}

        '''
        supported_tokens = set(token for tokens in self.pools.values() for token in tokens.values())
        mapping = {token: self.map_pools_for_token(token) for token in tqdm(supported_tokens)} 
        logger.info(f'Loaded {len(supported_tokens)} tokens on {self.label}')
        '''
        logger.info(f'Loaded {len(pool_mapping)} tokens on {self.label}')
        return pool_mapping

    def map_pools_for_token(self, token: str) -> Dict[str, str]:
        pools = {pool: tokens for pool, tokens in self.pools.items() if token in tokens.values()}
        return {
            pool: token0 if token == token1 else token1
            for pool, tokens in pools.items() for token0, token1 in tokens.items()
        }
    
    @log(logger)
    def deepest_pool(self, token_address, block = None):
        token_address = convert.to_address(token_address)

        try: pools = self.pool_mapping[token_address]
        except KeyError: return None

        if token_address == WRAPPED_GAS_COIN: return self.deepest_stable_pool(token_address)
        reserves = multicall_same_func_no_input(pools.keys(), 'getReserves()((uint112,uint112,uint32))', block=block)

        deepest_pool = None
        deepest_pool_balance = 0
        for pool, reserves in zip(pools.keys(),reserves):
            if reserves is None: continue
            if token_address == self.pools[pool]['token0']: reserve = reserves[0]
            elif token_address == self.pools[pool]['token1']: reserve = reserves[1]
            if reserve > deepest_pool_balance: 
                deepest_pool = pool
                deepest_pool_balance = reserve
        return deepest_pool

    @log(logger)
    def deepest_stable_pool(self, token_address: str, block: int = None) -> Dict[str, str]:
        token_address = convert.to_address(token_address)

        try: pools = self.pool_mapping[token_address]
        except KeyError: return None

        pools = {pool: paired_with for pool, paired_with in pools.items() if paired_with in STABLECOINS}
        reserves = multicall_same_func_no_input(pools.keys(), 'getReserves()((uint112,uint112,uint32))', block=block)

        deepest_stable_pool = None
        deepest_stable_pool_balance = 0
        for pool, reserves in zip(pools.keys(), reserves):
            if reserves is None: continue
            if token_address == self.pools[pool]['token0']: reserve = reserves[0]
            elif token_address == self.pools[pool]['token1']: reserve = reserves[1]
            if reserve > deepest_stable_pool_balance:
                deepest_stable_pool = pool
                deepest_stable_pool_balance = reserve
        return deepest_stable_pool

    @log(logger)
    def get_path_to_stables(self, token_address: str, block: int = None):
        token_address = convert.to_address(token_address)
        path = None
        deepest_pool = self.deepest_pool(token_address, block)
        deepest_stable_pool = self.deepest_stable_pool(token_address, block)
        if deepest_pool and deepest_stable_pool and deepest_pool == deepest_stable_pool:
            return [token_address, self.pool_mapping[token_address][deepest_pool]]
        elif self.pool_mapping[token_address][deepest_pool] == WRAPPED_GAS_COIN:
            deepest_stable_pool_wrapped_gas = self.deepest_stable_pool(WRAPPED_GAS_COIN, block)
            return [token_address, WRAPPED_GAS_COIN, self.pool_mapping[WRAPPED_GAS_COIN][deepest_stable_pool_wrapped_gas]]
        elif self.pool_mapping[token_address][deepest_pool] == weth.address:
            deepest_stable_pool_weth = self.deepest_stable_pool(weth.address, block)
            return [token_address, weth.address, self.pool_mapping[weth.address][deepest_stable_pool_weth]]
        
        # some routers do their own thing and pair tokens against their own token
        elif chain.id == Network.BinanceSmartChain:
            from y.constants import cake
            if self.pool_mapping[token_address][deepest_pool] == cake.address:
                deepest_stable_pool_cake = self.deepest_stable_pool(cake.address, block)
                path = [token_address, cake.address, self.pool_mapping[cake.address][deepest_stable_pool_cake]]
        
        # deepest pool doesn't pair against any of the acceptable pair tokens, let's try something else
        if path is None:
            paired_with = self.pool_mapping[token_address][deepest_pool]
            path = [token_address].extend(self.get_path_to_stables(paired_with))

        if path is None: raise CantFindSwapPath(f'Unable to find swap path for {token_address} on {Network.printable()}')
        return path

            

