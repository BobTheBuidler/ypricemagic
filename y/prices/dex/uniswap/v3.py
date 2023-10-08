import asyncio
import math
from functools import cached_property
from itertools import cycle
from typing import AsyncIterator, List, Optional, Tuple

import a_sync
from brownie import chain
from brownie.network.event import _EventItem
from eth_abi.packed import encode_abi_packed

from y import ENVIRONMENT_VARIABLES as ENVS
from y.classes.common import ERC20, ContractBase
from y.constants import usdc, weth
from y.contracts import Contract, contract_creation_block_async
from y.datatypes import Address, AnyAddressType, Block, Pool, UsdPrice
from y.exceptions import ContractNotVerified, TokenNotFound, UnsupportedNetwork
from y.interfaces.uniswap.quoterv3 import UNIV3_QUOTER_ABI
from y.networks import Network
from y.utils.events import ProcessedEvents
from y.utils.multicall import fetch_multicall

# https://github.com/Uniswap/uniswap-v3-periphery/blob/main/deploys.md
UNISWAP_V3_FACTORY = '0x1F98431c8aD98523631AE4a59f267346ea31F984'
UNISWAP_V3_QUOTER = '0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6'

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
        asynchronous: bool = True
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
            raise TokenNotFound(f"{token} is not in {self}")
        return ERC20(token, asynchronous=self.asynchronous)

    async def check_liquidity(self, token: AnyAddressType, block: Block) -> Optional[int]:
        if block < await self.deploy_block(sync=False):
            return 0
        return await self[token].balance_of(self.address, block, sync=False)


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

    @a_sync.aka.property
    async def factory(self) -> Contract:
        return await Contract.coroutine(addresses[chain.id]['factory'])
    
    @cached_property
    def loaded(self) -> a_sync.Event:
        return a_sync.Event(name="uniswap v3")
    
    @a_sync.aka.cached_property
    async def quoter(self) -> Contract:
        quoter = addresses[chain.id]['quoter']
        try:
            return await Contract.coroutine(quoter)
        except ContractNotVerified:
            return Contract.from_abi("Quoter", quoter, UNIV3_QUOTER_ABI)
    
    @a_sync.a_sync(cache_type='memory', ram_cache_ttl=ENVS.CACHE_TTL)
    async def get_price(
        self, 
        token: Address, 
        block: Optional[Block] = None,
        ignore_pools: Tuple[Pool, ...] = (),
        ) -> Optional[UsdPrice]:

        quoter = await self.__quoter__(sync=False)
        if block and block < await contract_creation_block_async(quoter, True):
            return None

        paths = [[token, fee, usdc.address] for fee in self.fee_tiers]
        if token != weth:
            paths += [
                [token, fee, weth.address, self.fee_tiers[0], usdc.address] for fee in self.fee_tiers
            ]

        amount_in = await ERC20(token, asynchronous=True).scale

        # TODO make this properly async after extending for brownie ContractTx
        results = await fetch_multicall(
            *[[quoter, 'quoteExactInput', self._encode_path(path), amount_in] for path in paths],
            block=block,
            sync=False
        )

        # Quoter v2 uses this weird return struct, we must unpack it to get amount out.
        outputs = [
            (amount if isinstance(amount, int) else amount[0]) / self._undo_fees(path) / 1e6
            for amount, path in zip(results, paths)
            if amount
        ]
        return UsdPrice(max(outputs)) if outputs else None

    @a_sync.aka.cached_property
    async def pools(self) -> List[UniswapV3Pool]:
        factory = await self.__factory__(sync=False)
        return UniV3Pools(factory, asynchronous=self.asynchronous)

    @a_sync.a_sync(ram_cache_maxsize=10_000, ram_cache_ttl=10*60)
    async def check_liquidity(self, token: Address, block: Block, ignore_pools: Tuple[Pool, ...] = ()) -> int:
        if block < await contract_creation_block_async(await self.__quoter__(sync=False)):
            return 0
        tasks = []
        async for pool in self._pools_for_token(token, block):
            if pool not in ignore_pools:
                tasks.append(pool.check_liquidity(token, block, sync=False))
        return max(await asyncio.gather(*tasks)) if tasks else 0

    async def _pools_for_token(self, token: Address, block: Block) -> AsyncIterator[UniswapV3Pool]:
        pools = await self.__pools__(sync=False)
        async for pool in pools.objects(to_block=block):
            if token in pool:
                yield pool

    def _encode_path(self, path) -> bytes:
        types = [type for _, type in zip(path, cycle(['address', 'uint24']))]
        return encode_abi_packed(types, path)

    def _undo_fees(self, path) -> float:
        fees = [1 - fee / FEE_DENOMINATOR for fee in path if isinstance(fee, int)]
        return math.prod(fees)


class UniV3Pools(ProcessedEvents[UniswapV3Pool]):
    __slots__ = "asynchronous", 
    def __init__(self, factory: Contract, asynchronous: bool = False):
        self.asynchronous = asynchronous
        super().__init__(addresses=[factory.address], topics=[factory.topics["PoolCreated"]], fetch_interval=60)
    def __repr__(self) -> str:
        return object.__repr__(self)
    def _include_event(self, event: _EventItem):
        return True
    def _process_event(self, event: _EventItem) -> UniswapV3Pool:
        token0, token1, fee, tick_spacing, pool = event.values()
        return UniswapV3Pool(pool, token0, token1, fee, tick_spacing, event.block_number, asynchronous=self.asynchronous)
    def _get_block_for_obj(self, obj: UniswapV3Pool) -> int:
        return obj._deploy_block


try:
    uniswap_v3 = UniswapV3(asynchronous=True)
except UnsupportedNetwork:
    uniswap_v3 = None
