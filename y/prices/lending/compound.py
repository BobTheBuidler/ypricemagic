import asyncio
import logging
from functools import cached_property, lru_cache
from typing import Any, Optional, Tuple

from async_property import async_cached_property
from brownie import chain, convert
from multicall import Call
from multicall.utils import await_awaitable

from y.classes.common import ERC20, ContractBase
from y.classes.singleton import Singleton
from y.constants import EEE_ADDRESS
from y.contracts import Contract, has_methods_async
from y.datatypes import AddressOrContract, AnyAddressType, Block, UsdPrice
from y.exceptions import call_reverted
from y.networks import Network
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
    def __init__(self, address: AnyAddressType, comptroller: Optional["Comptroller"], *args: Any, **kwargs: Any) -> None:
        self.comptroller = comptroller
        super().__init__(address, *args, **kwargs)
    
    def get_price(self, block: Optional[Block] = None) -> UsdPrice:
        return await_awaitable(self.get_price_async(block))
    
    async def get_price_async(self, block: Optional[Block] = None) -> UsdPrice:
        if self.troller:
            # We can use the protocol's oracle which will be quick
            underlying_per_ctoken, underlying_price = await asyncio.gather(
                self.underlying_per_ctoken_async(block=block),
                self.get_underlying_price(block=block),
            )
        else:
            # Or we can just price the underlying token ourselves
            underlying = await self.underlying_async
            underlying_per_ctoken, underlying_price = await asyncio.gather(
                self.underlying_per_ctoken_async(block=block),
                underlying.price_async(block=block)
            )
        return UsdPrice(underlying_per_ctoken * underlying_price)
    
    @cached_property
    #yLazyLogger(logger)
    def underlying(self) -> ERC20:
        return await_awaitable(self.underlying_async)
    
    #yLazyLogger(logger)
    @async_cached_property
    async def underlying_async(self) -> ERC20:
        underlying = await self.has_method_async('underlying()(address)', return_response=True)

        # this will run for gas coin markets like cETH, crETH
        if not underlying:
            underlying = EEE_ADDRESS

        return ERC20(underlying)
    
    #yLazyLogger(logger)
    @lru_cache
    def underlying_per_ctoken(self, block: Optional[Block] = None) -> float:
        return await_awaitable(self.underlying_per_ctoken_async(block))
    
    #yLazyLogger(logger)
    async def underlying_per_ctoken_async(self, block: Optional[Block] = None) -> float:
        exchange_rate, decimals, underlying = await asyncio.gather(
            self.exchange_rate_async(block=block),
            self.decimals,
            self.underlying_async,
        )
        return exchange_rate * 10 ** (decimals - await underlying.decimals)
    
    #yLazyLogger(logger)
    @lru_cache
    def exchange_rate(self, block: Optional[Block] = None) -> float:
        return await_awaitable(self.exchange_rate(block))

    #yLazyLogger(logger)
    async def exchange_rate_async(self, block: Optional[Block] = None) -> float:
        method = 'exchangeRateCurrent()(uint)'
        call = Call(self.address, [method], block_id=block)

        try:
            exchange_rate = await call.coroutine()
        except Exception as e:
            if not call_reverted(e):
                raise e
            exchange_rate = None

        if exchange_rate is None:
            # NOTE: Sometimes this works, not sure why
            try:
                exchange_rate = self.contract.exchangeRateCurrent.call(block_identifier=block)
            except Exception as e:
                if 'borrow rate is absurdly high' not in str(e):
                    raise
                exchange_rate = 0
        
        return exchange_rate / 1e18
    
    async def get_underlying_price(self, block: Optional[Block] = None) -> float:
        # always query the oracle in case it was changed
        oracle, underlying = await asyncio.gather(
            self.comptroller.oracle(block),
            self.underlying_async
        )
        price, underlying_decimals = await asyncio.gather(
            oracle.getUnderlyingPrice.coroutine(self.address, block_identifier=block),
            underlying.decimals
        ) 
        price /= 10 ** (36 - underlying_decimals)
        return price
    

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

    #yLazyLogger(logger)
    def __contains__(self, token_address: AnyAddressType) -> bool:
        return token_address in self.markets
    
    @cached_property
    def markets(self) -> Tuple[CToken]:
        return await_awaitable(self.markets_async)

    @async_cached_property
    async def markets_async(self) -> Tuple[CToken]:
        response = await self.has_method_async("getAllMarkets()(address[])", return_response=True)
        if not response:
            logger.error(f'had trouble loading markets for {self.__repr__()}')
            response = set()
        markets = tuple(CToken(market, self) for market in response)
        logger.info(f"loaded {len(markets)} markets for {self.__repr__()}")
        return markets
    
    async def oracle(self, block: Optional[Block] = None) -> Contract:
        oracle = await self.contract.oracle.coroutine(block_identifier=block)
        return await Contract.coroutine(oracle)


class Compound(metaclass = Singleton):
    def __init__(self) -> None:
        self.trollers = {
            protocol: Comptroller(troller)
            for protocol, troller
            in TROLLERS.items()
        }
    
    async def get_troller(self, token_address: AddressOrContract) -> Optional[Comptroller]:
        trollers = self.trollers.values()
        all_markets = await asyncio.gather(*[troller.markets_async for troller in trollers])
        for troller, markets in zip(trollers, all_markets):
            if token_address in markets:
                return troller

    #yLazyLogger(logger)
    def is_compound_market(self, token_address: AddressOrContract) -> bool:
        return await_awaitable(self.is_compound_market_async(token_address))
    
    #yLazyLogger(logger)
    async def is_compound_market_async(self, token_address: AddressOrContract) -> bool:
        if await self.get_troller(token_address):
            return True

        # NOTE: Workaround for pools that have since been revoked
        result = await has_methods_async(token_address, ('isCToken()(bool)','comptroller()(address)','underlying()(address)'))
        if result is True: self.__notify_if_unknown_comptroller(token_address)
        return result
    
    #yLazyLogger(logger)
    def get_price(self, token_address: AnyAddressType, block: Optional[Block] = None) -> Optional[UsdPrice]:
        return await_awaitable(self.get_price_async(token_address, block=block))

    #yLazyLogger(logger)
    async def get_price_async(self, token_address: AnyAddressType, block: Optional[Block] = None) -> Optional[UsdPrice]:
        troller = await self.get_troller(token_address)
        return await CToken(token_address, troller).get_price_async(block=block)

    #yLazyLogger(logger)
    def __contains__(self, token_address: AddressOrContract) -> bool:
        return self.is_compound_market(token_address)

    #yLazyLogger(logger)
    def __notify_if_unknown_comptroller(self, token_address: AddressOrContract) -> None:
        comptroller = raw_call(token_address,'comptroller()',output='address')
        if comptroller not in self.trollers.values():
            gh_issue_request(f'Comptroller {comptroller} is unknown to ypricemagic.', logger)


compound = Compound()
