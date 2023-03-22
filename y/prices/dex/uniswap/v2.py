
import asyncio
import logging
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

import a_sync
import brownie
from brownie import chain
from brownie.exceptions import EventLookupError
from multicall import Call

from y import convert
from y.classes.common import ERC20, ContractBase, WeiBalance
from y.constants import (RECURSION_TIMEOUT, STABLECOINS, WRAPPED_GAS_COIN,
                         log_possible_recursion_err, sushi,
                         thread_pool_executor, usdc, weth)
from y.contracts import Contract, contract_creation_block_async
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
from y.utils.events import decode_logs, get_logs_asap
from y.utils.multicall import (
    fetch_multicall, multicall_same_func_same_contract_different_inputs)
from y.utils.raw_calls import raw_call

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

Path = List[AddressOrContract]
Reserves = Tuple[int,int,int]


class UniswapPoolV2(ERC20):
    @a_sync.aka.cached_property
    async def factory(self) -> Address:
        try: return await raw_call(self.address, 'factory()', output='address', sync=False)
        except ValueError as e:
            if call_reverted(e):
                raise NotAUniswapV2Pool
            # `is not a valid ETH address` means we got some kind of response from the chain.
            # but couldn't convert to address. If it happens to be a goofy but
            # verified uni fork, maybe we can get factory this way
            okay_errors = ['is not a valid ETH address','invalid opcode','invalid jump destination']
            if any([msg in str(e) for msg in okay_errors]):
                contract = await Contract.coroutine(self.address)
                try: 
                    return await contract.factory.coroutine()
                except AttributeError:
                    raise NotAUniswapV2Pool
            else:
                raise

    @a_sync.aka.property
    async def tokens(self) -> Tuple[ERC20, ERC20]:
        return await asyncio.gather(self.__token0__(sync=False), self.__token1__(sync=False))
    
    @a_sync.aka.cached_property
    async def token0(self) -> ERC20:
        token0 = await Call(self.address, ['token0()(address)']).coroutine()
        return ERC20(token0, asynchronous=self.asynchronous)

    @a_sync.aka.cached_property
    async def token1(self) -> ERC20:
        token1 = await Call(self.address, ['token1()(address)']).coroutine()
        return ERC20(token1, asynchronous=self.asynchronous)
    
    @a_sync.a_sync(cache_type='memory')
    async def get_price(self, block: Optional[Block] = None) -> Optional[UsdPrice]:
        tvl = await self.tvl(block=block, sync=False)
        if tvl is not None:
            return UsdPrice(tvl / await self.total_supply_readable(block=block, sync=False))
        return None
    
    #yLazyLogger(logger)
    async def reserves(self, block: Optional[Block] = None) -> Tuple[WeiBalance, WeiBalance]:
        reserves, tokens = await asyncio.gather(
            Call(self.address, ['getReserves()((uint112,uint112,uint32))'], block_id=block).coroutine(),
            self.__tokens__(sync=False),
        )
        if reserves:
            return (WeiBalance(reserve, token, block=block) for reserve, token in zip(reserves, tokens))

    async def tvl(self, block: Optional[Block] = None) -> Optional[float]:
        prices, reserves = await asyncio.gather(
            asyncio.gather(*[token.price(block=block, return_None_on_failure=True, sync=False) for token in await self.__tokens__(sync=False)]),
            self.reserves(block=block, sync=False),
        )

        if reserves is None:
            return None

        vals = [
            None if price is None else await reserve.__readable__(sync=False) * price
            for reserve, price in zip(reserves, prices)
        ]
        
        if not vals[0] or not vals[1]:
            if vals[0] is not None and not vals[1]:
                vals[1] = vals[0]
            if vals[1] is not None and not vals[0]:
                vals[0] = vals[1]

        if vals[0] is not None and vals[1] is not None:
            return sum(vals)

    async def get_pool_details(self, block: Optional[Block] = None) -> Tuple[Optional[ERC20], Optional[ERC20], Optional[int], Optional[Reserves]]:
        methods = 'token0()(address)', 'token1()(address)', 'totalSupply()(uint)', 'getReserves()((uint112,uint112,uint32))'
        try:
            token0, token1, supply, reserves = await asyncio.gather(*[Call(self.address, [method], block_id=block).coroutine() for method in methods])
        except Exception as e:
            if not call_reverted(e):
                raise
            # if call reverted, let's try with brownie. Sometimes this works, not sure why
            try:
                contract = await Contract.coroutine(self.address)
                token0, token1, supply, reserves = fetch_multicall([contract,'token0'],[contract,'token1'],[contract,'totalSupply'],[contract,'getReserves'],block=block)
            except (AttributeError, ContractNotVerified, MessedUpBrownieContract):
                raise NotAUniswapV2Pool(self.address, "Are you sure this is a uni pool?")
        
        if token0:
            token0 = ERC20(token0, asynchronous=self.asynchronous)
        if token1:
            token1 = ERC20(token1, asynchronous=self.asynchronous)
        return token0, token1, supply, reserves

@a_sync.a_sync(default='async', executor=thread_pool_executor)
def _parse_pairs_from_events(logs):
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
    

async def _get_reserves_long_way(pool: Address, block: Block):
    # TODO: Figure out which abi we should use for getReserves
    try:
        pool = await Contract.coroutine(pool)
        if all(
            pool.getReserves.abi['outputs'][i]['type'] == _type 
            for i, _type in enumerate(['uint112', 'uint112', 'uint32'])
        ):
            return None
        reserves = await pool.getReserves.coroutine(block_identifier=block)
        logger.warning(f'abi for getReserves for {pool}' is {pool.getReserves.abi})
        return reserves
    except:
        logger.warning(f'must debug getReserves for {pool}')

class UniswapRouterV2(ContractBase):
    def __init__(self, router_address: AnyAddressType, *args: Any, **kwargs: Any) -> None:
        super().__init__(router_address, *args, **kwargs)

        self.label = ROUTER_TO_PROTOCOL[self.address]
        self.factory = ROUTER_TO_FACTORY[self.address]
        self.special_paths = special_paths(self.address)

        # we need the factory contract object cached in brownie so we can decode logs properly
        if not ContractBase(self.factory, asynchronous=self.asynchronous)._is_cached:
            brownie.Contract.from_abi('UniClone Factory [forced]', self.factory, UNIV2_FACTORY_ABI)
    
    def __repr__(self) -> str:
        return f"<UniswapV2Router {self.label} '{self.address}'>"

    @a_sync.a_sync(ram_cache_maxsize=500)
    async def get_price(
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
            busd = await Contract.coroutine("0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56")
            token_out = busd.address

        if str(token_in) in STABLECOINS:
            return 1
        
        try:
            amount_in = await ERC20(token_in, asynchronous=True).scale
        except NonStandardERC20:
            return None

        if token_in in [weth.address, WRAPPED_GAS_COIN] and token_out in STABLECOINS:
            path = [token_in, token_out]

        elif str(token_out) in STABLECOINS:
            try:
                path = await self.get_path_to_stables(token_in, block, sync=False)
                logger.debug('smrt')
            except CantFindSwapPath:
                pass
        
        # If we can't find a good path to stables, we might still be able to determine price from price of paired token
        if path is None and (deepest_pool:= await self.deepest_pool(token_in, block, sync=False)):
            paired_with = (await self.__pool_mapping__(sync=False))[token_in][deepest_pool]
            path = [token_in,paired_with]
            quote, out_scale = await asyncio.gather(self.get_quote(amount_in, path, block=block, sync=False), ERC20(path[-1], asynchronous=True).scale)
            if quote is not None:
                amount_out = quote[-1] / out_scale  
                fees = 0.997 ** (len(path) - 1)
                amount_out /= fees
                try:
                    for p in asyncio.as_completed([magic.get_price(paired_with, block, fail_to_None=True, sync=False)],timeout=RECURSION_TIMEOUT):
                        log_possible_recursion_err(f"Possible recursion error for {token_in} at block {block}")
                        paired_with_price = await p
                except asyncio.TimeoutError:
                    raise RecursionError(f'uniswap.v2 token: {token_in}')
                    
                #paired_with_price = magic.get_price_async(paired_with, block, fail_to_None=True)
                if paired_with_price:
                    return amount_out * paired_with_price

        # If we still don't have a workable path, try this smol brain method
        if path is None:
            path = self.smol_brain_path_selector(token_in, token_out, paired_against)
            logger.debug('smol')
        
        fees = 0.997 ** (len(path) - 1)
        logger.debug(f'router: {self.label}     path: {path}')
        quote, out_scale = await asyncio.gather(self.get_quote(amount_in, path, block=block, sync=False), ERC20(path[-1],asynchronous=True).scale)
        if quote is not None:
            amount_out = quote[-1] / out_scale
            return UsdPrice(amount_out / fees)


    @continue_on_revert
    async def get_quote(self, amount_in: int, path: Path, block: Optional[Block] = None) -> Tuple[int,int]:
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
                if not call_reverted(e) and not any(s in str(e) for s in strings):
                    raise e
        else:
            return await Call(
                self.address,
                ['getAmountsOut(uint,address[])(uint[])',amount_in,path],
                block_id=block
            ).coroutine()


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
    
    @a_sync.aka.cached_property
    async def pools(self) -> Dict[Address,Dict[Address,Address]]:
        PairCreated = ['0x0d3648bd0f6ba80134a33ba9275ac585d9d315f0ad8355cddefde31afa28d0e9']
        logger.info(f'Fetching pools for {self.label} on {Network.printable()}. If this is your first time using ypricemagic, this can take a while. Please wait patiently...')
        try:
            logs = await get_logs_asap(self.factory, PairCreated, sync=False)
            pairs, pools = await _parse_pairs_from_events(logs)
        except Exception as e:
            print(e)
            raise e
        all_pairs_len = await raw_call(self.factory,'allPairsLength()',block=chain.height,output='int', sync=False)

        if len(pairs) == all_pairs_len:
            return pools
        elif len(pairs) > all_pairs_len:
            if self.factory == "0x115934131916C8b277DD010Ee02de363c09d037c":
                for id, pair in pairs.items():
                    if id > all_pairs_len:
                        logger.debug(id, pair)
            logger.debug(f'factory: {self.factory}')
            logger.debug(f'len pairs: {len(pairs)}')
            logger.debug(f'len allPairs: {all_pairs_len}')
            # TODO debug why this scenario occurs. Likely a strange interation between asyncio and joblib, or an incorrect cache value. 
            #raise ValueError("Returning more pairs than allPairsLength, something is wrong.")
        else: # <
            logger.debug(f"Oh no! Looks like your node can't look back that far. Checking for the missing {all_pairs_len - len(pairs)} pools...")
            pools_your_node_couldnt_get = [i for i in range(all_pairs_len) if i not in pairs]
            logger.debug(f'pools: {pools_your_node_couldnt_get}')
            pools_your_node_couldnt_get = await multicall_same_func_same_contract_different_inputs(
                self.factory, 'allPairs(uint256)(address)', inputs=[i for i in pools_your_node_couldnt_get], sync=False
            )
            token0s, token1s = await asyncio.gather(
                asyncio.gather(*[Call(pool, ['token0()(address)']).coroutine() for pool in pools_your_node_couldnt_get]),
                asyncio.gather(*[Call(pool, ['token1()(address)']).coroutine() for pool in pools_your_node_couldnt_get]),
            )
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

    @a_sync.aka.cached_property
    async def pool_mapping(self) -> Dict[Address,Dict[Address,Address]]:
        pool_mapping = defaultdict(dict)
        for pool, tokens in (await self.__pools__(sync=False)).items():
            token0, token1 = tokens.values()
            pool_mapping[token0][pool] = token1
            pool_mapping[token1][pool] = token0
        logger.info(f'Loaded {len(await self.__pools__(sync=False))} pools supporting {len(pool_mapping)} tokens on {self.label}')
        return pool_mapping


    async def pools_for_token(self, token_address: Address, block: Optional[Block] = None) -> Dict[Address,Address]:
        all_pools = await self.__pool_mapping__(sync=False)
        try:
            pools = all_pools[token_address]
        except KeyError:
            return {}
        if block is not None:
            deploy_blocks = await asyncio.gather(*[contract_creation_block_async(k, True) for k in pools])
            pools = {k: v for (k, v), deploy_block in zip(pools.items(), deploy_blocks) if deploy_block <= block}
        return pools

    @a_sync.a_sync(ram_cache_maxsize=500)
    async def deepest_pool(self, token_address: AnyAddressType, block: Optional[Block] = None, _ignore_pools: Tuple[Address,...] = ()) -> Address:
        token_address = convert.to_address(token_address)
        if token_address == WRAPPED_GAS_COIN or token_address in STABLECOINS:
            return await self.deepest_stable_pool(token_address, block, sync=False)
        pools = await self.pools_for_token(token_address, block, sync=False)

        reserves = await asyncio.gather(*[Call(pool, 'getReserves()((uint112,uint112,uint32))', block_id=block).coroutine() for pool in pools], return_exceptions=True)

        # DEVELOPMENT:
        # some items in `reserves` will == None if the abi differs from the expected one.
        # I will remove this later. 
        to_fix = [(i, pool) for i, (pool, reserve) in enumerate(zip(pools, reserves)) if reserve is None]
        fixed = await asyncio.gather(*[_get_reserves_long_way(pool, block) for i, pool in to_fix])
        for (i, _), reserve in zip(to_fix, fixed):
            reserves[i] = reserve  

        deepest_pool = None
        deepest_pool_balance = 0
        for pool, reserves in zip(pools,reserves):
            if isinstance(reserves, Exception) or reserves is None or pool in _ignore_pools:
                continue
            if token_address == (await self.__pools__(sync=False))[pool]['token0']:
                reserve = reserves[0]
            elif token_address == (await self.__pools__(sync=False))[pool]['token1']:
                reserve = reserves[1]
            if reserve > deepest_pool_balance: 
                deepest_pool = pool
                deepest_pool_balance = reserve
        return deepest_pool


    @a_sync.a_sync(ram_cache_maxsize=500)
    async def deepest_stable_pool(self, token_address: AnyAddressType, block: Optional[Block] = None) -> Dict[str, str]:
        token_address = convert.to_address(token_address)
        pools = {
            pool: paired_with
            for pool, paired_with in (await self.pools_for_token(token_address, None, sync=False)).items()
            if paired_with in STABLECOINS
        }

        if block is not None:
            deploy_blocks = await asyncio.gather(*[contract_creation_block_async(pool, True) for pool in pools])
            pools = {pool: paired_with for (pool, paired_with), deploy_block in zip(pools.items(), deploy_blocks) if deploy_block <= block}
            
        reserves = await asyncio.gather(
            *[Call(pool, 'getReserves()((uint112,uint112,uint32))', block_id=block).coroutine() for pool in pools.keys()],
            return_exceptions=True
        )

        # DEVELOPMENT:
        # some items in `reserves` will == None if the abi differs from the expected one.
        # I will remove this later. 
        to_fix = [(i, pool) for i, (pool, reserve) in enumerate(zip(pools, reserves)) if reserve is None]
        fixed = await asyncio.gather(*[_get_reserves_long_way(pool, block) for i, pool in to_fix])
        for (i, _), reserve in zip(to_fix, fixed):
            reserves[i] = reserve  

        deepest_stable_pool = None
        deepest_stable_pool_balance = 0
        for pool, reserves in zip(pools, reserves):
            if isinstance(reserves, Exception) or reserves is None:
                continue
            if token_address == (await self.__pools__(sync=False))[pool]['token0']:
                reserve = reserves[0]
            elif token_address == (await self.__pools__(sync=False))[pool]['token1']:
                reserve = reserves[1]
            if reserve > deepest_stable_pool_balance:
                deepest_stable_pool = pool
                deepest_stable_pool_balance = reserve
        return deepest_stable_pool


    @a_sync.a_sync(ram_cache_maxsize=500)
    async def get_path_to_stables(self, token: AnyAddressType, block: Optional[Block] = None, _loop_count: int = 0, _ignore_pools: Tuple[Address,...] = ()) -> Path:
        if _loop_count > 10:
            raise CantFindSwapPath
        token_address = convert.to_address(token)
        path = [token_address]
        deepest_pool = await self.deepest_pool(token_address, block, _ignore_pools, sync=False)
        if deepest_pool:
            paired_with = (await self.__pool_mapping__(sync=False))[token_address][deepest_pool]
            deepest_stable_pool = await self.deepest_stable_pool(token_address, block, sync=False)
            if deepest_stable_pool and deepest_pool == deepest_stable_pool:
                last_step = (await self.__pool_mapping__(sync=False))[token_address][deepest_stable_pool]
                path.append(last_step)
                return path

            if path == [token_address]:
                try:
                    path.extend(
                        await self.get_path_to_stables(
                            paired_with,
                            block=block, 
                            _loop_count=_loop_count+1, 
                            _ignore_pools=tuple(list(_ignore_pools) + [deepest_pool]),
                            sync=False,
                        )
                    )
                except CantFindSwapPath:
                    pass

        if path == [token_address]:
            raise CantFindSwapPath(f'Unable to find swap path for {token_address} on {Network.printable()}')

        return path
