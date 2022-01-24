import logging

from brownie import chain, convert
from y.contracts import Contract, has_methods
from y.decorators import log
from y.networks import Network
from y.utils.logging import gh_issue_request
from ypricemagic.utils.multicall import (fetch_multicall,
                                         multicall_same_func_no_input)
from ypricemagic.utils.raw_calls import _decimals, raw_call

logger = logging.getLogger(__name__)

TROLLERS = {
    Network.Mainnet: {
        "comp":             "0x3d9819210A31b4961b30EF54bE2aeD79B9c9Cd3B",
        "cream":            "0x3d5BC3c8d13dcB8bF317092d84783c2697AE9258",
        "ironbank":         "0xAB1c342C7bf5Ec5F02ADEA1c2270670bCa144CbB",
        "inverse":          "0x4dCf7407AE5C07f8681e1659f626E114A7667339",
        "unfederalreserve": "0x3105D328c66d8d55092358cF595d54608178E9B5",
    },
    Network.BinanceSmartChain: {
        "venus":            "0xfD36E2c2a6789Db23113685031d7F16329158384",
    },
    Network.Polygon: {
        "easyfi":           "0xcb3fA413B23b12E402Cfcd8FA120f983FB70d8E8",
    },
    Network.Fantom: {
        "cream":            "0x4250A6D3BD57455d7C6821eECb6206F507576cD2",
    }
}.get(chain.id, {})


class Comptroller:
    def __init__(self, address, markets) -> None:
        self.address = address
        self.markets = markets

class Compound:
    def __init__(self) -> None:
        self.trollers = TROLLERS

        if len(self.trollers) == 0: return 

        response = multicall_same_func_no_input(self.trollers.values(), 'getAllMarkets()(address[])')
        response = [[convert.to_address(market) for market in troller_market] for troller_market in response]
        self.trollers = {
            name: Comptroller(troller, markets)
            for name, troller, markets
            in zip(self.trollers.keys(), self.trollers.values(), response)
        }

    @log(logger)
    def is_compound_market(self, token_address: str) -> bool:
        if any(token_address in self.trollers[name].markets for name in self.trollers):
            return True
        # NOTE: Workaround for pools that have since been revoked
        result = has_methods(token_address, ['isCToken()(bool)','comptroller()(address)','underlying()(address)'])
        if result is True: self.notify_if_unknown_comptroller(token_address)
        return result
    
    @log(logger)
    def __contains__(self, token_address: str) -> bool:
        return self.is_compound_market(token_address)
    
    @log(logger)
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

    @log(logger)
    def notify_if_unknown_comptroller(self, token_address: str) -> None:
        '''
        If the `comptroller` for token `token_address` is not known to ypricemagic, log a message:
        - `logger.warn(f'Comptroller {comptroller} is unknown to ypricemagic.')`
        - `logger.warn('Please create an issue and/or create a PR at https://github.com/BobTheBuidler/ypricemagic')`
        - `logger.warn(f'In your issue, please include the network {network_details} and the comptroller address')`
        - `logger.warn('and I will add it soon :). This will not prevent ypricemagic from fetching price for this asset.')`
        '''
        comptroller = raw_call(token_address,'comptroller()',output='address')
        if comptroller not in self.trollers:
            gh_issue_request(f'Comptroller {comptroller} is unknown to ypricemagic.', logger)


compound = Compound()
