
from brownie import chain
from brownie.exceptions import ContractNotFound
from ypricemagic.constants import usdc
from ypricemagic.exceptions import UnsupportedNetwork
from ypricemagic.networks import Network
from ypricemagic.utils.contracts import Contract
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
        try:
            exchange = Contract(factory.getExchange(token_address))
            eth_bought = exchange.getTokenToEthInputPrice(10 ** _decimals(token_address,block), block_identifier=block)
            exchange = Contract(factory.getExchange(usdc))
            usdc_bought = exchange.getEthToTokenInputPrice(eth_bought, block_identifier=block) / 1e6
            fees = 0.997 ** 2
            return usdc_bought / fees
        except (ContractNotFound):
            pass
