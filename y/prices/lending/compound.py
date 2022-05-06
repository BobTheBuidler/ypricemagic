import logging
from functools import cached_property, lru_cache
from typing import Any, Optional, Set

from brownie import chain, convert
from multicall import Call
from y.classes.common import ERC20, ContractBase
from y.classes.singleton import Singleton
from y.constants import EEE_ADDRESS
from y.contracts import has_methods
from y.datatypes import UsdPrice
from y.networks import Network
from y.typing import AddressOrContract, AnyAddressType, Block
from y.utils.logging import gh_issue_request, yLazyLogger
from y.utils.raw_calls import raw_call

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
        "ola":              "0xD65eB596cFb5DE402678a12df651E0e588Dc3A81",
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


class CToken(ERC20):
    def __init__(self, address: AnyAddressType, *args: Any, **kwargs: Any) -> None:
        super().__init__(address, *args, **kwargs)
    
    def get_price(self, block: Optional[Block] = None) -> UsdPrice:
        return UsdPrice(self.underlying_per_ctoken(block=block) * self.underlying.price(block=block))
    
    @cached_property
    @yLazyLogger(logger)
    def underlying(self) -> ERC20:
        underlying = self.has_method('underlying()(address)', return_response=True)

        # this will run for gas coin markets like cETH, crETH
        if not underlying:
            underlying = EEE_ADDRESS

        return ERC20(underlying)
    
    @yLazyLogger(logger)
    @lru_cache
    def underlying_per_ctoken(self, block: Optional[Block] = None) -> float:
        return self.exchange_rate(block=block) * 10 ** (self.decimals - self.underlying.decimals)
    
    @yLazyLogger(logger)
    @lru_cache
    def exchange_rate(self, block: Optional[Block] = None) -> float:
        method = 'exchangeRateCurrent()(uint)'
        try:
            exchange_rate = Call(self.address, [method], [[method,None]], block_id=block)()[method]
        except Exception as e:
            if 'borrow rate is absurdly high' in str(e):
                exchange_rate = 0
            else:
                raise
        return exchange_rate / 1e18
    

class Comptroller(ContractBase):
    def __init__(self, address: Optional[AnyAddressType] = None, key: Optional[str] = None) -> None:
        assert address or key,          'Must provide either an address or a key'
        assert not (address and key),   'Must provide either an address or a key, not both'

        if key: address = TROLLERS[key]
        else: key = [key for key in TROLLERS if address == TROLLERS[key]][0]

        self.address = convert.to_address(address)
        self.key = key
    
    def __repr__(self) -> str:
        return f"<Comptroller {self.key} '{self.address}'>"

    @yLazyLogger(logger)
    def __contains__(self, token_address: AnyAddressType) -> bool:
        return token_address in self.markets
    
    @cached_property
    def markets(self) -> Set[CToken]:
        response = self.has_method("getAllMarkets()(address[])", return_response=True)
        if not response:
            logger.error(f'had trouble loading markets for {self.__repr__()}')
            response = set()
        markets = {CToken(market) for market in response}
        logger.info(f"loaded {len(markets)} markets for {self.__repr__()}")
        return markets


class Compound(metaclass = Singleton):
    def __init__(self) -> None:
        self.trollers = {
            protocol: Comptroller(troller)
            for protocol, troller
            in TROLLERS.items()
        }

    @yLazyLogger(logger)
    def is_compound_market(self, token_address: AddressOrContract) -> bool:
        if any(token_address in troller for troller in self.trollers.values()):
            return True

        # NOTE: Workaround for pools that have since been revoked
        result = has_methods(token_address, ['isCToken()(bool)','comptroller()(address)','underlying()(address)'])
        if result is True: self.__notify_if_unknown_comptroller(token_address)
        return result
    
    @yLazyLogger(logger)
    def get_price(self, token_address: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
        return CToken(token_address).get_price(block=block)

    @yLazyLogger(logger)
    def __contains__(self, token_address: AddressOrContract) -> bool:
        return self.is_compound_market(token_address)

    @yLazyLogger(logger)
    def __notify_if_unknown_comptroller(self, token_address: AddressOrContract) -> None:
        comptroller = raw_call(token_address,'comptroller()',output='address')
        if comptroller not in self.trollers.values():
            gh_issue_request(f'Comptroller {comptroller} is unknown to ypricemagic.', logger)


compound = Compound()
