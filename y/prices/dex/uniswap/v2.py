
import asyncio
import logging
from collections import defaultdict
from functools import cached_property, lru_cache
from typing import Any, Dict, List, Optional, Tuple

import brownie
from async_lru import alru_cache
from async_property import async_cached_property
from brownie import chain
from brownie.exceptions import EventLookupError
from cachetools.func import ttl_cache
from multicall import Call
from multicall.utils import await_awaitable, gather, raise_if_exception_in
from y import convert
from y.classes.common import ERC20, ContractBase, WeiBalance
from y.constants import STABLECOINS, WRAPPED_GAS_COIN, sushi, usdc, weth
from y.contracts import Contract
from y.datatypes import (Address, AddressOrContract, AnyAddressType, Block,
                         UsdPrice)
from y.decorators import continue_on_revert
from y.exceptions import (CantFindSwapPath, ContractNotVerified,
                          MessedUpBrownieContract, NonStandardERC20,
                          NotAUniswapV2Pool, call_reverted)
from y.interfaces.uniswap.factoryv2 import UNIV2_FACTORY_ABI
from y.networks import Network
from y.prices import magic
from y.prices.dex.uniswap.v2_forks import (ROUTER_TO_FACTORY,
                                           ROUTER_TO_PROTOCOL, special_paths)
from y.utils.aio import as_aiter
from y.utils.events import (decode_logs, get_logs_asap_async,
                            thread_pool_executor)
from y.utils.logging import yLazyLogger
from y.utils.multicall import (
    fetch_multicall, multicall_same_func_same_contract_different_inputs_async)
from y.utils.raw_calls import raw_call_async

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

Path = List[AddressOrContract]
Reserves = Tuple[int,int,int]


class UniswapPoolV2(ERC20):
    def __init__(self, address: AnyAddressType) -> None:
        super().__init__(address)
        try:
            self.decimals
        except NonStandardERC20:
            raise NotAUniswapV2Pool    

    def __repr__(self) -> str:
        try:
            return f"<UniswapPoolV2 {self.symbol} {self.address}>"  
        except RuntimeError:
            return f"<UniswapPoolV2 {self.address}>"  
    
    @cached_property
    @yLazyLogger(logger)
    def factory(self) -> Address:
        return await_awaitable(self.factory_async)
    
    @yLazyLogger(logger)
    @async_cached_property
    async def factory_async(self) -> Address:
        try: return await raw_call_async(self.address, 'factory()', output='address')
        except ValueError as e:
            if call_reverted(e):
                raise NotAUniswapV2Pool
            # `is not a valid ETH address` means we got some kind of response from the chain.
            # but couldn't convert to address. If it happens to be a goofy but
            # verified uni fork, maybe we can get factory this way
            okay_errors = ['is not a valid ETH address','invalid opcode','invalid jump destination']
            if any([msg in str(e) for msg in okay_errors]):
                try: self.factory = Contract(self.address).factory()
                except AttributeError: raise NotAUniswapV2Pool
            else: raise

    @cached_property
    @yLazyLogger(logger)
    def tokens(self) -> Tuple[ERC20, ERC20]:
        return await_awaitable(self.tokens_async)
    
    @yLazyLogger(logger)
    @async_cached_property
    async def tokens_async(self) -> Tuple[ERC20, ERC20]:
        methods = 'token0()(address)', 'token1()(address)'
        token0, token1 = await gather([Call(self.address, [method]).coroutine() for method in methods])
        return ERC20(token0), ERC20(token1)
    
    @yLazyLogger(logger)
    def token0(self) -> ERC20:
        return self.tokens[0]
    
    @yLazyLogger(logger)
    async def token0_async(self) -> ERC20:
        return await(self.tokens_async)[0]

    @yLazyLogger(logger)
    def token1(self) -> ERC20:
        return self.tokens[1]
    
    @yLazyLogger(logger)
    async def token1_async(self) -> ERC20:
        return await(self.tokens_async)[1]
    
    @yLazyLogger(logger)
    @lru_cache(maxsize=None)
    def get_price(self, block: Optional[Block] = None) -> Optional[UsdPrice]:
        return await_awaitable(self.get_price_async(block=block))
    
    @yLazyLogger(logger)
    @alru_cache(maxsize=None)
    async def get_price_async(self, block: Optional[Block] = None) -> Optional[UsdPrice]:
        tvl = await self.tvl_async(block=block)
        if tvl is not None:
            return UsdPrice(tvl / await self.total_supply_readable_async(block=block))
        return None
    
    @yLazyLogger(logger)
    def reserves(self, block: Optional[Block] = None) -> Tuple[WeiBalance, WeiBalance]:
        return await_awaitable(self.reserves_async(block=block))

    @yLazyLogger(logger)
    async def reserves_async(self, block: Optional[Block] = None) -> Tuple[WeiBalance, WeiBalance]:
        reserves, tokens = await gather([
            Call(self.address, ['getReserves()((uint112,uint112,uint32))'], block_id=block).coroutine(),
            self.tokens_async,
        ])
        if reserves:
            return (WeiBalance(reserve, token, block=block) for reserve, token in zip(reserves, tokens))

    @yLazyLogger(logger)
    def tvl(self, block: Optional[Block] = None) -> Optional[float]:
        return await_awaitable(self.tvl_async(block=block))

    @yLazyLogger(logger)
    async def tvl_async(self, block: Optional[Block] = None) -> Optional[float]:
        prices, reserves = await gather([
            asyncio.gather(
                *[
                    token.price_async(block=block, return_None_on_failure=True)
                    for token in await self.tokens_async
                ],
                return_exceptions=True,
            ),
            self.reserves_async(block=block),
        ])
        raise_if_exception_in(prices)

        if reserves is None:
            return None

        vals = [
            None if price is None else await reserve.readable_async * price
            for reserve, price in zip(reserves, prices)
        ]
        
        if not vals[0] or not vals[1]:
            if vals[0] is not None and not vals[1]:
                vals[1] = vals[0]
            if vals[1] is not None and not vals[0]:
                vals[0] = vals[1]

        if vals[0] is not None and vals[1] is not None:
            return sum(vals)

    @yLazyLogger(logger)
    def get_pool_details(self, block: Optional[Block] = None) -> Tuple[Optional[ERC20], Optional[ERC20], Optional[int], Optional[Reserves]]:
        return await_awaitable(self.get_pool_details_async(block=block))
    
    @yLazyLogger(logger)
    async def get_pool_details_async(self, block: Optional[Block] = None) -> Tuple[Optional[ERC20], Optional[ERC20], Optional[int], Optional[Reserves]]:
        methods = 'token0()(address)', 'token1()(address)', 'totalSupply()(uint)', 'getReserves()((uint112,uint112,uint32))'
        try:
            token0, token1, supply, reserves = await gather([
                Call(self.address, [method], block_id=block).coroutine()
                for method in methods
            ])
        except Exception as e:
            if not call_reverted(e):
                raise
            # if call reverted, let's try with brownie. Sometimes this works, not sure why
            try:
                contract = Contract(self.address)
                token0, token1, supply, reserves = fetch_multicall([contract,'token0'],[contract,'token1'],[contract,'totalSupply'],[contract,'getReserves'],block=block)
            except (AttributeError, ContractNotVerified, MessedUpBrownieContract):
                raise NotAUniswapV2Pool(self.address, "Are you sure this is a uni pool?")
        
        if token0:
            token0 = ERC20(token0)
        if token1:
            token1 = ERC20(token1)
        self.tokens = token0, token1
        return token0, token1, supply, reserves


def _events_subprocess(logs):
    events = decode_logs(logs)
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
        pools = {pool: tokens for pair in pairs.values() for pool, tokens in pair.items()}
    # In at least one edge case, we have trouble getting the pools the easy way.
    # They will be gathered later, the harder way. 
    except EventLookupError:
        pairs, pools = {}, {}
    return pairs, pools
    


class UniswapRouterV2(ContractBase):
    def __init__(self, router_address: AnyAddressType, *args: Any, **kwargs: Any) -> None:
        super().__init__(router_address, *args, **kwargs)

        self.label = ROUTER_TO_PROTOCOL[self.address]
        self.factory = ROUTER_TO_FACTORY[self.address]
        self.special_paths = special_paths(self.address)

        # we need the factory contract object cached in brownie so we can decode logs properly
        if not ContractBase(self.factory)._is_cached:
            brownie.Contract.from_abi('UniClone Factory [forced]', self.factory, UNIV2_FACTORY_ABI)
    

    def __repr__(self) -> str:
        return f"<UniswapV2Router {self.label} '{self.address}'>"


    @ttl_cache(ttl=36000)
    @yLazyLogger(logger)
    def get_price(
        self,
        token_in: Address,
        block: Optional[Block] = None,
        token_out: Address = usdc.address,
        paired_against: Address = WRAPPED_GAS_COIN
        ) -> Optional[UsdPrice]:
        return await_awaitable(
            self.get_price_async(token_in, block=block, token_out=token_out, paired_against=paired_against)
        )

    @yLazyLogger(logger)
    @alru_cache(maxsize=500)
    async def get_price_async(
        self,
        token_in: Address,
        block: Optional[Block] = None,
        token_out: Address = usdc.address,
        paired_against: Address = WRAPPED_GAS_COIN
        ) -> Optional[UsdPrice]:
        """
        Calculate a price based on Uniswap Router quote for selling one `token_in`.
        Always uses intermediate WETH pair if `[token_in,weth,token_out]` swap path available.
        """

        token_in, token_out, path = str(token_in), str(token_out), None

        if chain.id == Network.BinanceSmartChain and token_out == usdc.address:
            busd = Contract("0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56")
            token_out = busd.address

        try:
            amount_in = await ERC20(token_in).scale
        except NonStandardERC20:
            return None

        if str(token_in) in STABLECOINS:
            return 1

        if str(token_out) in STABLECOINS:
            try:
                path = await self.get_path_to_stables_async(token_in, block)
                logger.debug('smrt')
            except CantFindSwapPath:
                pass
        
        # If we can't find a good path to stables, we might still be able to determine price from price of paired token
        deepest_pool = await self.deepest_pool_async(token_in, block)
        if path is None and deepest_pool:
            paired_with = (await self.pool_mapping_async)[token_in][deepest_pool]
            path = [token_in,paired_with]
            quote, out_scale = await gather([
                self.get_quote_async(amount_in, path, block=block),
                ERC20(path[-1]).scale,
            ])
            if quote is not None:
                amount_out = quote[-1] / out_scale  
                fees = 0.997 ** (len(path) - 1)
                amount_out /= fees
                try:
                    for p in asyncio.as_completed([magic.get_price_async(paired_with, block, fail_to_None=True)],timeout=1):
                        paired_with_price = await p
                except asyncio.TimeoutError:
                    raise RecursionError(f'uniswap.v2 token: {token_in}')
                    
                #paired_with_price = magic.get_price_async(paired_with, block, fail_to_None=True)
                if paired_with_price:
                    return amount_out * paired_with_price

        # If we still don't have a workable path, try this smol brain method
        if path is None:
            print("runs2")
            path = self.smol_brain_path_selector(token_in, token_out, paired_against)
            logger.debug('smol')
        
        fees = 0.997 ** (len(path) - 1)
        logger.debug(f'router: {self.label}     path: {path}')
        quote, out_scale = await gather([
            self.get_quote_async(amount_in, path, block=block),
            ERC20(path[-1]).scale,
        ])
        if quote is not None:
            amount_out = quote[-1] / out_scale
            return UsdPrice(amount_out / fees)


    @continue_on_revert
    @yLazyLogger(logger)
    def get_quote(self, amount_in: int, path: Path, block: Optional[Block] = None) -> Tuple[int,int]:
        return await_awaitable(self.get_quote_async(amount_in, path, block=block))
    
    @continue_on_revert
    @yLazyLogger(logger)
    async def get_quote_async(self, amount_in: int, path: Path, block: Optional[Block] = None) -> Tuple[int,int]:
        if self._is_cached:
            try:
                return await self.contract.getAmountsOut.coroutine(amount_in, path, block_identifier=block)
            # TODO figure out how to best handle uni forks with slight modifications.
            # Sometimes the below "else" code will not work with modified methods. Brownie works for now.
            except Exception as e:
                strings = [
                    "INSUFFICIENT_INPUT_AMOUNT",
                    "INSUFFICIENT_LIQUIDITY",
                    "INSUFFICIENT_OUT_LIQUIDITY",
                    "Sequence has incorrect length",
                ]
                if any(s in str(e) for s in strings):
                    return
                raise e
        else:
            return await Call(
                self.address,
                ['getAmountsOut(uint,address[])(uint[])',amount_in,path],
                block_id=block
            ).coroutine()


    @yLazyLogger(logger)
    def smol_brain_path_selector(self, token_in: AddressOrContract, token_out: AddressOrContract, paired_against: AddressOrContract) -> Path:
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
    def pools(self) -> Dict[Address,Dict[Address,Address]]:
        return await_awaitable(self.pools_async)
    
    @async_cached_property
    async def pools_async(self) -> Dict[Address,Dict[Address,Address]]:
        PairCreated = ['0x0d3648bd0f6ba80134a33ba9275ac585d9d315f0ad8355cddefde31afa28d0e9']
        logger.info(f'Fetching pools for {self.label} on {Network.printable()}. If this is your first time using ypricemagic, this can take a while. Please wait patiently...')
        logs = await get_logs_asap_async(self.factory, PairCreated)
        pairs, pools = await asyncio.get_event_loop().run_in_executor(
            #process_pool_executor,
            thread_pool_executor,
            _events_subprocess,
            logs,
        )
        all_pairs_len = await raw_call_async(self.factory,'allPairsLength()',block=chain.height,output='int')

        if len(pairs) == all_pairs_len:
            return pools
        elif len(pairs) > all_pairs_len:
            if self.factory == "0x115934131916C8b277DD010Ee02de363c09d037c":
                for id, pair in pairs.items():
                    if id > all_pairs_len:
                        print(id, pair)
            print(f'factory: {self.factory}')
            print(f'len pairs: {len(pairs)}')
            print(f'len allPairs: {all_pairs_len}')
            # TODO debug why this scenario occurs. Likely a strange interation between asyncio and joblib, or an incorrect cache value. 
            #raise ValueError("Returning more pairs than allPairsLength, something is wrong.")
        else: # <
            logger.debug(f"Oh no! Looks like your node can't look back that far. Checking for the missing {all_pairs_len - len(pairs)} pools...")
            pools_your_node_couldnt_get = [i for i in range(all_pairs_len) if i not in pairs]
            logger.debug(f'pools: {pools_your_node_couldnt_get}')
            pools_your_node_couldnt_get = await multicall_same_func_same_contract_different_inputs_async(
                self.factory, 'allPairs(uint256)(address)', inputs=[i for i in pools_your_node_couldnt_get])
            #calls = [Call(pool, ['token0()(address)']).coroutine() for pool in pools_your_node_couldnt_get]
            #token0s = await gather(calls)
            #calls = [Call(pool, ['token1()(address)']).coroutine() for pool in pools_your_node_couldnt_get]
            #token1s = await gather(calls)
            token0s, token1s = await gather([
                gather([Call(pool, ['token0()(address)']).coroutine() for pool in pools_your_node_couldnt_get]),
                gather([Call(pool, ['token1()(address)']).coroutine() for pool in pools_your_node_couldnt_get])
            ])
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
    def pool_mapping(self) -> Dict[Address,Dict[Address,Address]]:
        return await_awaitable(self.pool_mapping_async)
    
    @async_cached_property
    async def pool_mapping_async(self) -> Dict[Address,Dict[Address,Address]]:
        pool_mapping = defaultdict(dict)
        for pool, tokens in (await self.pools_async).items():
            token0, token1 = tokens.values()
            pool_mapping[token0][pool] = token1
            pool_mapping[token1][pool] = token0
        logger.info(f'Loaded {len(await self.pools_async)} pools supporting {len(pool_mapping)} tokens on {self.label}')
        return pool_mapping


    def pools_for_token(self, token_address: Address) -> Dict[Address,Address]:
        return await_awaitable(self.pools_for_token_async(token_address))
    
    async def pools_for_token_async(self, token_address: Address) -> Dict[Address,Address]:
        try: 
            return (await self.pool_mapping_async)[token_address]
        except KeyError:
            return {}

    @yLazyLogger(logger)
    @lru_cache(maxsize=500)
    def deepest_pool(self, token_address: AnyAddressType, block: Optional[Block] = None, _ignore_pools: Tuple[Address,...] = ()) -> Address:
        return await_awaitable(
            self.deepest_pool_async(token_address, block=block, _ignore_pools=_ignore_pools)
        )

    @yLazyLogger(logger)
    @alru_cache(maxsize=500)
    async def deepest_pool_async(self, token_address: AnyAddressType, block: Optional[Block] = None, _ignore_pools: Tuple[Address,...] = ()) -> Address:
        token_address = convert.to_address(token_address)
        if token_address == WRAPPED_GAS_COIN or token_address in STABLECOINS:
            return await self.deepest_stable_pool_async(token_address)
        pools = await self.pools_for_token_async(token_address)

        reserves = await asyncio.gather(*[Call(pool, 'getReserves()((uint112,uint112,uint32))', block_id=block).coroutine() for pool in pools], return_exceptions=True)

        # DEVELOPMENT:
        # some items in `reserves` will == None if the abi differs from the expected one.
        # I will remove this later. 
        async for i, (pool, reserve) in as_aiter(enumerate(zip(pools, reserves))):
            if reserve is None or isinstance(i, Exception):
                # TODO: Figure out which abi we should use for getReserves
                try:
                    pool = Contract(pool)
                    if all(
                        pool.getReserves.abi['outputs'][i]['type'] == _type 
                        for i, _type in enumerate(['uint112', 'uint112', 'uint32'])
                    ):
                        continue
                    reserves[i] = await pool.getReserves.coroutine(block_identifier=block)
                    logger.warning(f'abi for getReserves for {pool}' is {pool.getReserves.abi})
                except:
                    logger.error(f'must debug getReserves for {pool}')

        deepest_pool = None
        deepest_pool_balance = 0
        for pool, reserves in zip(pools,reserves):
            if isinstance(reserves, Exception) or reserves is None or pool in _ignore_pools:
                continue
            if token_address == (await self.pools_async)[pool]['token0']:
                reserve = reserves[0]
            elif token_address == (await self.pools_async)[pool]['token1']:
                reserve = reserves[1]
            if reserve > deepest_pool_balance: 
                deepest_pool = pool
                deepest_pool_balance = reserve
        return deepest_pool


    @yLazyLogger(logger)
    @lru_cache(maxsize=500)
    def deepest_stable_pool(self, token_address: AnyAddressType, block: Optional[Block] = None) -> Dict[str, str]:
        return await_awaitable(self.deepest_stable_pool_async(token_address, block=block))

    @yLazyLogger(logger)
    @alru_cache(maxsize=500)
    async def deepest_stable_pool_async(self, token_address: AnyAddressType, block: Optional[Block] = None) -> Dict[str, str]:
        token_address = convert.to_address(token_address)
        pools = {
            pool: paired_with
            for pool, paired_with in (await self.pools_for_token_async(token_address)).items()
            if paired_with in STABLECOINS
        }
        reserves = await asyncio.gather(
            *[Call(pool, 'getReserves()((uint112,uint112,uint32))', block_id=block).coroutine() for pool in pools.keys()],
            return_exceptions=True
        )

        # DEVELOPMENT:
        # some items in `reserves` will == None if the abi differs from the expected one.
        # I will remove this later. 
        async for i, (pool, reserve) in as_aiter(enumerate(zip(pools, reserves))):
            if reserve is None or isinstance(i, Exception):
                # TODO: Figure out which abi we should use for getReserves
                try:
                    pool = Contract(pool)
                    if all(
                        pool.getReserves.abi['outputs'][i]['type'] == _type 
                        for i, _type in enumerate(['uint112', 'uint112', 'uint32'])
                    ):
                        continue
                    reserves[i] = await pool.getReserves.coroutine(block_identifier=block)
                    logger.warning(f'abi for getReserves for {pool}' is {pool.getReserves.abi})
                except:
                    logger.error(f'must debug getReserves for {pool}')

        deepest_stable_pool = None
        deepest_stable_pool_balance = 0
        for pool, reserves in zip(pools, reserves):
            if isinstance(reserves, Exception) or reserves is None:
                continue
            if token_address == (await self.pools_async)[pool]['token0']:
                reserve = reserves[0]
            elif token_address == (await self.pools_async)[pool]['token1']:
                reserve = reserves[1]
            if reserve > deepest_stable_pool_balance:
                deepest_stable_pool = pool
                deepest_stable_pool_balance = reserve
        return deepest_stable_pool


    @yLazyLogger(logger)
    @lru_cache(maxsize=500)
    def get_path_to_stables(self, token: AnyAddressType, block: Optional[Block] = None, _loop_count: int = 0, _ignore_pools: Tuple[Address,...] = ()) -> Path:
        return await_awaitable(
            self.get_path_to_stables_async(token, block=block, _loop_count=_loop_count, _ignore_pools=_ignore_pools)
        )
    
    @yLazyLogger(logger)
    @alru_cache(maxsize=500)
    async def get_path_to_stables_async(self, token: AnyAddressType, block: Optional[Block] = None, _loop_count: int = 0, _ignore_pools: Tuple[Address,...] = ()) -> Path:
        if _loop_count > 10:
            raise CantFindSwapPath
        token_address = convert.to_address(token)
        path = [token_address]
        deepest_pool = await self.deepest_pool_async(token_address, block, _ignore_pools)
        if deepest_pool:
            paired_with = (await self.pool_mapping_async)[token_address][deepest_pool]
            deepest_stable_pool = await self.deepest_stable_pool_async(token_address, block)
            if deepest_stable_pool and deepest_pool == deepest_stable_pool:
                last_step = (await self.pool_mapping_async)[token_address][deepest_stable_pool]
                path.append(last_step)
                return path

            if path == [token_address]:
                try:
                    path.extend(
                        await self.get_path_to_stables_async(
                            paired_with,
                            block=block, 
                            _loop_count=_loop_count+1, 
                            _ignore_pools=tuple(list(_ignore_pools) + [deepest_pool])
                        )
                    )
                except CantFindSwapPath:
                    pass

        if path == [token_address]:
            raise CantFindSwapPath(f'Unable to find swap path for {token_address} on {Network.printable()}')

        return path
