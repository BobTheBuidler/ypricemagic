
import logging
from typing import Optional

from brownie import ZERO_ADDRESS, chain
from brownie.exceptions import ContractNotFound
from multicall.utils import await_awaitable
from y.constants import usdc
from y.contracts import Contract
from y.datatypes import Address, Block, UsdPrice
from y.exceptions import ContractNotVerified, UnsupportedNetwork
from y.networks import Network
from y.utils.logging import yLazyLogger
from y.utils.raw_calls import _decimals

logger = logging.getLogger(__name__)

V1 = {
    Network.Mainnet: "0xc0a47dFe034B400B47bDaD5FecDa2621de6c4d95",
}.get(chain.id,None)

class UniswapV1:
    def __init__(self) -> None:
        self.factory = V1
    
    @yLazyLogger(logger)
    def get_price(self, token_address: Address, block: Optional[Block]) -> Optional[UsdPrice]:
        return await_awaitable(self.get_price_async(token_address, block=block))

    @yLazyLogger(logger)
    async def get_price_async(self, token_address: Address, block: Optional[Block]) -> Optional[UsdPrice]:
        try:
            factory = Contract(self.factory)
        except ValueError:
            raise UnsupportedNetwork
        exchange = factory.getExchange(token_address)
        if exchange == ZERO_ADDRESS:
            return None
        try:
            exchange = Contract(exchange)
            eth_bought = exchange.getTokenToEthInputPrice(10 ** await _decimals(token_address,block), block_identifier=block)
            exchange = Contract(factory.getExchange(usdc))
            usdc_bought = exchange.getEthToTokenInputPrice(eth_bought, block_identifier=block) / 1e6
            fees = 0.997 ** 2
            return UsdPrice(usdc_bought / fees)
        except (ContractNotFound, ContractNotVerified):
            pass
        except ValueError as e:
            if 'invalid jump destination' in str(e):
                return
            else:
                raise
