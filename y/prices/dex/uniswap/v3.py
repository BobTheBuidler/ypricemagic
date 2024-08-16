import asyncio
import logging
import math
from collections import defaultdict
from functools import cached_property, lru_cache
from itertools import cycle
from typing import AsyncIterator, DefaultDict, List, Optional, Tuple

import a_sync
import eth_retry
from a_sync.a_sync import HiddenMethodDescriptor
from brownie import chain
from brownie.network.event import _EventItem
from typing_extensions import Self

from y import ENVIRONMENT_VARIABLES as ENVS
from y._decorators import stuck_coro_debugger
from y.classes.common import ERC20, ContractBase
from y.constants import usdc, weth
from y.contracts import Contract, contract_creation_block_async
from y.datatypes import Address, AnyAddressType, Block, Pool, UsdPrice
from y.exceptions import ContractNotVerified, TokenNotFound, UnsupportedNetwork, call_reverted
from y.interfaces.uniswap.quoterv3 import UNIV3_QUOTER_ABI
from y.networks import Network
from y.utils.events import ProcessedEvents

try:
    from eth_abi.packed import encode_packed
except ImportError:
    from eth_abi.packed import encode_abi_packed as encode_packed

# https://github.com/Uniswap/uniswap-v3-periphery/blob/main/deploys.md
UNISWAP_V3_FACTORY = '0x1F98431c8aD98523631AE4a59f267346ea31F984'
UNISWAP_V3_QUOTER = '0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6'

logger = logging.getLogger(__name__)

# same addresses on all networks
addresses = {
    Network.Mainnet: {
        'factory': UNISWAP_V3_FACTORY,
        'quoter': UNISWAP_V3_QUOTER,
        'fee_tiers': [3000, 500, 10_000, 100],
    },
    Network.Arbitrum: {
        'factory': UNISWAP_V3_FACTORY,
        'quoter': UNISWAP_V3_QUOTER,
        'fee_tiers': [3000, 500, 10_000],
    },
    Network.Optimism: {
        'factory': UNISWAP_V3_FACTORY,
        'quoter': UNISWAP_V3_QUOTER,
        'fee_tiers': [3000, 500, 10_000, 100],
    },
    Network.Base: {
        'factory': '0x33128a8fC17869897dcE68Ed026d694621f6FDfD',
        'quoter': '0x3d4e44Eb1374240CE5F1B871ab261CD16335B76a', # quoter v2
        'fee_tiers': [3000, 500, 10_000, 100],
    }
}

FEE_DENOMINATOR = 1_000_000


class UniswapV3Pool(ContractBase):
    __slots__ = 'fee', 'token0', 'token1', 'tick_spacing'
    def __init__(
        self,
        address: Address,
        token0: Address, 
        token1: Address, 
        tick_spacing: int, 
        fee: int, 
        deploy_block: int,
        asynchronous: bool = False
    ) -> None:
        super().__init__(address, asynchronous=asynchronous)
        self.token0 = ERC20(token0, asynchronous=asynchronous)
        self.token1 = ERC20(token1, asynchronous=asynchronous)
        self.tick_spacing = tick_spacing
        self.fee = fee
        self._deploy_block = deploy_block

    def __contains__(self, token: Address) -> bool:
        return token in [self.token0, self.token1]
    
    def __getitem__(self, token: Address) -> ERC20:
        if token not in self:
            raise TokenNotFound(token, self)
        return ERC20(token, asynchronous=self.asynchronous)

    @a_sync.a_sync(ram_cache_maxsize=100_000, ram_cache_ttl=60*60, semaphore=10000)  # lets try a semaphore here
    async def check_liquidity(self, token: AnyAddressType, block: Block) -> Optional[int]:
        logger.debug("checking %s liquidity for %s at %s", self, token, block)
        if block < await self.deploy_block(sync=False):
            logger.debug("block %s prior to %s deploy block", block, self)
            return 0
        try:
            liquidity = await self[token].balance_of(self.address, block, sync=False)
        except ContractNotVerified:
            logger.debug("%s is not verified and we cannot fetch balance the usual way. returning 0.", token)
            return 0
        logger.debug("%s liquidity for %s at %s: %s", self, token, block, liquidity)
        return liquidity
    
    @a_sync.a_sync(ram_cache_maxsize=100_000, ram_cache_ttl=60*60)
    async def _check_liquidity_token_out(self, token_in: AnyAddressType, block: Block) -> Optional[int]:
        return await self.check_liquidity(self._get_token_out(token_in), block=block, sync=False)
    
    @lru_cache
    def _get_token_out(self, token_in: ERC20) -> ERC20:
        if token_in == self.token0:
            return self.token1
        elif token_in == self.token1:
            return self.token0
        raise TokenNotFound(token_in, self)


class UniswapV3(a_sync.ASyncGenericSingleton):
    def __init__(self, asynchronous: bool = True) -> None:
        self.asynchronous = asynchronous
        if chain.id not in addresses:
            raise UnsupportedNetwork('compound is not supported on this network')
        self.fee_tiers = addresses[chain.id]['fee_tiers']
        self.loading = False
        self._pools = {}

    def __contains__(self, asset) -> bool:
        return chain.id in addresses
    
    @cached_property
    def loaded(self) -> a_sync.Event:
        return a_sync.Event(name=self)

    @a_sync.aka.property
    async def factory(self) -> Contract:
        return await Contract.coroutine(addresses[chain.id]['factory'])
    __factory__: HiddenMethodDescriptor[Self, Contract]
    
    @a_sync.aka.cached_property
    async def quoter(self) -> Contract:
        quoter = addresses[chain.id]['quoter']
        try:
            return await Contract.coroutine(quoter)
        except ContractNotVerified:
            return Contract.from_abi("Quoter", quoter, UNIV3_QUOTER_ABI)
    __quoter__: HiddenMethodDescriptor[Self, Contract]

    @a_sync.aka.cached_property
    @stuck_coro_debugger
    async def pools(self) -> List[UniswapV3Pool]:
        factory = await self.__factory__
        return UniV3Pools(factory, asynchronous=self.asynchronous)
    __pools__: HiddenMethodDescriptor[Self, "UniV3Pools"]

    async def pools_for_token(self, token: Address, block: Block) -> AsyncIterator[UniswapV3Pool]:
        pools = await self.__pools__
        async for pool in pools.objects(to_block=block):
            if token in pool:
                yield pool
    
    @stuck_coro_debugger
    @a_sync.a_sync(cache_type='memory', ram_cache_ttl=ENVS.CACHE_TTL)
    async def get_price(
        self, 
        token: Address, 
        block: Optional[Block] = None,
        ignore_pools: Tuple[Pool, ...] = (), # unused
        skip_cache: bool = ENVS.SKIP_CACHE,  # unused
        ) -> Optional[UsdPrice]:

        quoter = await self.__quoter__
        if block and block < await contract_creation_block_async(quoter, True):
            return None

        paths = [[token, fee, usdc.address] for fee in self.fee_tiers]
        if token != weth:
            paths += [
                [token, fee, weth.address, self.fee_tiers[0], usdc.address] for fee in self.fee_tiers
            ]
        logger.debug("paths: %s", paths)
        
        amount_in = await ERC20(token, asynchronous=True).scale
        results = await asyncio.gather(*(self._quote_exact_input(path, amount_in, block) for path in paths), return_exceptions=True)

        for result in results:
            if isinstance(result, Exception) and not call_reverted(result):
                raise result.with_traceback(result.__traceback__)
            
        logger.debug("results: %s", results)
        
        outputs = [
            # Quoter v2 uses this weird return struct, we must unpack it to get amount out.
            (amount if isinstance(amount, int) else amount[0]) / _undo_fees(path) / 1e6
            for amount, path in zip(results, paths)
            if amount and not call_reverted(amount)
        ]
        logger.debug("outputs: %s", outputs)
        return UsdPrice(max(outputs)) if outputs else None

    @stuck_coro_debugger
    @a_sync.a_sync(ram_cache_maxsize=100_000, ram_cache_ttl=60*60)
    async def check_liquidity(self, token: Address, block: Block, ignore_pools: Tuple[Pool, ...] = ()) -> int:
        logger.debug("checking %s liquidity for %s at %s", self, token, block)
        if chain.id == Network.Mainnet and token == "0x6DEA81C8171D0bA574754EF6F8b412F2Ed88c54D":
            # LQTY, TODO refactor this somehow
            return 0
        
        quoter = await self.__quoter__
        if block and block < await contract_creation_block_async(quoter):
            logger.debug("block %s is before %s deploy block", block, quoter)
            return 0

        if token == weth.address:
            # NOTE: we need to filter these or else we will be fetching every pool
            #       for now, we only focus on weth/usdc pools
            filter_fn = lambda pool: pool._get_token_out(token) == usdc.address and pool not in ignore_pools
        else:
            filter_fn = lambda pool: pool not in ignore_pools

        token_out_tasks = UniswapV3Pool._check_liquidity_token_out.map(token_in=token, block=block)
        pools_for_token: a_sync.ASyncIterator[UniswapV3Pool] = self.pools_for_token(token, block)
        async for pool in pools_for_token.filter(filter_fn):
            # the mapping will start the tasks internally
            logger.debug("starting token_out_task for %s", pool)
            token_out_tasks[pool]
        if not token_out_tasks:
            return 0
        logger.debug("%s token_out_tasks for %s at %s: %s", self, token, block, token_out_tasks)
        
        # Since uni v3 liquidity can be provided asymmetrically, the most liquid pool in terms of `token` might not actually be the most liquid pool in terms of `token_out`
        # We need some spaghetticode here to account for these erroneous liquidity values
        # TODO: Refactor this
        token_out_liquidity: DefaultDict[ERC20, List[int]] = defaultdict(list)
        async for pool, liquidity in token_out_tasks.map(pop=False):
            logger.debug("%s liquidity for %s at %s: %s", pool, token, block, liquidity)
            token_out_liquidity[pool._get_token_out(token)].append(liquidity)
        logger.debug("%s token_out_liquidity: %s", token, token_out_liquidity)
        
        token_out_min_liquidity = {token_out: min(liquidities) for token_out, liquidities in token_out_liquidity.items()}

        token_in_tasks = UniswapV3Pool.check_liquidity.map(token=token, block=block)
        async for pool, liquidity in token_out_tasks.map(pop=True):
            token_out = pool._get_token_out(token)
            if len(token_out_liquidity[token_out]) > 1 and liquidity == token_out_min_liquidity[token_out]:
                logger.debug("ignoring liquidity for %s", pool)
            elif token_out == weth and liquidity < 10 ** 19:  # 10 ETH
                # NOTE: this is totally arbitrary, works for all known cases but eventually will probably cause issues
                logger.debug("insufficient liquidity for %s", pool)
            else:
                token_in_tasks[pool]

        liquidity = await token_in_tasks.max(pop=True, sync=False) if token_in_tasks else 0
        logger.debug("%s liquidity for %s at %s is %s", self, token, block, liquidity)
        return liquidity
    
    @stuck_coro_debugger
    @eth_retry.auto_retry
    async def _quote_exact_input(self, path: List[list], amount_in: int, block: int) -> int:
        quoter = await self.__quoter__
        return await quoter.quoteExactInput.coroutine(_encode_path(path), amount_in, block_identifier=block)

def _encode_path(path) -> bytes:
    types = [type for _, type in zip(path, cycle(['address', 'uint24']))]
    return encode_packed(types, path)

def _undo_fees(path) -> float:
    fees = [1 - fee / FEE_DENOMINATOR for fee in path if isinstance(fee, int)]
    return math.prod(fees)


class UniV3Pools(ProcessedEvents[UniswapV3Pool]):
    __slots__ = "asynchronous", 
    def __init__(self, factory: Contract, asynchronous: bool = False):
        self.asynchronous = asynchronous
        super().__init__(addresses=[factory.address], topics=[factory.topics["PoolCreated"]])
    def _process_event(self, event: _EventItem) -> UniswapV3Pool:
        token0, token1, fee, tick_spacing, pool = event.values()
        return UniswapV3Pool(pool, token0, token1, fee, tick_spacing, event.block_number, asynchronous=self.asynchronous)
    def _get_block_for_obj(self, obj: UniswapV3Pool) -> int:
        return obj._deploy_block


try:
    uniswap_v3 = UniswapV3(asynchronous=True)
except UnsupportedNetwork:
    uniswap_v3 = None
