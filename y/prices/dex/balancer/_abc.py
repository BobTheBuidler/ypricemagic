
import abc
from typing import Generic, Optional, Tuple, Type, TypeVar

import a_sync

import y.ENVIRONMENT_VARIABLES as ENVS
from y import contracts
from y.classes._abc import LiquidityPool
from y._decorators import stuck_coro_debugger
from y.datatypes import AddressOrContract, AnyAddressType, Block, UsdPrice


class BalancerPool(LiquidityPool):
    """A :class:`~LiquidityPool` specific to the Balancer protocol."""

_B = TypeVar("_B", bound=BalancerPool)

class BalancerABC(a_sync.ASyncGenericBase, Generic[_B]):
    def __repr__(self) -> str:
        return f"<{type(self).__name__} object at {hex(id(self))}>"
    @a_sync.a_sync(ram_cache_ttl=5*60)
    @stuck_coro_debugger
    async def is_pool(self, token_address: AnyAddressType) -> bool:
        return await contracts.has_methods(token_address, self._check_methods, sync=False)
    @stuck_coro_debugger
    async def get_pool_price(self, pool_address: AnyAddressType, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE) -> UsdPrice:
        return await self._pool_type(pool_address, asynchronous=True).get_pool_price(block=block, skip_cache=skip_cache)
    @abc.abstractproperty
    def _pool_type(self) -> Type[_B]:
        ...
    @abc.abstractproperty
    def _check_methods(self) -> Tuple[str]:
        ...
    @abc.abstractmethod
    async def get_token_price(self, token_address: AddressOrContract, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE) -> Optional[UsdPrice]:
        ...