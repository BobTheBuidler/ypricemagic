import asyncio
import math
from functools import lru_cache
from itertools import cycle
from typing import Optional

from async_lru import alru_cache
from brownie import chain
from eth_abi.packed import encode_abi_packed
from multicall.utils import await_awaitable
from y.classes.common import ERC20
from y.classes.singleton import Singleton
from y.constants import usdc, weth
from y.contracts import Contract, contract_creation_block
from y.datatypes import Address, Block, UsdPrice
from y.exceptions import UnsupportedNetwork
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
}

FEE_DENOMINATOR = 1_000_000


class UniswapV3(metaclass=Singleton):
    def __init__(self) -> None:
        if chain.id not in addresses:
            raise UnsupportedNetwork('compound is not supported on this network')

        conf = addresses[chain.id]
        self.factory = Contract(conf['factory'])
        self.quoter = Contract(conf['quoter'])
        self.fee_tiers = conf['fee_tiers']

    def __contains__(self, asset) -> bool:
        return chain.id in addresses

    def encode_path(self, path) -> bytes:
        types = [type for _, type in zip(path, cycle(['address', 'uint24']))]
        return encode_abi_packed(types, path)

    def undo_fees(self, path) -> float:
        fees = [1 - fee / FEE_DENOMINATOR for fee in path if isinstance(fee, int)]
        return math.prod(fees)

    @lru_cache(maxsize=None)
    def get_price(self, token: Address, block: Optional[Block] = None) -> Optional[UsdPrice]:
        return await_awaitable(self.get_price_async(token, block=block))
    
    @alru_cache(maxsize=None)
    async def get_price_async(self, token: Address, block: Optional[Block] = None) -> Optional[UsdPrice]:
        if block and block < contract_creation_block(UNISWAP_V3_QUOTER):
            return None

        paths = []
        if token != weth:
            paths += [
                [token, fee, weth.address, self.fee_tiers[0], usdc.address] for fee in self.fee_tiers
            ]

        paths += [[token, fee, usdc.address] for fee in self.fee_tiers]

        amount_in = await ERC20(token).scale

        # TODO make this async after extending brownie ContractTx
        results = fetch_multicall(
            *[
                [self.quoter, 'quoteExactInput', self.encode_path(path), amount_in]
                for path in paths
            ],
            block=block,
        )

        # TODO async version
        #results = await gather(
        #    *[
        #        self.quoter.quoteExactInput.coroutine(self.encode_path(path), amount_in, block_identifier=block)
        #        for path in paths
        #    ],
        #    return_exceptions=True
        #)

        outputs = [
            amount / self.undo_fees(path) / 1e6
            for amount, path in zip(results, paths)
            if amount
        ]
        return UsdPrice(max(outputs)) if outputs else None


uniswap_v3 = None
try:
    uniswap_v3 = UniswapV3()
except UnsupportedNetwork:
    pass
