import abc
from typing import Generic, Optional, Tuple, Type, TypeVar

import a_sync

import y.ENVIRONMENT_VARIABLES as ENVS
from y import contracts
from y.classes._abc import LiquidityPool
from y._decorators import stuck_coro_debugger
from y.datatypes import AddressOrContract, AnyAddressType, Block, UsdPrice


class BalancerPool(LiquidityPool):
    """
    Represents a liquidity pool specific to the Balancer protocol.

    This class is a subclass of :class:`~y.classes._abc.LiquidityPool` and is intended to represent
    a Balancer pool. However, it currently does not implement any specific functionality or methods
    related to the Balancer protocol.

    Examples:
        >>> class MyBalancerPool(BalancerPool):
        ...     pass
        >>> pool = MyBalancerPool("0xAddress")
        >>> print(pool)
        <MyBalancerPool object at 0x...>

    See Also:
        - :class:`~y.classes._abc.LiquidityPool`
    """


_B = TypeVar("_B", bound=BalancerPool)


class BalancerABC(a_sync.ASyncGenericBase, Generic[_B]):
    """
    Abstract base class for interacting with Balancer pools.

    This class provides asynchronous methods to check if a token is a Balancer pool and to get the price
    of a pool. It uses the :mod:`a_sync` library for asynchronous operations.

    Examples:
        >>> class MyBalancer(BalancerABC):
        ...     _pool_type = MyBalancerPool
        ...     _check_methods = ("method1", "method2")
        ...     async def get_token_price(self, token_address, block=None, skip_cache=False):
        ...         return UsdPrice(100.0)
        >>> balancer = MyBalancer()
        >>> is_pool = await balancer.is_pool("0xTokenAddress")
        >>> print(is_pool)
        True

    See Also:
        - :class:`~y.classes._abc.LiquidityPool`
    """

    def __repr__(self) -> str:
        return f"<{type(self).__name__} object at {hex(id(self))}>"

    @a_sync.a_sync(ram_cache_ttl=5 * 60)
    @stuck_coro_debugger
    async def is_pool(self, token_address: AnyAddressType) -> bool:
        """
        Check if the given token address is a Balancer pool.

        Args:
            token_address: The address of the token to check.

        Returns:
            True if the token is a Balancer pool, False otherwise.

        Examples:
            >>> is_pool = await balancer.is_pool("0xTokenAddress")
            >>> print(is_pool)
            True
        """
        return await contracts.has_methods(
            token_address, self._check_methods, sync=False
        )

    @stuck_coro_debugger
    async def get_pool_price(
        self,
        pool_address: AnyAddressType,
        block: Optional[Block] = None,
        skip_cache: bool = ENVS.SKIP_CACHE,
    ) -> UsdPrice:
        """
        Get the price of a Balancer pool.

        Args:
            pool_address: The address of the pool.
            block: The block number at which to get the price. If None, uses the latest block.
            skip_cache: If True, bypasses ypricemagic's local caching mechanisms and forces a fresh calculation.

        Returns:
            The price of the pool as a :class:`~y.datatypes.UsdPrice` object.

        Examples:
            >>> price = await balancer.get_pool_price("0xPoolAddress")
            >>> print(price)
            100.0
        """
        return await self._pool_type(pool_address, asynchronous=True).get_pool_price(
            block=block, skip_cache=skip_cache
        )

    @property
    @abc.abstractmethod
    def _pool_type(self) -> Type[_B]:
        """
        The type of Balancer pool.

        This property should be overridden by subclasses to specify the type of Balancer pool.

        Examples:
            >>> class MyBalancer(BalancerABC):
            ...     _pool_type = MyBalancerPool
        """

    @property
    @abc.abstractmethod
    def _check_methods(self) -> Tuple[str]:
        """
        The methods to check for identifying a Balancer pool.

        This property should be overridden by subclasses to specify the methods used to identify a Balancer pool.

        Examples:
            >>> class MyBalancer(BalancerABC):
            ...     _check_methods = ("method1", "method2")
        """

    @abc.abstractmethod
    async def get_token_price(
        self,
        token_address: AddressOrContract,
        block: Optional[Block] = None,
        skip_cache: bool = ENVS.SKIP_CACHE,
    ) -> Optional[UsdPrice]:
        """
        Get the price of a token in a Balancer pool.

        This method should be implemented by subclasses to provide the logic for retrieving the token price.

        Args:
            token_address: The address of the token.
            block: The block number at which to get the price. If None, uses the latest block.
            skip_cache: If True, bypasses ypricemagic's local caching mechanisms and forces a fresh calculation.

        Examples:
            >>> price = await balancer.get_token_price("0xTokenAddress")
            >>> print(price)
            100.0
        """
