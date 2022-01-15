from brownie import chain, convert
from y.contracts import Contract
from y.networks import Network
from ypricemagic.utils.multicall import (fetch_multicall,
                                         multicall_same_func_no_input)
from ypricemagic.utils.raw_calls import _decimals

UNITROLLERS = {
    Network.Mainnet: {
        "comp": "0x3d9819210A31b4961b30EF54bE2aeD79B9c9Cd3B",
        "cream": "0x3d5BC3c8d13dcB8bF317092d84783c2697AE9258",
        "ironbank": "0xAB1c342C7bf5Ec5F02ADEA1c2270670bCa144CbB"
    },
    Network.BinanceSmartChain: {
        "venus": "0xfD36E2c2a6789Db23113685031d7F16329158384"
    },
    Network.Polygon: {
        "easyfi": "0xcb3fA413B23b12E402Cfcd8FA120f983FB70d8E8"
    }
}.get(chain.id, {})


class Comptroller:
    def __init__(self, address, markets) -> None:
        self.address = address
        self.markets = markets

class Compound:
    def __init__(self) -> None:
        trollers = {name: address for name, address in UNITROLLERS.items()}
        response = multicall_same_func_no_input(trollers.values(), 'getAllMarkets()(address[])')
        response = [[convert.to_address(market) for market in troller_market] for troller_market in response]
        self.trollers = {name: Comptroller(troller, markets) for name, troller, markets in zip(trollers.keys(), trollers.values(), response)}

    def is_compound_market(self, token_address: str):
        if any(token_address in self.trollers[name].markets for name in self.trollers):
            return True
        # NOTE: Workaround for pools that have since been revoked
        token_contract = Contract(token_address)
        required = {"isCToken", "comptroller", "underlying"} 
        return set(token_contract.__dict__) & required == required
    
    def get_price(self, token_address: str, block=None):
        token = Contract(token_address)
        try:
            underlying, exchange_rate, decimals = fetch_multicall(
                [token, 'underlying'],
                [token, 'exchangeRateCurrent'],
                [token, 'decimals'],
                block=block
            )
            exchange_rate /= 1e18
            under_decimals = _decimals(underlying,block)
            return [exchange_rate * 10 ** (decimals - under_decimals), underlying]
        except AttributeError: # this will run for gas coin markets like cETH, crETH
            exchange_rate, decimals = fetch_multicall(
                [token, 'exchangeRateCurrent'],
                [token, 'decimals'],
                block=block
            )
            exchange_rate /= 1e18
            under_decimals = 18
            return [exchange_rate * 10 ** (decimals - under_decimals), "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"]
        '''
        # NOTE no current chains without multicall2 support, keeping for future use

        try:
            underlying = token.underlying(block_identifier = block)
            exchange_rate = token.exchangeRateStored(block_identifier = block) / 1e18
            decimals = _decimals(token_address,block)
            under_decimals = _decimals(underlying,block)
            return [exchange_rate * 10 ** (decimals - under_decimals), underlying]
        except AttributeError:
            exchange_rate = token.exchangeRateStored(block_identifier = block) / 1e18
            decimals = _decimals(token_address,block)
            under_decimals = 18
            return [exchange_rate * 10 ** (decimals - under_decimals), "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"]
        '''

compound = Compound()
