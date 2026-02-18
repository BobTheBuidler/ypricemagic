import logging
from decimal import Decimal

import a_sync
from a_sync import cgather
from a_sync.a_sync import HiddenMethodDescriptor
from brownie import ZERO_ADDRESS, chain
from web3.exceptions import ContractLogicError

from y import ENVIRONMENT_VARIABLES as ENVS
from y import convert
from y._decorators import stuck_coro_debugger
from y.classes.common import ERC20
from y.contracts import Contract, has_methods
from y.datatypes import Address, AnyAddressType, Block, UsdPrice
from y.networks import Network
from y.utils.cache import a_sync_ttl_cache
from y.utils.raw_calls import raw_call

logger = logging.getLogger(__name__)

_POOL_METHODS = (
    "poolId()(uint256)",
    "token()(address)",
    "router()(address)",
    "sharedDecimals()(uint256)",
    "localDecimals()(uint256)",
    "convertRate()(uint256)",
    "totalLiquidity()(uint256)",
    "totalSupply()(uint256)",
)

SEED_POOLS = {
    Network.Mainnet: (
        # S*USDC (USD Coin-LP)
        "0xdf0770dF86a8034b3EFEf0A1Bb3c889B8332FF56",
    )
}

_factories: dict[Address, "StargateFactory"] = {}
_factory_pools: dict[Address, set[Address]] = {}
_known_pools: set[Address] = set()
_seeds_loaded: set[int] = set()


async def _factory_from_pool(pool: Address) -> Address | None:
    router = await raw_call(
        pool,
        "router()",
        output="address",
        return_None_on_failure=True,
        sync=False,
    )
    if not router or router == ZERO_ADDRESS:
        return None
    factory = await raw_call(
        router,
        "factory()",
        output="address",
        return_None_on_failure=True,
        sync=False,
    )
    if not factory or factory == ZERO_ADDRESS:
        return None
    return factory


async def _load_factory_pools(factory: Address) -> set[Address]:
    if factory in _factory_pools:
        return _factory_pools[factory]

    stargate_factory = _factories.get(factory)
    if stargate_factory is None:
        stargate_factory = StargateFactory(factory, asynchronous=True)
        _factories[factory] = stargate_factory

    pools = await stargate_factory.pools(sync=False)
    if pools:
        _factory_pools[factory] = pools
        _known_pools.update(pools)
    return pools


async def _prime_factory_cache() -> None:
    if chain.id in _seeds_loaded:
        return
    _seeds_loaded.add(chain.id)
    for pool in SEED_POOLS.get(chain.id, ()):  # type: ignore[arg-type]
        factory = await _factory_from_pool(pool)
        if factory:
            await _load_factory_pools(factory)


@a_sync.a_sync(default="sync", cache_type="memory", ram_cache_ttl=5 * 60)
async def is_stargate_lp(token_address: AnyAddressType) -> bool:
    token_address = await convert.to_address_async(token_address)
    await _prime_factory_cache()

    if token_address in _known_pools:
        return True

    if not await has_methods(token_address, _POOL_METHODS, sync=False):
        return False

    factory = await _factory_from_pool(token_address)
    if factory:
        await _load_factory_pools(factory)

    return True


class StargateFactory(a_sync.ASyncGenericBase):
    def __init__(self, address: Address, *, asynchronous: bool = False) -> None:
        self.address = address
        self.asynchronous = asynchronous
        super().__init__()

    @a_sync.aka.cached_property
    async def contract(self) -> Contract:
        return await Contract.coroutine(self.address)

    __contract__: HiddenMethodDescriptor["StargateFactory", Contract]

    @stuck_coro_debugger
    @a_sync_ttl_cache
    async def pools(self) -> set[Address]:
        try:
            all_pools_len = await raw_call(
                self.address,
                "allPoolsLength()",
                output="int",
                return_None_on_failure=True,
                sync=False,
            )
        except Exception as exc:  # pragma: no cover - defensive, depends on node
            logger.debug("Failed to read Stargate allPoolsLength: %s", exc)
            return set()

        if not all_pools_len:
            return set()

        pool_map = a_sync.map(
            self._pool_at,
            range(all_pools_len),
            name=f"load {self} poolId",
        )
        await pool_map._init_loader
        pools = await pool_map.values(pop=True)
        return {pool for pool in pools if pool and pool != ZERO_ADDRESS}

    @stuck_coro_debugger
    async def _pool_at(self, poolid: int) -> Address | None:
        return await raw_call(
            self.address,
            "allPools(uint256)",
            inputs=poolid,
            output="address",
            return_None_on_failure=True,
            sync=False,
        )


class StargatePool(ERC20):
    @a_sync.aka.cached_property
    async def contract(self) -> Contract:
        return await Contract.coroutine(self.address)

    __contract__: HiddenMethodDescriptor["StargatePool", Contract]

    @a_sync.aka.cached_property
    async def underlying(self) -> ERC20:
        token = await raw_call(
            self.address,
            "token()",
            output="address",
            return_None_on_failure=True,
            sync=False,
        )
        if not token or token == ZERO_ADDRESS:
            raise ValueError(f"Stargate pool {self.address} has no underlying token")
        return ERC20(token, asynchronous=self.asynchronous)

    __underlying__: HiddenMethodDescriptor["StargatePool", ERC20]

    async def amount_lp_to_ld(self, amount_lp: int, block: Block | None = None) -> int | None:
        pool = await self.__contract__
        try:
            return await pool.amountLPtoLD.coroutine(amount_lp, block_identifier=block)
        except ContractLogicError:
            return None

    @stuck_coro_debugger
    async def price(
        self,
        block: Block | None = None,
        skip_cache: bool = ENVS.SKIP_CACHE,
    ) -> UsdPrice | None:
        try:
            lp_scale, underlying = await cgather(self.__scale__, self.__underlying__)
        except ValueError:
            return None

        amount_ld = await self.amount_lp_to_ld(lp_scale, block=block)
        if amount_ld is None:
            return None

        underlying_scale, underlying_price = await cgather(
            underlying.__scale__,
            underlying.price(block, skip_cache=skip_cache, sync=False),
        )
        if underlying_price is None:
            return None

        ratio = Decimal(amount_ld) / Decimal(underlying_scale)
        return UsdPrice(ratio * Decimal(underlying_price))


@a_sync.a_sync(default="sync")
async def get_price(
    token_address: AnyAddressType,
    block: Block | None = None,
    skip_cache: bool = ENVS.SKIP_CACHE,
) -> UsdPrice | None:
    pool = StargatePool(token_address, asynchronous=True)
    return await pool.price(block=block, skip_cache=skip_cache, sync=False)
