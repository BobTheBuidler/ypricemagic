import logging
from typing import List, Optional, Union

import a_sync
from a_sync.a_sync.property import HiddenMethodDescriptor
from typing_extensions import Self

from y import ENVIRONMENT_VARIABLES as ENVS
from y import exceptions
from y._decorators import stuck_coro_debugger
from y.constants import CHAINID, CONNECTED_TO_MAINNET
from y.datatypes import AnyAddressType, Block, UsdPrice
from y.networks import Network
from y.prices.dex.balancer._abc import BalancerABC
from y.prices.dex.balancer.v1 import BalancerV1
from y.prices.dex.balancer.v2 import BalancerV2
from y.utils.cache import optional_async_diskcache


logger = logging.getLogger(__name__)


class BalancerMultiplexer(a_sync.ASyncGenericBase):
    """A multiplexer for interacting with different versions of Balancer pools.

    This class provides methods to determine if a token is a Balancer pool,
    retrieve pool prices, and get token prices across different Balancer versions.

    Examples:
        Initialize the multiplexer:

        >>> multiplexer = BalancerMultiplexer(asynchronous=True)

        Check if a token is a Balancer pool:

        >>> is_pool = await multiplexer.is_balancer_pool(token_address)

        Get the price of a token:

        >>> price = await multiplexer.get_price(token_address, block=12345678)

    See Also:
        - :class:`BalancerV1`
        - :class:`BalancerV2`
    """

    def __init__(self, *, asynchronous: bool = False) -> None:
        """
        Initialize the BalancerMultiplexer.

        Args:
            asynchronous: Whether to operate in asynchronous mode.
        """
        super().__init__()
        self.asynchronous = asynchronous

    @a_sync.aka.property
    async def versions(self) -> List[Union[BalancerV1, BalancerV2]]:
        """
        Get the available Balancer versions.

        Returns:
            A list of available Balancer versions.

        Examples:
            >>> versions = await multiplexer.versions
        """
        return [
            v
            async for v in a_sync.as_completed([self.__v1__, self.__v2__], aiter=True)
            if v
        ]

    __versions__: HiddenMethodDescriptor[Self, List[Union[BalancerV1, BalancerV2]]]

    @a_sync.aka.cached_property
    async def v1(self) -> Optional[BalancerV1]:
        """
        Get the Balancer V1 instance.

        Returns:
            An instance of BalancerV1 if available, otherwise None.

        Examples:
            >>> v1 = await multiplexer.v1
        """
        try:
            return BalancerV1(asynchronous=self.asynchronous)
        except ImportError:
            return None

    __v1__: HiddenMethodDescriptor[Self, Optional[BalancerV1]]

    @a_sync.aka.cached_property
    async def v2(self) -> Optional[BalancerV2]:
        """
        Get the Balancer V2 instance.

        Returns:
            An instance of BalancerV2 if available, otherwise None.

        Examples:
            >>> v2 = await multiplexer.v2
        """
        try:
            return BalancerV2(asynchronous=self.asynchronous)
        except ImportError:
            return None

    __v2__: HiddenMethodDescriptor[Self, Optional[BalancerV2]]

    @stuck_coro_debugger
    @optional_async_diskcache
    async def is_balancer_pool(self, token_address: AnyAddressType) -> bool:
        """
        Check if a given token address is a Balancer pool.

        Args:
            token_address: The address of the token to check.

        Returns:
            True if the token is a Balancer pool, otherwise False.

        Examples:
            >>> is_pool = await multiplexer.is_balancer_pool(token_address)
        """
        try:
            await self.get_version(token_address)
            return True
        except exceptions.TokenError:
            return False

    @stuck_coro_debugger
    async def get_pool_price(
        self,
        token_address: AnyAddressType,
        block: Optional[Block] = None,
        skip_cache: bool = ENVS.SKIP_CACHE,
    ) -> Optional[UsdPrice]:
        """
        Get the price of a Balancer pool.

        Args:
            token_address: The address of the pool token.
            block: The block number to query the price at.
            skip_cache: Whether to skip the cache.

        Returns:
            The price of the pool in USD, or None if not available.

        Examples:
            >>> price = await multiplexer.get_pool_price(token_address, block=12345678)
        """
        balancer: BalancerABC = await self.get_version(token_address)
        logger.debug("pool %s is from %s", token_address, balancer)
        price = await balancer.get_pool_price(
            token_address, block, skip_cache=skip_cache, sync=False
        )
        return None if price is None else UsdPrice(price)

    @stuck_coro_debugger
    @a_sync.a_sync(ram_cache_ttl=ENVS.CACHE_TTL)
    async def get_price(
        self,
        token_address: AnyAddressType,
        block: Optional[Block] = None,
        skip_cache: bool = ENVS.SKIP_CACHE,
    ) -> Optional[UsdPrice]:
        """
        Get the price of a token using Balancer pools.

        Args:
            token_address: The address of the token.
            block: The block number to query the price at.
            skip_cache: Whether to skip the cache.

        Returns:
            The price of the token in USD, or None if not available.

        Examples:
            >>> price = await multiplexer.get_price(token_address, block=12345678)
        """
        if await self.is_balancer_pool(token_address, sync=False):
            return await self.get_pool_price(
                token_address, block=block, skip_cache=skip_cache, sync=False
            )

        price = None

        if (  # NOTE: Only query v2 if block queried > v2 deploy block plus some extra blocks to build up liquidity
            CONNECTED_TO_MAINNET and (not block or block > 12272146 + 100000)
        ) or (
            CHAINID == Network.Fantom and (not block or block > 16896080)
        ):  # TODO: refactor this out
            v2 = await self.__v2__
            if price := await v2.get_token_price(
                token_address, block, skip_cache=skip_cache, sync=False
            ):
                logger.debug("balancer v2 -> $%s", price)
                return price

        if not price and CONNECTED_TO_MAINNET:
            v1 = await self.__v1__
            if price := await v1.get_token_price(
                token_address, block, skip_cache=skip_cache, sync=False
            ):
                logger.debug("balancer v1 -> $%s", price)
                return price

    # cached forever because not many items
    @a_sync.a_sync(cache_type="memory", ram_cache_ttl=None)
    async def get_version(self, token_address: AnyAddressType) -> BalancerABC:
        """
        Determine the Balancer version for a given token address.

        Args:
            token_address: The address of the token.

        Returns:
            The Balancer version instance.

        Raises:
            exceptions.TokenError: If the token is not a Balancer pool.

        Examples:
            >>> version = await multiplexer.get_version(token_address)
        """
        for v in await self.__versions__:
            if await v.is_pool(token_address, sync=False):
                return v
        raise exceptions.TokenError(token_address, "Balancer pool")


balancer_multiplexer = BalancerMultiplexer(asynchronous=True)
