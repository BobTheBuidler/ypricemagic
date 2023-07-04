import math
from itertools import cycle
from typing import Optional

import a_sync
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


class UniswapV3(a_sync.ASyncGenericSingleton):
    def __init__(self, asynchronous: bool = True) -> None:
        self.asynchronous = asynchronous
        if chain.id not in addresses:
            raise UnsupportedNetwork('compound is not supported on this network')

        #self.factory = Contract(conf['factory'])
        #try:
        #    self.quoter = Contract(conf['quoter'])
        #except ContractNotVerified:
        #    self.quoter = brownie.Contract.from_abi("Quoter", conf['quoter'], UNIV3_QUOTER_ABI)
        self.fee_tiers = addresses[chain.id]['fee_tiers']

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

        amount_in = await ERC20(token, asynchronous=True).scale

        # TODO make this async after extending for brownie ContractTx
        quoter = await self.__quoter__(sync=False)
        results = fetch_multicall(
            *[
                [quoter, 'quoteExactInput', self._encode_path(path), amount_in]
                for path in paths
            ],
            block=block,
        )

        outputs = [
            amount / self._undo_fees(path) / 1e6
            for amount, path in zip(results, paths)
            if amount
        ]
        return UsdPrice(max(outputs)) if outputs else None


uniswap_v3 = None
try:
    uniswap_v3 = UniswapV3(asynchronous=True)
except UnsupportedNetwork:
    pass
