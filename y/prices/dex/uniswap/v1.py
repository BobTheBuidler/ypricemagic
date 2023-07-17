
import asyncio
import logging
from typing import Optional

import a_sync
from brownie import ZERO_ADDRESS, chain

from y.constants import usdc
from y.contracts import Contract
from y.datatypes import Address, Block, UsdPrice
from y.exceptions import UnsupportedNetwork, continue_if_call_reverted
from y.networks import Network
from y.utils.raw_calls import _decimals

logger = logging.getLogger(__name__)

V1 = {
    Network.Mainnet: "0xc0a47dFe034B400B47bDaD5FecDa2621de6c4d95",
}.get(chain.id,None)


class UniswapV1(a_sync.ASyncGenericBase):
    def __init__(self, asynchronous: bool = False) -> None:
        self.asynchronous = asynchronous
        super().__init__()
    
    @a_sync.aka.cached_property
    async def factory(self) -> Contract:
        if V1 is None:
            raise UnsupportedNetwork(f"UniswapV1 does not suppport chainid {chain.id}")
        return await Contract.coroutine(V1)            
        
    @a_sync.a_sync(ram_cache_maxsize=256)
    async def get_exchange(self, token_address: Address) -> Optional[Contract]:
        factory = await self.__factory__(sync=False)
        exchange = await factory.getExchange.coroutine(token_address)
        if exchange == ZERO_ADDRESS:
            return None
        return await Contract.coroutine(exchange)

    async def get_price(self, token_address: Address, block: Optional[Block]) -> Optional[UsdPrice]:
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
