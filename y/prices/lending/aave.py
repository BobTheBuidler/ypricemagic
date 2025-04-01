import logging
from abc import abstractmethod
from decimal import Decimal
from typing import Awaitable, List, Optional, Union

import a_sync
from a_sync import cgather, igather
from a_sync.a_sync import HiddenMethodDescriptor
from brownie import chain
from multicall import Call
from typing_extensions import Self
from web3.exceptions import ContractLogicError

from y import ENVIRONMENT_VARIABLES as ENVS
from y import convert
from y.classes.common import ERC20, ContractBase
from y.contracts import Contract
from y.datatypes import Address, AddressOrContract, AnyAddressType, Block, UsdPrice
from y.networks import Network
from y.utils import hasall
from y.utils.logging import get_price_logger
from y.utils.raw_calls import raw_call

logger = logging.getLogger(__name__)


v1_pools = {
    Network.Mainnet: ("0x398eC7346DcD622eDc5ae82352F02bE94C62d119",),
}.get(chain.id, ())

v2_pools = {
    Network.Mainnet: (
        "0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9",  # aave
        "0x7937D4799803FbBe595ed57278Bc4cA21f3bFfCB",  # aave amm
        "0xcE744a9BAf573167B2CF138114BA32ed7De274Fa",  # umee
    ),
    Network.Polygon: ("0x8dFf5E27EA6b7AC08EbFdf9eB090F32ee9a30fcf",),  # aave
    Network.Avalanche: ("0x70BbE4A294878a14CB3CDD9315f5EB490e346163",),  # blizz
}.get(chain.id, [])

v3_pools = {
    Network.Mainnet: ("0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2",),  # aave v3
    Network.Optimism: ("0x794a61358D6845594F94dc1DB02A252b5b4814aD",),  # aave v3
    Network.Arbitrum: ("0x794a61358D6845594F94dc1DB02A252b5b4814aD",),  # aave v3
    Network.Harmony: ("0x794a61358D6845594F94dc1DB02A252b5b4814aD",),  # aave v3
    Network.Arbitrum: ("0x794a61358D6845594F94dc1DB02A252b5b4814aD",),  # aave v3
    Network.Fantom: ("0x794a61358D6845594F94dc1DB02A252b5b4814aD",),  # aave v3
    Network.Avalanche: ("0x794a61358D6845594F94dc1DB02A252b5b4814aD",),  # aave v3
    Network.Polygon: ("0x794a61358D6845594F94dc1DB02A252b5b4814aD",),  # aave v3
}.get(chain.id, ())


class AaveMarketBase(ContractBase):
    """
    Base class for Aave markets.

    This class provides common functionality for Aave markets, including methods
    to check if a token is an aToken from the market and to retrieve reserve data.

    See Also:
        - :class:`AaveMarketV1`
        - :class:`AaveMarketV2`
        - :class:`AaveMarketV3`
    """

    def __contains__(self, token: object) -> bool:
        """
        Check if `token` is an aToken from this market.

        This method is intended for synchronous use. If `self.asynchronous` is not `False`,
        a `RuntimeError` will be raised.

        Args:
            token: The item to check.

        Returns:
            True if the token is an aToken from the market, False otherwise.

        Raises:
            RuntimeError: If `self.asynchronous` is not `False`.

        Example:
            >>> market = AaveMarketV1("0xAddress")
            >>> token = "0xTokenAddress"
            >>> token in market
            True
        """
        if not self.asynchronous:
            cls = self.__class__.__name__
            raise RuntimeError(
                f"'self.asynchronous' must be False to use {cls}.__contains__.\nYou may wish to use {cls}.is_atoken instead."
            )
        return convert.to_address(token) in self.atokens

    async def contains(self, token: object) -> bool:
        """
        Check if `token` is an aToken from this market.

        This method is intended for asynchronous use.

        Args:
            token: The item to check.

        Returns:
            True if the token is an aToken from the market, False otherwise.

        Example:
            >>> market = AaveMarketV1("0xAddress", asynchronous=True)
            >>> token = "0xTokenAddress"
            >>> await market.contains(token)
            True
        """
        contains = await convert.to_address_async(token) in await self.__atokens__
        logger.debug("%s contains %s: %s", self, token, contains)
        return contains

    async def get_reserves(self) -> List[Address]:
        return await Call(self.address, [self._get_reserves_method])

    async def get_reserve_data(self, reserve: AnyAddressType) -> tuple:
        return await self.contract.getReserveData.coroutine(reserve)

    @property
    @abstractmethod
    async def atokens(self) -> Awaitable[List[ERC20]]:
        """
        Get the aTokens of the market.

        This is an abstract property and must be implemented by subclasses.

        Returns:
            A list of aTokens as :class:`~ERC20` objects.

        Example:
            >>> market = AaveMarketV1("0xAddress", asynchronous=True)
            >>> atokens = await market.atokens
            >>> print(atokens)
            [<ERC20 '0xTokenAddress1'>, <ERC20 '0xTokenAddress2'>]
        """

    __atokens__: HiddenMethodDescriptor[Self, List[ERC20]]

    @abstractmethod
    async def underlying(self, atoken_address: AddressOrContract) -> ERC20:
        """
        Get the underlying asset of the given aToken address.

        This is an abstract method and must be implemented by subclasses.

        Args:
            atoken_address: The address of the aToken.

        Returns:
            The underlying asset.

        Example:
            >>> market = AaveMarketV1("0xAddress", asynchronous=True)
            >>> underlying_asset = await market.underlying("0xATokenAddress")
            >>> print(underlying_asset)
            <ERC20 '0xUnderlyingAssetAddress'>
        """

    @property
    @abstractmethod
    def _get_reserves_method(self) -> str:
        """
        The method that must be called to get the reserves list.

        This is an abstract property and must be implemented by subclasses.

        Example:
            >>> market = AaveMarketV1("0xAddress")
            >>> print(market._get_reserves_method)
            'getReserves()(address[])'
        """


class AaveMarketV1(AaveMarketBase):
    @a_sync.aka.cached_property
    async def atokens(self) -> List[ERC20]:
        reserves_data = a_sync.map(self.get_reserve_data, self.get_reserves(sync=False))
        atokens = [
            ERC20(reserve_data["aTokenAddress"], asynchronous=self.asynchronous)
            async for _, reserve_data in reserves_data
        ]
        logger.info("loaded %s v1 atokens for %s", len(atokens), repr(self))
        return atokens

    @a_sync.a_sync(ram_cache_maxsize=256)
    async def underlying(self, atoken_address: AddressOrContract) -> ERC20:
        underlying = await raw_call(
            atoken_address, "underlyingAssetAddress()", output="address", sync=False
        )
        return ERC20(underlying)

    _get_reserves_method = "getReserves()(address[])"


_V2_RESERVE_DATA_METHOD = "getReserveData(address)((uint256,uint128,uint128,uint128,uint128,uint128,uint40,address,address,address,address,uint8))"


class AaveMarketV2(AaveMarketBase):
    @a_sync.aka.cached_property
    async def atokens(self) -> List[ERC20]:
        reserves_data = a_sync.map(self.get_reserve_data, self.get_reserves(sync=False))
        try:
            atokens = [
                ERC20(reserve_data[7], asynchronous=self.asynchronous)
                async for _, reserve_data in reserves_data
            ]
            logger.info("loaded %s v2 atokens for %s", len(atokens), repr(self))
            return atokens
        except (
            TypeError
        ) as e:  # TODO figure out what to do about non verified aave markets
            logger.exception(e)
            logger.warning("failed to load tokens for %s", self)
            return []

    async def get_reserve_data(self, reserve: AnyAddressType) -> tuple:
        return await Call(self.address, [_V2_RESERVE_DATA_METHOD, str(reserve)])

    @a_sync.a_sync(ram_cache_maxsize=256)
    async def underlying(self, atoken_address: AddressOrContract) -> ERC20:
        underlying = await raw_call(
            atoken_address, "UNDERLYING_ASSET_ADDRESS()", output="address", sync=False
        )
        logger.debug("underlying: %s", underlying)
        return ERC20(underlying, asynchronous=self.asynchronous)

    _get_reserves_method = "getReservesList()(address[])"


class AaveMarketV3(AaveMarketBase):
    @a_sync.aka.cached_property
    async def atokens(self) -> List[ERC20]:
        reserves_data = a_sync.map(self.get_reserve_data, self.get_reserves(sync=False))
        try:
            atokens = [
                ERC20(reserve_data[8], asynchronous=self.asynchronous)
                async for _, reserve_data in reserves_data
            ]
            logger.info("loaded %s v3 atokens for %s", len(atokens), repr(self))
            return atokens
        except (
            TypeError
        ) as e:  # TODO figure out what to do about non verified aave markets
            logger.exception(e)
            logger.warning("failed to load tokens for %s", self)
            return []

    @a_sync.a_sync(ram_cache_maxsize=256)
    async def underlying(self, atoken_address: AddressOrContract) -> ERC20:
        underlying = await raw_call(
            atoken_address, "UNDERLYING_ASSET_ADDRESS()", output="address", sync=False
        )
        logger.debug("underlying: %s", underlying)
        return ERC20(underlying, asynchronous=self.asynchronous)

    _get_reserves_method = "getReservesList()(address[])"


AaveMarket = Union[AaveMarketV1, AaveMarketV2, AaveMarketV3]

_WRAPPED_V2_METHODS = "ATOKEN", "STATIC_ATOKEN_LM_REVISION", "staticToDynamicAmount"
_WRAPPED_V3_METHODS = "ATOKEN", "AAVE_POOL", "UNDERLYING"


class AaveRegistry(a_sync.ASyncGenericSingleton):
    def __init__(self, *, asynchronous: bool = False) -> None:
        self.asynchronous = asynchronous
        super().__init__()

    @a_sync.aka.cached_property
    async def pools(self) -> List[AaveMarket]:
        v1, v2, v3 = await cgather(
            self.__pools_v1__,
            self.__pools_v2__,
            self.__pools_v3__,
        )
        return v1 + v2 + v3

    __pools__: HiddenMethodDescriptor[Self, List[AaveMarket]]

    @a_sync.aka.cached_property
    async def pools_v1(self) -> List[AaveMarketV1]:
        pools = [
            AaveMarketV1(pool, asynchronous=self.asynchronous) for pool in v1_pools
        ]
        logger.debug("AaveRegistry v1 pools %s", pools)
        return pools

    __pools_v1__: HiddenMethodDescriptor[Self, List[AaveMarketV1]]

    @a_sync.aka.cached_property
    async def pools_v2(self) -> List[AaveMarketV2]:
        pools = [
            AaveMarketV2(pool, asynchronous=self.asynchronous) for pool in v2_pools
        ]
        logger.debug("AaveRegistry v2 pools %s", pools)
        return pools

    __pools_v2__: HiddenMethodDescriptor[Self, List[AaveMarketV2]]

    @a_sync.aka.cached_property
    async def pools_v3(self) -> List[AaveMarketV3]:
        pools = [
            AaveMarketV3(pool, asynchronous=self.asynchronous) for pool in v3_pools
        ]
        logger.debug("AaveRegistry v3 pools %s", pools)
        return pools

    __pools_v3__: HiddenMethodDescriptor[Self, List[AaveMarketV3]]

    async def pool_for_atoken(
        self, atoken_address: AnyAddressType
    ) -> Optional[Union[AaveMarketV1, AaveMarketV2, AaveMarketV3]]:
        pools = await self.__pools__
        for pool in pools:
            if await pool.contains(atoken_address, sync=False):
                return pool

    def __contains__(self, __o: object) -> bool:
        if self.asynchronous:
            raise RuntimeError(
                f"'self.asynchronous' must be False to use AaveRegistry.__contains__.\nYou may wish to use AaveRegistry.is_atoken instead."
            )
        return any(__o in pool for pool in self.pools)

    @a_sync.a_sync(cache_type="memory")
    async def is_atoken(self, atoken_address: AnyAddressType) -> bool:
        logger = get_price_logger(atoken_address, block=None, extra="aave")
        is_atoken = any(
            await igather(
                pool.contains(atoken_address, sync=False)
                for pool in await self.__pools__
            )
        )
        logger.debug("is_atoken: %s", is_atoken)
        return is_atoken

    async def is_wrapped_atoken_v2(self, atoken_address: AnyAddressType) -> bool:
        # NOTE: Not sure if this wrapped version is actually related to aave but this works for pricing purposes.
        contract = await Contract.coroutine(atoken_address, require_success=False)
        return contract.verified and hasall(contract, _WRAPPED_V2_METHODS)

    async def is_wrapped_atoken_v3(self, atoken_address: AnyAddressType) -> bool:
        # NOTE: Not sure if this wrapped version is actually related to aave but this works for pricing purposes.
        contract = await Contract.coroutine(atoken_address, require_success=False)
        return contract.verified and hasall(contract, _WRAPPED_V3_METHODS)

    @a_sync.a_sync(cache_type="memory")
    async def underlying(self, atoken_address: AddressOrContract) -> ERC20:
        pool: Union[AaveMarketV1, AaveMarketV2, AaveMarketV3] = (
            await self.pool_for_atoken(atoken_address, sync=False)
        )
        return await pool.underlying(atoken_address, sync=False)

    async def get_price(
        self,
        atoken_address: AddressOrContract,
        block: Optional[Block] = None,
        skip_cache: bool = ENVS.SKIP_CACHE,
    ) -> UsdPrice:
        underlying: ERC20 = await self.underlying(atoken_address, sync=False)
        return await underlying.price(block, skip_cache=skip_cache, sync=False)

    async def get_price_wrapped_v2(
        self,
        atoken_address: AddressOrContract,
        block: Optional[Block] = None,
        skip_cache: bool = ENVS.SKIP_CACHE,
    ) -> Optional[UsdPrice]:
        return await self._get_price_wrapped(
            atoken_address, "staticToDynamicAmount", block=block, skip_cache=skip_cache
        )

    async def get_price_wrapped_v3(
        self,
        atoken_address: AddressOrContract,
        block: Optional[Block] = None,
        skip_cache: bool = ENVS.SKIP_CACHE,
    ) -> Optional[UsdPrice]:
        return await self._get_price_wrapped(
            atoken_address, "convertToAssets", block=block, skip_cache=skip_cache
        )

    async def _get_price_wrapped(
        self,
        atoken_address: AddressOrContract,
        method: str,
        block: Optional[Block] = None,
        skip_cache: bool = ENVS.SKIP_CACHE,
    ) -> Optional[UsdPrice]:
        contract, scale = await cgather(
            Contract.coroutine(atoken_address),
            ERC20._get_scale_for(atoken_address),
        )
        try:
            underlying, price_per_share = await cgather(
                # NOTE: We can probably cache this without breaking anything
                contract.ATOKEN.coroutine(block_identifier=block),
                getattr(contract, method).coroutine(scale, block_identifier=block),
            )
        except ContractLogicError:
            return None
        price_per_share /= Decimal(scale)
        return price_per_share * Decimal(
            await ERC20(underlying, asynchronous=True).price(
                block, skip_cache=skip_cache
            )
        )


aave: AaveRegistry = AaveRegistry(asynchronous=True)
