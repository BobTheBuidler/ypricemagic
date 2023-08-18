import asyncio
import math
from itertools import cycle
from typing import List, Optional

import a_sync
from async_lru import alru_cache
from brownie import chain
from eth_abi.packed import encode_abi_packed

from y import ENVIRONMENT_VARIABLES as ENVS
from y.classes.common import ERC20
from y.constants import usdc, weth
from y.contracts import Contract, contract_creation_block_async
from y.datatypes import Address, Block, UsdPrice
from y.exceptions import ContractNotVerified, UnsupportedNetwork
from y.interfaces.uniswap.quoterv3 import UNIV3_QUOTER_ABI
from y.networks import Network
from y.utils.events import decode_logs, get_logs_asap_generator
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
    }
}

FEE_DENOMINATOR = 1_000_000


class UniswapV3Pool(a_sync.ASyncGenericSingleton):
    def __init__(
        self,
        address: Address,
        token0: Address, 
        token1: Address, 
        tick_spacing: int, 
        fee: int, 
        asynchronous: bool = True
    ) -> None:
        self.address = address
        self.token0 = token0
        self.token1 = token1
        self.tick_spacing = tick_spacing
        self.fee = fee
        self.asynchronous = asynchronous

    def __contains__(self, token: Address) -> bool:
        return token in [self.token0, self.token1]
    
    async def check_liquidity(self, token: Address, block: Block) -> Optional[int]:
        if token in self:
            return await ERC20(token, asynchronous=True).balance_of(self.address, block)
        

class UniswapV3(a_sync.ASyncGenericSingleton):
    def __init__(self, asynchronous: bool = True) -> None:
        self.asynchronous = asynchronous
        if chain.id not in addresses:
            raise UnsupportedNetwork('compound is not supported on this network')
        self.fee_tiers = addresses[chain.id]['fee_tiers']
        self.loading = False
        self.loaded = a_sync.Event()
        self._pools = {}

    def __contains__(self, asset) -> bool:
        return chain.id in addresses

    @a_sync.aka.property
    async def factory(self) -> Contract:
        return await Contract.coroutine(addresses[chain.id]['factory'])
    
    @a_sync.aka.cached_property
    async def quoter(self) -> Contract:
        quoter = addresses[chain.id]['quoter']
        try:
            return await Contract.coroutine(quoter)
        except ContractNotVerified:
            return Contract.from_abi("Quoter", quoter, UNIV3_QUOTER_ABI)

    def _encode_path(self, path) -> bytes:
        types = [type for _, type in zip(path, cycle(['address', 'uint24']))]
        return encode_abi_packed(types, path)

    def _undo_fees(self, path) -> float:
        fees = [1 - fee / FEE_DENOMINATOR for fee in path if isinstance(fee, int)]
        return math.prod(fees)
    
    @a_sync.a_sync(cache_type='memory', ram_cache_ttl=ENVS.CACHE_TTL)
    async def get_price(self, token: Address, block: Optional[Block] = None) -> Optional[UsdPrice]:
        if block and block < await contract_creation_block_async(UNISWAP_V3_QUOTER, True):
            return None

        paths = [[token, fee, usdc.address] for fee in self.fee_tiers]
        if token != weth:
            paths += [
                [token, fee, weth.address, self.fee_tiers[0], usdc.address] for fee in self.fee_tiers
            ]

        quoter, amount_in = await asyncio.gather(self.__quoter__(sync=False), ERC20(token, asynchronous=True).scale)

        # TODO make this properly async after extending for brownie ContractTx
        results = await fetch_multicall(
            *[
                [quoter, 'quoteExactInput', self._encode_path(path), amount_in]
                for path in paths
            ],
            block=block,
            sync=False
        )

        outputs = [
            amount / self._undo_fees(path) / 1e6
            for amount, path in zip(results, paths)
            if amount
        ]
        return UsdPrice(max(outputs)) if outputs else None

    @a_sync.aka.cached_property
    async def pools(self) -> List[UniswapV3Pool]:
        factory = await self.__factory__(sync=False)
        pools = []
        async for logs in get_logs_asap_generator(factory.address, [factory.topics["PoolCreated"]], chronological=False):
            for event in decode_logs(logs):
                token0, token1, fee, tick_spacing, pool = event
                pools.append(UniswapV3Pool(pool, token0, token1, fee, tick_spacing, asynchronous=self.asynchronous))
        return pools

    @alru_cache(maxsize=None)
    async def pools_for_token(self, token: Address) -> List[Address]:
        return [pool for pool in await self.__pools__(sync=False) if token in pool]

    @alru_cache(maxsize=10_000, ttl=10*60)
    async def check_liquidity(self, token: Address, block: Block) -> int:
        pools: List[UniswapV3Pool] = await self.pools_for_token(token, sync=False)
        return max(await asyncio.gather(*[pool.check_liquidity(token, block, sync=False) for pool in pools]))

try:
    uniswap_v3 = UniswapV3(asynchronous=True)
except UnsupportedNetwork:
    uniswap_v3 = None
