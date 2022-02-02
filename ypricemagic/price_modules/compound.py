import logging

from brownie import chain, convert, web3
from multicall import Call, Multicall
from y.constants import EEE_ADDRESS
from y.contracts import has_methods
from y.decorators import log
from y.networks import Network
from y.utils.logging import gh_issue_request
from ypricemagic.utils.raw_calls import _decimals, raw_call

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

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
        "apple":            "0x46220a07F071D1a821D68fA7C769BCcdA3C65430",
        "chumhum":          "0x1D43f6DA91e9EF6614dCe95bCef43E4d7b2bcFB5",
        "cream":            "0x20CA53E2395FA571798623F1cFBD11Fe2C114c24",
    },
    Network.Fantom: {
        "cream":            "0x4250A6D3BD57455d7C6821eECb6206F507576cD2",
        "scream":           "0x260E596DAbE3AFc463e75B6CC05d8c46aCAcFB09",
    },
    Network.Avalanche: {
        "vee":              "0xA67DFeD73025b0d61F2515c531dd8D25D4Cfd0Db",
        "vee2":             "0x43AAd7d8Bc661dfA70120865239529ED92Faa054",
        "vee3":             "0xeEf69Cab52480D2BD2D4A3f3E8F5CcfF2923f6eF",
        "cream":            "0x2eE80614Ccbc5e28654324a66A396458Fa5cD7Cc",
    },
    Network.Arbitrum: {
        "cream":            "0xbadaC56c9aca307079e8B8FC699987AAc89813ee",
        "neku":             "0xD5B649c7d27C13a2b80425daEe8Cb6023015Dc6B",
        "channels":         "0x3C13b172bf8BE5b873EB38553feC50F78c826284",
        "hund":             "0x0F390559F258eB8591C8e31Cf0905E97cf36ACE2",
    }
}.get(chain.id, {})


class Comptroller:
    def __init__(self, address: str = None, key: str = None) -> None:

        assert address or key,          'Must provide either an address or a key'
        assert not (address and key),   'Must provide either an address or a key, not both'

        if key: address = TROLLERS[key]
        else: key = [key for key in TROLLERS if address == TROLLERS[key]][0]

        self.address = convert.to_address(address)
        self.key = key
        self.markets = {
            convert.to_address(market)
            for market
            in Call(self.address, ["getAllMarkets()(address[])"],[['markets',None]], _w3=web3)()['markets']
        }
        logger.info(f"loaded {len(self.markets)} lending markets on {self.key}")
    

    @log(logger)
    def __contains__(self, token_address: str) -> bool:
        return convert.to_address(token_address) in self.markets


class Compound:
    def __init__(self) -> None:
        self.trollers = {
            protocol: Comptroller(troller)
            for protocol, troller
            in TROLLERS.items()
        }


    @log(logger)
    def is_compound_market(self, token_address: str) -> bool:
        if any(token_address in troller for troller in self.trollers.values()):
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
        methods = 'underlying()(address)','exchangeRateCurrent()(uint)','decimals()(uint)'
        calls = [Call(token_address, [method], [[i,None]]) for i, method in enumerate(methods)]
        underlying, exchange_rate, decimals = Multicall(calls, block_id=block, _w3=web3, require_success=False)().values()

        # this will run for gas coin markets like cETH, crETH
        if underlying is None: underlying, under_decimals = EEE_ADDRESS, 18
        else: under_decimals = _decimals(underlying,block)
        
        exchange_rate /= 1e18

        return [exchange_rate * 10 ** (decimals - under_decimals), underlying]


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
        if comptroller not in self.trollers.values():
            gh_issue_request(f'Comptroller {comptroller} is unknown to ypricemagic.', logger)


compound = Compound()
