
import asyncio
import logging
from typing import Optional, Tuple

import a_sync
from brownie import ZERO_ADDRESS, chain

from y.classes.common import ERC20
from y.constants import usdc
from y.contracts import Contract, contract_creation_block_async
from y.datatypes import Address, Block, Pool, UsdPrice
from y.decorators import stuck_coro_debugger
from y.exceptions import UnsupportedNetwork, continue_if_call_reverted
from y.networks import Network
from y.utils.raw_calls import _decimals

logger = logging.getLogger(__name__)

class UniswapV1(a_sync.ASyncGenericBase):
    factory = "0xc0a47dFe034B400B47bDaD5FecDa2621de6c4d95"

    def __init__(self, asynchronous: bool = False) -> None:
        if chain.id != Network.Mainnet:
            raise UnsupportedNetwork(f"UniswapV1 does not suppport chainid {chain.id}")
        self.asynchronous = asynchronous
        
    @a_sync.a_sync(ram_cache_maxsize=None)
    @stuck_coro_debugger
    async def get_exchange(self, token_address: Address) -> Optional[Contract]:
        factory = await Contract.coroutine(self.factory)
        exchange = await factory.getExchange.coroutine(token_address)
        if exchange != ZERO_ADDRESS:
            return await Contract.coroutine(exchange)

    @stuck_coro_debugger
    async def get_price(
        self, 
        token_address: Address, 
        block: Optional[Block],
        ignore_pools: Tuple[Pool, ...] = (),
        ) -> Optional[UsdPrice]:
        exchange, usdc_exchange, decimals = await asyncio.gather(
            self.get_exchange(token_address, sync=False),
            self.get_exchange(usdc, sync=False),
            _decimals(token_address, block, sync=False),
        )
        if exchange is None:
            return None
        
        try:
            eth_bought = await exchange.getTokenToEthInputPrice.coroutine(10 ** decimals, block_identifier=block)
            usdc_bought = await usdc_exchange.getEthToTokenInputPrice.coroutine(eth_bought, block_identifier=block) / 1e6
            fees = 0.997 ** 2
            return UsdPrice(usdc_bought / fees)
        except ValueError as e:
            if 'invalid jump destination' in str(e):
                return None
            continue_if_call_reverted(e)

    @a_sync.a_sync(ram_cache_maxsize=10_000, ram_cache_ttl=10*60)
    @stuck_coro_debugger
    async def check_liquidity(self, token_address: Address, block: Block, ignore_pools: Tuple[Pool, ...] = ()) -> int:
        exchange = await self.get_exchange(token_address, sync=False)
        if exchange is None or exchange in ignore_pools:
            return 0
        if block < await contract_creation_block_async(exchange):
            return 0
        return await ERC20(token_address, asynchronous=True).balance_of(exchange, block)
