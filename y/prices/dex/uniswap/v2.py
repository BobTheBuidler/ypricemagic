
import asyncio
import itertools
import logging
from contextlib import suppress
from decimal import Decimal
from typing import Any, AsyncIterator, Dict, List, Optional, Tuple

import a_sync
import brownie
from brownie import chain
from brownie.network.event import _EventItem
from eth_abi.exceptions import InsufficientDataBytes
from multicall import Call
from web3.exceptions import ContractLogicError

from y import convert
from y.classes.common import ERC20, ContractBase, WeiBalance
from y.constants import STABLECOINS, WRAPPED_GAS_COIN, sushi, usdc, weth
from y.contracts import Contract, contract_creation_block_async
from y.datatypes import (Address, AddressOrContract, AnyAddressType, Block,
                         Pool, UsdPrice)
from y.decorators import continue_on_revert, stuck_coro_debugger
from y.exceptions import (CantFindSwapPath, ContractNotVerified,
                          NonStandardERC20, NotAUniswapV2Pool, TokenNotFound,
                          call_reverted)
from y.interfaces.uniswap.factoryv2 import UNIV2_FACTORY_ABI
from y.networks import Network
from y.prices import magic
from y.prices.dex.uniswap.v2_forks import (ROUTER_TO_FACTORY,
                                           ROUTER_TO_PROTOCOL, special_paths)
from y.utils.dank_mids import dank_w3
from y.utils.events import ProcessedEvents
from y.utils.multicall import \
    multicall_same_func_same_contract_different_inputs
from y.utils.raw_calls import raw_call

logger = logging.getLogger(__name__)

Path = List[AddressOrContract]
Reserves = Tuple[int,int,int]

class UniswapV2Pool(ERC20):
    __slots__ = 'get_reserves', '_token0', '_token1', '_types_assumed'
    def __init__(
        self, 
        address: AnyAddressType, 
        token0: Optional[Address] = None, 
        token1: Optional[Address] = None, 
        deploy_block: Optional[int] = None, 
        asynchronous: bool = False,
    ):
        super().__init__(address, asynchronous=asynchronous)
        self.get_reserves = Call(self.address, 'getReserves()((uint112,uint112,uint32))')
        self._deploy_block = deploy_block
        self._token0 = token0
        self._token1 = token1
        self._types_assumed = True
        
    @a_sync.aka.cached_property
    async def factory(self) -> Address:
        try: return await raw_call(self.address, 'factory()', output='address', sync=False)
        except ValueError as e:
            if call_reverted(e):
                raise NotAUniswapV2Pool from e
            # `is not a valid ETH address` means we got some kind of response from the chain.
            # but couldn't convert to address. If it happens to be a goofy but
            # verified uni fork, maybe we can get factory this way
            okay_errors = ['is not a valid ETH address','invalid opcode','invalid jump destination']
            if any([msg in str(e) for msg in okay_errors]):
                contract = await Contract.coroutine(self.address)
                try: 
                    return await contract.factory.coroutine()
                except AttributeError as exc:
                    raise NotAUniswapV2Pool from exc
            else:
                raise

    @a_sync.aka.property
    async def tokens(self) -> Tuple[ERC20, ERC20]:
        return await asyncio.gather(self.__token0__(sync=False), self.__token1__(sync=False))
    
    @a_sync.aka.property
    async def token0(self) -> ERC20:
        if self._token0 is None:
            with suppress(ContractLogicError):
                if token0 := await Call(self.address, ['token0()(address)']).coroutine():
                    self._token0 = ERC20(token0, asynchronous=self.asynchronous)
        if self._token0 is None:
            raise NotAUniswapV2Pool(self.address)
        return self._token0

    @a_sync.aka.property
    async def token1(self) -> ERC20:
        if self._token1 is None:
            with suppress(ContractLogicError):
                if token1 := await Call(self.address, ['token1()(address)']).coroutine():
                    return ERC20(token1, asynchronous=self.asynchronous)
        if self._token1 is None:
            raise NotAUniswapV2Pool(self.address)
        return self._token1
    
    @a_sync.a_sync(cache_type='memory')
    @stuck_coro_debugger
    async def get_price(self, block: Optional[Block] = None) -> Optional[UsdPrice]:
        tvl = await self.tvl(block=block, sync=False)
        if tvl is not None:
            # TODO: move decimal conversion into total_supply_readable
            return UsdPrice(tvl / Decimal(await self.total_supply_readable(block=block, sync=False)))
        return None
    
    @stuck_coro_debugger
    async def reserves(self, block: Optional[Block] = None) -> Optional[Tuple[WeiBalance, WeiBalance]]:
        reserves, tokens = await asyncio.gather(self.get_reserves.coroutine(block_id=block), self.__tokens__(sync=False))

        if reserves is None and self._types_assumed:
            try:
                self._check_return_types()
            except AttributeError as e:
                raise NotAUniswapV2Pool(self.address) from e
            return await self.reserves(block, sync=False)
        
        if reserves is None and self._verified:
            # This shouldn't really run anymore, maybe delete
            try:
                reserves = await self.contract.getReserves.coroutine(block_identifier=block)
                types = ",".join(output["type"] for output in self.contract.getReserves.abi["outputs"])
                logger.warning(f'abi for getReserves for {self.contract} is {types}')
            except Exception as e:
                if not call_reverted(e):
                    raise e
                    
        if reserves is None:
            reserves = 0, 0

        return (WeiBalance(reserves[i], tokens[i], block=block) for i in range(2))

    @stuck_coro_debugger
    async def tvl(self, block: Optional[Block] = None) -> Optional[Decimal]:
        prices, reserves = await asyncio.gather(
            asyncio.gather(*[token.price(block=block, return_None_on_failure=True, sync=False) for token in await self.__tokens__(sync=False)]),
            self.reserves(block=block, sync=False),
        )

        if reserves is None:
            return None

        vals = [
            None if price is None else Decimal(await reserve.__readable__(sync=False)) * Decimal(price)
            for reserve, price in zip(reserves, prices)
        ]

        if vals[0] is not None and not vals[1]:
            vals[1] = vals[0]
        if vals[1] is not None and not vals[0]:
            vals[0] = vals[1]

        logger.debug('reserves: %s', reserves)
        logger.debug('prices: %s', prices)
        logger.debug('vals: %s', vals)
        if vals[0] is not None and vals[1] is not None:
            return sum(vals)
    
    @stuck_coro_debugger
    async def check_liquidity(self, token: Address, block: Block) -> int:
        if block < await self.deploy_block(sync=False):
            return 0
        try:
            if reserves := await self.reserves(block, sync=False):
                balance: WeiBalance
                for balance in reserves:
                    if token == balance.token:
                        return balance.balance
                raise TokenNotFound(f"{token} not found in {reserves}")
        except InsufficientDataBytes:
            return 0

    @stuck_coro_debugger
    async def is_uniswap_pool(self, block: Optional[Block] = None) -> bool:
        try:
            return all(await asyncio.gather(self.reserves(block, sync=False), self.total_supply(block, sync=False)))
        except (NotAUniswapV2Pool, InsufficientDataBytes):
            return False
        
    def _check_return_types(self) -> None:
        if not self._types_assumed:
            return
        try:
            reserves_types = ",".join(output["type"] for output in self.contract.getReserves.abi["outputs"])
            self._verified = True
            assert reserves_types.count(',') == 2, reserves_types
            self.get_reserves = Call(self.address, f'getReserves()(({reserves_types}))')
        except ContractNotVerified:
            self._verified = False
        self._types_assumed = False


class PoolsFromEvents(ProcessedEvents[UniswapV2Pool]):
    PairCreated = "0x0d3648bd0f6ba80134a33ba9275ac585d9d315f0ad8355cddefde31afa28d0e9"
    __slots__ = "asynchronous", "label"
    def __init__(self, factory: AnyAddressType, label: str, asynchronous: bool = False):
        self.asynchronous = asynchronous
        self.label = label
        super().__init__(addresses=[factory], topics=[[self.PairCreated]])
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} label={self.label}>"
    async def pools(self, to_block: Optional[int] = None) -> AsyncIterator[UniswapV2Pool]:
        async for pool in self._objects_thru(block=to_block):
            yield pool
    def _get_block_for_obj(self, obj: UniswapV2Pool) -> int:
        return obj._deploy_block
    def _process_event(self, event: _EventItem) -> UniswapV2Pool:
        return UniswapV2Pool(
            address=event["pair"], 
            token0=event["token0"], 
            token1=event["token1"], 
            deploy_block=event.block_number, 
            asynchronous=self.asynchronous,
        )
    

class UniswapRouterV2(ContractBase):
    def __init__(self, router_address: AnyAddressType, *args: Any, **kwargs: Any) -> None:
        super().__init__(router_address, *args, **kwargs)

        self.label = ROUTER_TO_PROTOCOL[self.address]
        self.factory = ROUTER_TO_FACTORY[self.address]
        self.special_paths = special_paths(self.address)
        self.get_amounts_out = Call(self.address, "getAmountsOut(uint,address[])(uint[])")

        # we need the factory contract object cached in brownie so we can decode logs properly
        if not ContractBase(self.factory, asynchronous=self.asynchronous)._is_cached:
            brownie.Contract.from_abi('UniClone Factory [forced]', self.factory, UNIV2_FACTORY_ABI)

        self._events = PoolsFromEvents(self.factory, self.label, asynchronous=self.asynchronous)
        
    
    def __repr__(self) -> str:
        return f"<UniswapV2Router {self.label} '{self.address}'>"

    @a_sync.a_sync(ram_cache_maxsize=500)
    @stuck_coro_debugger
    async def get_price(
        self,
        token_in: Address,
        block: Optional[Block] = None,
        token_out: Address = usdc.address,
        paired_against: Address = WRAPPED_GAS_COIN,
        ignore_pools: Tuple[Pool, ...] = (),
        ) -> Optional[UsdPrice]:
        """
        Calculate a price based on Uniswap Router quote for selling one `token_in`.
        Always uses intermediate WETH pair if `[token_in,weth,token_out]` swap path available.
        """

        token_in, token_out, path = str(token_in), str(token_out), None

        if chain.id == Network.BinanceSmartChain and token_out == usdc.address:
            busd = await Contract.coroutine("0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56")
            token_out = busd.address

        if token_in in STABLECOINS:
            return 1

        try:
            amount_in = await ERC20(token_in, asynchronous=True).scale
        except NonStandardERC20:
            return None

        if token_in in [weth.address, WRAPPED_GAS_COIN] and token_out in STABLECOINS:
            path = [token_in, token_out]

        elif str(token_out) in STABLECOINS:
            with suppress(CantFindSwapPath):
                path = await self.get_path_to_stables(token_in, block, _ignore_pools=ignore_pools, sync=False)
                logger.debug('smrt')

        # If we can't find a good path to stables, we might still be able to determine price from price of paired token
        if path is None and (deepest_pool:= await self.deepest_pool(token_in, block, _ignore_pools=ignore_pools, sync=False)):
            paired_with = (await self.get_pools_for(token_in, sync=False))[deepest_pool]
            path = [token_in, paired_with]
            quote, out_scale = await asyncio.gather(self.get_quote(amount_in, path, block=block, sync=False), ERC20(path[-1], asynchronous=True).scale)
            if quote is not None:
                amount_out = Decimal(quote[-1]) / out_scale  
                fees = 0.997 ** (len(path) - 1)
                amount_out /= fees
                paired_with_price = Decimal(await magic.get_price(paired_with, block, fail_to_None=True, ignore_pools=(*ignore_pools, deepest_pool), sync=False))

                if paired_with_price:
                    return amount_out * Decimal(paired_with_price)

        # If we still don't have a workable path, try this smol brain method
        if path is None:
            path = self._smol_brain_path_selector(token_in, token_out, paired_against)
            logger.debug('smol')

        fees = 0.997 ** (len(path) - 1)
        logger.debug('router: %s     path: %s', self.label, path)
        quote, out_scale = await asyncio.gather(self.get_quote(amount_in, path, block=block, sync=False), ERC20(path[-1],asynchronous=True).scale)
        if quote is not None:
            amount_out = quote[-1] / out_scale
            return UsdPrice(amount_out / fees)


    @continue_on_revert
    @stuck_coro_debugger
    async def get_quote(self, amount_in: int, path: Path, block: Optional[Block] = None) -> Tuple[int,int]:
        if not self._is_cached:
            return await self.get_amounts_out.coroutine((amount_in, path), block_id=block)
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
            if not call_reverted(e) and all(s not in str(e) for s in strings):
                raise e

    def _smol_brain_path_selector(self, token_in: AddressOrContract, token_out: AddressOrContract, paired_against: AddressOrContract) -> Path:
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
    async def pools(self) -> List[UniswapV2Pool]:
        logger.info('Fetching pools for %s on %s. If this is your first time using ypricemagic, this can take a while. Please wait patiently...', self.label, Network.printable())
        pools = [pool async for pool in self._events.pools(to_block=await dank_w3.eth.block_number)]
        all_pairs_len = await raw_call(self.factory, 'allPairsLength()', block=chain.height, output='int', sync=False)
        if len(pools) > all_pairs_len:
            raise NotImplementedError('this shouldnt happen again')
        elif len(pools) < all_pairs_len: # <
            to_get = all_pairs_len - len(pools)
            logger.debug("Oh no! Looks like your node can't look back that far. Checking for the missing %s pools...", to_get)
            for pool in await multicall_same_func_same_contract_different_inputs(self.factory, 'allPairs(uint256)(address)', inputs=range(to_get), sync=False):
                pools.insert(0, UniswapV2Pool(address=pool, asynchronous=self.asynchronous))
        tokens = set(await asyncio.gather(*itertools.chain(*((pool.token0, pool.token1) for pool in pools))))
        logger.info('Loaded %s pools supporting %s tokens on %s', len(pools), len(tokens), self.label)
        return pools

    @a_sync.a_sync(ram_cache_maxsize=None, ram_cache_ttl=600)
    @stuck_coro_debugger
    async def get_pools_for(self, token_in: Address) -> Dict[UniswapV2Pool, Address]:
        pool: UniswapV2Pool
        pool_to_token_out = {}
        for pool in await self.__pools__(sync=False):
            token0, token1 = await asyncio.gather(pool.__token0__(sync=False), pool.__token1__(sync=False))
            if token_in == token0:
                pool_to_token_out[pool] = token1
            elif token_in == token1:
                pool_to_token_out[pool] = token0
        return pool_to_token_out

    @stuck_coro_debugger
    async def pools_for_token(self, token_address: Address, block: Optional[Block] = None, _ignore_pools: Tuple[UniswapV2Pool,...] = ()) -> Dict[UniswapV2Pool, Address]:
        pools: Dict[UniswapV2Pool, Address]
        pools = await self.get_pools_for(token_address, sync=False)
        pools = {k: v for k, v in pools.items() if k not in _ignore_pools}
        if pools and block is not None:
            deploy_blocks = await asyncio.gather(*[pool.deploy_block(when_no_history_return_0=True, sync=False) for pool in pools])
            pools = {k: v for (k, v), deploy_block in zip(pools.items(), deploy_blocks) if deploy_block <= block}
        return pools

    @a_sync.a_sync(ram_cache_maxsize=500)
    @stuck_coro_debugger
    async def deepest_pool(self, token_address: AnyAddressType, block: Optional[Block] = None, _ignore_pools: Tuple[UniswapV2Pool,...] = ()) -> Optional[UniswapV2Pool]:
        token_address = convert.to_address(token_address)
        if token_address == WRAPPED_GAS_COIN or token_address in STABLECOINS:
            return await self.deepest_stable_pool(token_address, block, sync=False)
        pools = await self.pools_for_token(token_address, block, _ignore_pools=_ignore_pools, sync=False)
        if not pools:
            return None
        liquidity = await asyncio.gather(*[pool.check_liquidity(token_address, block, sync=False) for pool in pools])

        deepest_pool = None
        deepest_pool_balance = 0
        for pool, depth in zip(pools, liquidity):
            if depth and depth > deepest_pool_balance:
                deepest_pool = pool
                deepest_pool_balance = depth
        return deepest_pool

    @a_sync.a_sync(ram_cache_maxsize=500)
    @stuck_coro_debugger
    async def deepest_stable_pool(self, token_address: AnyAddressType, block: Optional[Block] = None, _ignore_pools: Tuple[UniswapV2Pool,...] = ()) -> Optional[UniswapV2Pool]:
        token_address = convert.to_address(token_address)
        pools: Dict[UniswapV2Pool, Address]
        pools = {
            pool: paired_with
            for pool, paired_with in (await self.pools_for_token(token_address, None, _ignore_pools=_ignore_pools, sync=False)).items()
            if paired_with in STABLECOINS
        }

        if pools and block is not None:
            deploy_blocks = await asyncio.gather(*[pool.deploy_block(when_no_history_return_0=True, sync=False) for pool in pools])
            pools = {pool: paired_with for (pool, paired_with), deploy_block in zip(pools.items(), deploy_blocks) if deploy_block <= block}
            
        if not pools:
            return None
        liquidity = await asyncio.gather(*[pool.check_liquidity(token_address, block, sync=False) for pool in pools])

        deepest_stable_pool = None
        deepest_stable_pool_balance = 0
        for pool, depth in zip(pools, liquidity):
            if depth > deepest_stable_pool_balance:
                deepest_stable_pool = pool
                deepest_stable_pool_balance = depth
        return deepest_stable_pool


    @a_sync.a_sync(ram_cache_maxsize=500)
    @stuck_coro_debugger
    async def get_path_to_stables(self, token: AnyAddressType, block: Optional[Block] = None, _loop_count: int = 0, _ignore_pools: Tuple[UniswapV2Pool,...] = ()) -> Path:
        if _loop_count > 10:
            raise CantFindSwapPath
        token_address = convert.to_address(token)
        path = [token_address]
        deepest_pool = await self.deepest_pool(token_address, block, _ignore_pools, sync=False)
        if deepest_pool:
            paired_with = (await self.get_pools_for(token_address, sync=False))[deepest_pool]
            deepest_stable_pool = await self.deepest_stable_pool(token_address, block, _ignore_pools=_ignore_pools, sync=False)
            if deepest_stable_pool and deepest_pool == deepest_stable_pool:
                last_step = (await self.get_pools_for(token_address, sync=False))[deepest_stable_pool]
                path.append(last_step)
                return path

            if path == [token_address]:
                with suppress(CantFindSwapPath):
                    path.extend(
                        await self.get_path_to_stables(
                            paired_with,
                            block=block, 
                            _loop_count=_loop_count+1, 
                            _ignore_pools=tuple(list(_ignore_pools) + [deepest_pool]),
                            sync=False,
                        )
                    )

        if path == [token_address]:
            raise CantFindSwapPath(f'Unable to find swap path for {token_address} on {Network.printable()}')

        return path

    @a_sync.a_sync(ram_cache_maxsize=10_000, ram_cache_ttl=10*60)
    @stuck_coro_debugger
    async def check_liquidity(self, token: Address, block: Block, ignore_pools = []) -> int:
        if block < await contract_creation_block_async(self.factory):
            return 0
        pools = await self.pools_for_token(token, _ignore_pools=ignore_pools, sync=False)
        return max(await asyncio.gather(*[pool.check_liquidity(token, block) for pool in pools])) if pools else 0
