
from brownie import ZERO_ADDRESS, chain
from brownie.exceptions import ContractNotFound
from y.constants import usdc
from y.contracts import Contract
from y.exceptions import UnsupportedNetwork
from y.networks import Network
from ypricemagic.utils.raw_calls import _decimals

V1 = {
    Network.Mainnet: "0xc0a47dFe034B400B47bDaD5FecDa2621de6c4d95",
}.get(chain.id,None)

class UniswapV1:
    def __init__(self) -> None:
        self.factory = V1
    
    def get_price(self, token_address, block):
        try: factory = Contract(self.factory)
        except ValueError: raise UnsupportedNetwork
        exchange = factory.getExchange(token_address)
        if exchange == ZERO_ADDRESS: return
        try:
            exchange = Contract(exchange)
            eth_bought = exchange.getTokenToEthInputPrice(10 ** _decimals(token_address,block), block_identifier=block)
            exchange = Contract(factory.getExchange(usdc))
            usdc_bought = exchange.getEthToTokenInputPrice(eth_bought, block_identifier=block) / 1e6
            fees = 0.997 ** 2
            return usdc_bought / fees
        except (ContractNotFound):
            pass
        except ValueError as e:
            if 'invalid jump destination' in str(e): return
            else: raise
