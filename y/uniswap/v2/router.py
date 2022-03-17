

import logging
from collections import defaultdict
from functools import cached_property
from typing import Dict, List

from brownie import Contract as _Contract
from brownie import chain, convert, web3
from brownie.exceptions import EventLookupError, VirtualMachineError
from cachetools.func import ttl_cache
from multicall import Call, Multicall
from y.classes.common import ERC20, ContractBase
from y.constants import STABLECOINS, WRAPPED_GAS_COIN, sushi, usdc, weth
from y.contracts import Contract
from y.decorators import continue_on_revert, log
from y.exceptions import CantFindSwapPath, NonStandardERC20, call_reverted
from y.interfaces.uniswap.factoryv2 import UNIV2_FACTORY_ABI
from y.networks import Network
from y.prices import magic
from y.uniswap.protocols import (ROUTER_TO_FACTORY, ROUTER_TO_PROTOCOL,
                                 special_paths)
from y.utils.events import decode_logs, get_logs_asap
from y.utils.multicall import (
    multicall_same_func_no_input,
    multicall_same_func_same_contract_different_inputs)
from y.utils.raw_calls import _decimals, raw_call

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

class UniswapRouterV2(ContractBase):
    def __init__(self, router_address: str, *args, **kwargs):
        super().__init__(router_address, *args, **kwargs)

        self.label = ROUTER_TO_PROTOCOL[self.address]
        self.factory = ROUTER_TO_FACTORY[self.address]
        self.special_paths = special_paths(self.address)

        # we need the factory contract object cached in brownie so we can decode logs properly
        if not ContractBase(self.factory)._is_cached:
            _Contract.from_abi('UniClone Factory [forced]', self.factory, UNIV2_FACTORY_ABI)
    

    def __repr__(self) -> str:
        return f"<UniswapV2Router {self.label} '{self.address}'>"


    @ttl_cache(ttl=36000)
    @log(logger)
    def get_price(self, token_in: str, block: int = None, token_out: str = usdc.address, paired_against = WRAPPED_GAS_COIN):
        """
        Calculate a price based on Uniswap Router quote for selling one `token_in`.
        Always uses intermediate WETH pair if `[token_in,weth,token_out]` swap path available.
        """

        token_in, token_out, path = str(token_in), str(token_out), None

        if chain.id == Network.BinanceSmartChain and token_out == usdc.address:
            busd = Contract("0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56")
            token_out = busd.address

        try:
            amount_in = ERC20(token_in).scale
        except NonStandardERC20:
            return None

        if str(token_in) in STABLECOINS:
            return 1

        if str(token_out) in STABLECOINS:
            try:
                path = self.get_path_to_stables(token_in, block)
                logger.debug('smrt')
            except CantFindSwapPath:
                pass
        
        # If we can't find a good path to stables, we might still be able to determine price from price of paired token
        deepest_pool = self.deepest_pool(token_in, block)
        if path is None and deepest_pool:
            paired_with = self.pool_mapping[token_in][deepest_pool]
            path = [token_in,paired_with]
            quote = self.get_quote(amount_in, path, block=block)
            if quote is not None:
                amount_out = quote[-1] / ERC20(path[-1]).scale 
                fees = 0.997 ** (len(path) - 1)
                amount_out /= fees
                return amount_out * magic.get_price(paired_with, block)

        # If we still don't have a workable path, try this smol brain method
        if path is None:
            path = self.smol_brain_path_selector(token_in, token_out, paired_against)
            logger.debug('smol')
        
        fees = 0.997 ** (len(path) - 1)
        logger.debug(f'router: {self.label}     path: {path}')
        quote = self.get_quote(amount_in, path, block=block)
        if quote is not None:
            amount_out = quote[-1] / ERC20(path[-1]).scale
            return amount_out / fees


    @continue_on_revert
    @log(logger)
    def get_quote(self, amount_in: int, path: List[str], block=None):

        if self._is_cached:
            try: return self.contract.getAmountsOut.call(amount_in, path, block_identifier=block)
            # TODO figure out how to best handle uni forks with slight modifications
            except ValueError as e:
                if 'Sequence has incorrect length' in str(e):
                    return 
                #if 'is not a valid ETH address' in str(e): pass # TODO figure out why this happens and fix root cause
                raise
            except VirtualMachineError as e:
                if 'INSUFFICIENT_INPUT_AMOUNT' in str(e):
                    return
                if 'INSUFFICIENT_LIQUIDITY' in str(e):
                    return
                if 'INSUFFICIENT_OUT_LIQUIDITY' in str(e):
                    return
                raise

        else: return Call(self.address,['getAmountsOut(uint,address[])(uint[])',amount_in,path],[['amounts',None]],block_id=block)()['amounts']


    @log(logger)
    def smol_brain_path_selector(self, token_in: str, token_out: str, paired_against: str):
        '''Chooses swap path to use for quote'''
        token_in, token_out, paired_against = str(token_in), str(token_out), str(paired_against)

        if str(paired_against) in STABLECOINS and str(token_out) in STABLECOINS:            path = [token_in, paired_against]
        elif weth in (token_in, token_out):                                                 path = [token_in, token_out]
        elif sushi and paired_against == sushi and token_out != sushi:                      path = [token_in,sushi,weth,token_out]
        elif str(token_in) in self.special_paths and str(token_out) in STABLECOINS:         path = self.special_paths[str(token_in)]

        elif chain.id == Network.BinanceSmartChain:
            from y.constants import cake, wbnb
            if WRAPPED_GAS_COIN in (token_in, token_out):                                   path = [token_in, token_out]
            elif cake.address in (token_in, token_out):                                     path = [token_in, token_out]
            else:                                                                           path = [token_in,wbnb.address,token_out]
        else:
            if WRAPPED_GAS_COIN in (token_in, token_out):                                   path = [token_in, token_out]
            else:                                                                           path = [token_in, WRAPPED_GAS_COIN, token_out]

        return path
    

    @cached_property
    def pools(self) -> Dict[str,Dict[str,str]]:
        logger.info(f'Fetching pools for {self.label} on {Network.printable()}. If this is your first time using ypricemagic, this can take a while. Please wait patiently...')
        PairCreated = ['0x0d3648bd0f6ba80134a33ba9275ac585d9d315f0ad8355cddefde31afa28d0e9']
        events = decode_logs(get_logs_asap(self.factory, PairCreated))
        try:
            pairs = {
                event['']: {
                    convert.to_address(event['pair']): {
                        'token0':convert.to_address(event['token0']),
                        'token1':convert.to_address(event['token1']),
                    }
                }
                for event in events
            }
            pools = {pool: tokens for i, pair in pairs.items() for pool, tokens in pair.items()}
        except EventLookupError:
            pairs, pools = {}, {}
        
        all_pairs_len = raw_call(self.factory,'allPairsLength()',output='int')
        if len(pairs) < all_pairs_len:
            logger.debug("Oh no! Looks like your node can't look back that far. Checking for the missing pools...")
            pools_your_node_couldnt_get = [i for i in range(all_pairs_len) if i not in pairs]
            logger.debug(f'pools: {pools_your_node_couldnt_get}')
            pools_your_node_couldnt_get = multicall_same_func_same_contract_different_inputs(
                self.factory, 'allPairs(uint256)(address)', inputs=[i for i in pools_your_node_couldnt_get])
            calls = [Call(pool, ['token0()(address)'], [[pool,None]]) for pool in pools_your_node_couldnt_get]
            token0s = Multicall(calls)().values()
            calls = [Call(pool, ['token1()(address)'], [[pool,None]]) for pool in pools_your_node_couldnt_get]
            token1s = Multicall(calls)().values()
            pools_your_node_couldnt_get = {
                convert.to_address(pool): {
                    'token0':convert.to_address(token0),
                    'token1':convert.to_address(token1),
                }
                for pool, token0, token1
                in zip(pools_your_node_couldnt_get,token0s,token1s)
            }
            pools.update(pools_your_node_couldnt_get)

        return pools


    @cached_property
    def pool_mapping(self) -> Dict[str,Dict[str,str]]:
        pool_mapping = defaultdict(dict)
        for pool, tokens in self.pools.items():
            token0, token1 = tokens.values()
            pool_mapping[token0][pool] = token1
            pool_mapping[token1][pool] = token0
        logger.info(f'Loaded {len(self.pools)} pools supporting {len(pool_mapping)} tokens on {self.label}')
        return pool_mapping


    def pools_for_token(self, token_address: str) -> Dict[str,str]:
        try: 
            return self.pool_mapping[token_address]
        except KeyError:
            return {}

    @log(logger)
    def deepest_pool(self, token_address, block = None, _ignore_pools: List[str] = [] ):
        token_address = convert.to_address(token_address)
        if token_address == WRAPPED_GAS_COIN or token_address in STABLECOINS:
            return self.deepest_stable_pool(token_address)
        pools = self.pools_for_token(token_address)

        try:
            reserves = multicall_same_func_no_input(pools, 'getReserves()((uint112,uint112,uint32))', block=block, return_None_on_failure=True)
        except Exception as e:
            if call_reverted(e):
                return None
            raise

        deepest_pool = None
        deepest_pool_balance = 0
        for pool, reserves in zip(pools,reserves):
            if reserves is None or pool in _ignore_pools:
                continue
            if token_address == self.pools[pool]['token0']:
                reserve = reserves[0]
            elif token_address == self.pools[pool]['token1']:
                reserve = reserves[1]
            if reserve > deepest_pool_balance: 
                deepest_pool = pool
                deepest_pool_balance = reserve
        return deepest_pool


    @log(logger)
    def deepest_stable_pool(self, token_address: str, block: int = None) -> Dict[str, str]:
        token_address = convert.to_address(token_address)
        pools = {pool: paired_with for pool, paired_with in self.pools_for_token(token_address).items() if paired_with in STABLECOINS}
        reserves = multicall_same_func_no_input(pools.keys(), 'getReserves()((uint112,uint112,uint32))', block=block)

        deepest_stable_pool = None
        deepest_stable_pool_balance = 0
        for pool, reserves in zip(pools, reserves):
            if reserves is None:
                continue
            if token_address == self.pools[pool]['token0']: reserve = reserves[0]
            elif token_address == self.pools[pool]['token1']: reserve = reserves[1]
            if reserve > deepest_stable_pool_balance:
                deepest_stable_pool = pool
                deepest_stable_pool_balance = reserve
        return deepest_stable_pool


    @log(logger)
    def get_path_to_stables(self, token_address: str, block: int = None, _loop_count: int = 0, _ignore_pools: List[str] = [] ):
        if _loop_count > 10:
            raise CantFindSwapPath
        token_address = convert.to_address(token_address)
        path = [token_address]
        deepest_pool = self.deepest_pool(token_address, block, _ignore_pools)
        if deepest_pool:
            paired_with = self.pool_mapping[token_address][deepest_pool]
            deepest_stable_pool = self.deepest_stable_pool(token_address, block)
            if deepest_stable_pool and deepest_pool == deepest_stable_pool:
                last_step = self.pool_mapping[token_address][deepest_stable_pool]
                path.append(last_step)
                return path

            if path == [token_address]:
                try: path.extend(
                        self.get_path_to_stables(
                            paired_with,
                            block=block, 
                            _loop_count=_loop_count+1, 
                            _ignore_pools=_ignore_pools + [deepest_pool]
                        )
                    )
                except CantFindSwapPath: pass

        if path == [token_address]: raise CantFindSwapPath(f'Unable to find swap path for {token_address} on {Network.printable()}')

        return path

            

