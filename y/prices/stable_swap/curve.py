import abc
import asyncio
import logging
from collections import defaultdict
from decimal import Decimal
from enum import IntEnum
from functools import cached_property
from typing import Awaitable, Dict, List, Optional, Tuple, TypeVar

import a_sync
import brownie
from brownie import ZERO_ADDRESS, chain
from brownie.convert.datatypes import EthAddress
from brownie.exceptions import ContractNotFound
from brownie.network.event import _EventItem

from y import convert
from y.classes.common import ERC20, WeiBalance, _EventsLoader, _Loader
from y.contracts import Contract, contract_creation_block_async
from y.datatypes import (Address, AddressOrContract, AnyAddressType, Block,
                         Pool, UsdPrice, UsdValue)
from y.exceptions import (ContractNotVerified, MessedUpBrownieContract,
                          PriceError, UnsupportedNetwork, call_reverted)
from y.interfaces.curve.CurveRegistry import CURVE_REGISTRY_ABI
from y.networks import Network
from y.utils.events import ProcessedEvents
from y.utils.middleware import ensure_middleware
from y.utils.multicall import \
    multicall_same_func_same_contract_different_inputs
from y.utils.raw_calls import raw_call

T = TypeVar('T')

logger = logging.getLogger(__name__)

ensure_middleware()

# curve registry documentation https://curve.readthedocs.io/registry-address-provider.html
ADDRESS_PROVIDER = '0x0000000022D53366457F9d5E68Ec105046FC4383'

class Ids(IntEnum):
    Main_Registry = 0
    PoolInfo_Getters = 1
    Exchanges = 2
    Metapool_Factory = 3
    Fee_Distributor = 4
    CryptoSwap_Registry = 5
    CryptoPool_Factory = 6
    # On Mainnet, id 7 is listed as "metafactory".
    # On Polygon, id 7 is listed as "cryptopool factory".
    # On other chains, "cryptopool factory" is id 6.
    # On Polygon, id 6 is "crypto factory".
    # I've only seen this on Mainnet and Polygon so far, for now will treat `7` == `6`.
    Cryptopool_Factory = 7
    crvUSD_Plain_Pools_deprecated_1 = 8
    crvUSD_Plain_Pools_deprecated_2 = 9
    crvUSD_Plain_Pools = 10
    Curve_Tricrypto_Factory = 11



class _CurveLoader(_Loader):
    __slots__ = "curve",
    def __init__(self, address: Address, curve: "CurveRegistry", asynchronous: bool = False):
        super().__init__(address, asynchronous=asynchronous)
        self.curve = curve

_LT = TypeVar("_LT", bound=_CurveLoader)

class _CurveEventsLoader(_CurveLoader, _EventsLoader):
    _events: "CurveEvents"

class CurveEvents(ProcessedEvents[_EventItem]):
    __slots__ = "_base",
    def __init__(self, base: _LT):
        super().__init__(addresses=base.address)
        self._base = base
    
class AddressProviderEvents(CurveEvents):
    @property
    def provider(self) -> "AddressProvider":
        return self._base
    def _process_event(self, event) -> None:
        if event.name == 'NewAddressIdentifier' and event['addr'] != ZERO_ADDRESS:
            self.provider.identifiers[Ids(event['id'])].append(event['addr'])
        elif event.name == 'AddressModified' and event['new_address'] != ZERO_ADDRESS:
            self.provider.identifiers[Ids(event['id'])].append(event['new_address'])
        logger.debug("%s loaded event %s at block %s", self, event, event.block_number)
        return event
        
class RegistryEvents(CurveEvents):
    __slots__ = "_tasks",
    def __init__(self, base: _LT):
        super().__init__(base)
        self._tasks: List["asyncio.Task[EthAddress]"] = []
    @property
    def registry(self) -> "Registry":
        return self._base
    def _process_event(self, event: _EventItem) -> None:
        if event.name == 'PoolAdded':
            # TODO async this
            pool = event['pool']
            self._tasks.append(asyncio.create_task(coro=self._add_pool(pool), name=f"Registry._add_pool for pool {pool}"))
            self.registry.curve.registries[event.address].add(pool)
        elif event.name == 'PoolRemoved':
            self.registry.curve.registries[event.address].discard(event['pool'])
        logger.debug("%s loaded event %s at block %s", self, event, event.block_number)
        return event
    async def _add_pool(self, pool: Address) -> EthAddress:
        lp_token = await self.registry.contract.get_lp_token.coroutine(pool)
        self.registry.curve.token_to_pool[lp_token] = pool
    async def _set_lock(self, block: int) -> None:
        await asyncio.gather(*self._tasks)
        self._tasks.clear()
        self._lock.set(block)



class AddressProvider(_CurveEventsLoader):
    __slots__ = "identifiers", "_events", 
    def __init__(self, address: Address, curve: "CurveRegistry", asynchronous: bool = False):
        super().__init__(address, curve, asynchronous=asynchronous)
        self.identifiers = defaultdict(list)
        self._events = AddressProviderEvents(self)
    def __await__(self):
        return self.loaded.__await__()
    async def get_registry(self) -> EthAddress:
        return await self.contract.get_registry.coroutine()
    async def _load_factories(self) -> None:
        # factory events are quite useless, so we use a different method
        logger.debug("loading pools from metapool factories")
        metapool_factories = [
            Factory(factory, self.curve, asynchronous=self.asynchronous)
            for i in [Ids.Metapool_Factory, Ids.crvUSD_Plain_Pools, Ids.Curve_Tricrypto_Factory]
            for factory in self.identifiers[i]
        ]

        metapool_factory_pools = await asyncio.gather(*[factory.read_pools(sync=False) for factory in metapool_factories])
        for factory, pool_list in zip(metapool_factories, metapool_factory_pools):
            for pool in pool_list:
                # for metpool factories pool is the same as lp token
                self.curve.token_to_pool[pool] = pool
                self.curve.factories[factory].add(pool)

        # if there are factories that haven't yet been added to the on-chain address provider,
        # please refer to commit 3f70c4246615017d87602e03272b3ed18d594d3c to see how to add them manually
        logger.debug("loading pools from cryptopool factories")
        await asyncio.gather(*[
            Factory(factory, self.curve, asynchronous=self.asynchronous) 
            for factory in self.identifiers[Ids.CryptoPool_Factory] + self.identifiers[Ids.Cryptopool_Factory]
        ])
        if not self.curve._done.is_set():
            logger.info('loaded %s pools from %s registries and %s factories', len(self.curve.token_to_pool), len(self.curve.registries), len(self.curve.factories))
            self.curve._done.set()

class Registry(_CurveEventsLoader):
    __slots__ = "_events"
    def __init__(self, address: Address, curve: "CurveRegistry", asynchronous: bool = False):
        super().__init__(address, curve, asynchronous=asynchronous)
        self._events = RegistryEvents(self)
    def __await__(self):
        return self.loaded.__await__()

class Factory(_CurveLoader):
    def __await__(self):
        return self.loaded.__await__()
    @property
    def loaded(self) -> Awaitable[T]:
        if self._loaded is None:
            self._task  # ensure task is running
            self._loaded = a_sync.Event(name=f"curve factory {self.address}")
        return self._loaded.wait()
    async def get_pool(self, i: int) -> EthAddress:
        return await self.contract.pool_list.coroutine(i)
    async def pool_count(self, block: Optional[int] = None) -> int:
        return await self.contract.pool_count.coroutine(block_identifier=block)
    async def read_pools(self) -> List[EthAddress]:
        try:
            # lets load the contract async and then we can use the sync property more conveniently
            await Contract.coroutine(self.address)
        except ContractNotVerified:
            if chain.id == Network.xDai:
                Contract.from_abi("Vyper_contract", self.address, CURVE_REGISTRY_ABI)
            else:
                # This happens sometimes, not sure why as the contract is verified.
                brownie.Contract.from_explorer(self.address)
        return await asyncio.gather(*[self.get_pool(i) for i in range(await self.pool_count())])
    async def _load(self) -> None:
        pool_list = await self.read_pools(sync=False)
        await asyncio.gather(*[self._load_pool(pool) for pool in pool_list if pool not in self.curve.factories[self.address]])
        logger.debug("loaded %s pools for %s", len(pool_list), self)
        self._loaded.set()
    async def _load_pool(self, pool: Address) -> None:
        factory = await Contract.coroutine(self.address)
        # for curve v5 pools, pool and lp token are separate
        if hasattr(factory, 'get_token'):
            lp_token = await factory.get_token.coroutine(pool)
        elif hasattr(factory, 'get_lp_token'):
            lp_token = await factory.get_lp_token.coroutine(pool)
        else:
            raise NotImplementedError(f"New factory {factory.address} is not yet supported. Please notify a ypricemagic maintainer.")
        self.curve.token_to_pool[lp_token] = pool
        self.curve.factories[factory.address].add(pool)
        logger.debug("loaded %s pool %s", self, pool)
        


class CurvePool(ERC20): # this shouldn't be ERC20 but works for inheritance for now
    @a_sync.aka.cached_property
    async def factory(self) -> Contract:
        return await curve.get_factory(self, sync=False)

    @a_sync.aka.cached_property
    async def coins(self) -> List[ERC20]:
        """
        Get coins of pool.
        """
        factory = await self.__factory__(sync=False)
        if factory:
            coins = await factory.get_coins.coroutine(self.address)
        else:
            registry = await curve.__registry__(sync=False)
            coins = await registry.get_coins.coroutine(self.address)
        
        # pool not in registry
        if set(coins) == {ZERO_ADDRESS}:
            coins = await multicall_same_func_same_contract_different_inputs(
                self.address, 
                'coins(uint256)(address)', 
                inputs = [i for i in range(8)],
                return_None_on_failure=True,
                sync=False,
            )

        return [ERC20(coin, asynchronous=self.asynchronous) for coin in coins if coin not in {None, ZERO_ADDRESS}]
    
    @a_sync.a_sync(ram_cache_maxsize=256)
    async def get_coin_index(self, coin: AnyAddressType) -> int:
        return [i for i, _coin in enumerate(await self.__coins__(sync=False)) if _coin == coin][0]
    
    @a_sync.aka.cached_property
    async def num_coins(self) -> int:
        return len(await self.__coins__(sync=False))
    
    async def get_dy(self, coin_ix_in: int, coin_ix_out: int, block: Optional[Block] = None, ignore_pools: Tuple[Pool, ...] = ()) -> Optional[WeiBalance]:
        tokens = await self.__coins__(sync=False)
        token_in = tokens[coin_ix_in]
        token_out = tokens[coin_ix_out]
        amount_in = await token_in.__scale__(sync=False)
        try:
            amount_out = await self.contract.get_dy.coroutine(coin_ix_in, coin_ix_out, amount_in, block_identifier=block)
            return WeiBalance(amount_out, token_out, block=block, ignore_pools=(*ignore_pools, self))
        except Exception as e:
            if call_reverted(e):
                return None
            raise
    
    @a_sync.aka.cached_property
    async def coins_decimals(self) -> List[int]:
        factory = await self.__factory__(sync=False)
        source = factory or await curve.registry
        coins_decimals = await source.get_decimals.coroutine(self.address)

        # pool not in registry
        if not any(coins_decimals):
            coins = await self.__coins__(sync=False)
            coins_decimals = await asyncio.gather(*[coin.__decimals__(sync=False) for coin in coins])
        
        return [dec for dec in coins_decimals if dec != 0]
    
    @a_sync.aka.cached_property
    async def get_underlying_coins(self) -> List[ERC20]:    
        factory = await self.__factory__(sync=False)    
        if factory:
            # new factory reverts for non-meta pools
            if not hasattr(factory, 'is_meta') or factory.is_meta(self.address):
                coins = await factory.get_underlying_coins.coroutine(self.address)
            else:
                coins = await factory.get_coins.coroutine(self.address)
        else:
            registry = await curve.registry
            coins = await registry.get_underlying_coins.coroutine(self.address)
        
        # pool not in registry, not checking for underlying_coins here
        if set(coins) == {ZERO_ADDRESS}:
            return await self.__coins__(sync=False)

        return [ERC20(coin, asynchronous=self.asynchronous) for coin in coins if coin != ZERO_ADDRESS]
    
    @a_sync.a_sync(ram_cache_maxsize=1000)
    async def get_balances(self, block: Optional[Block] = None) -> Dict[ERC20, Decimal]:
        """
        Get {token: balance} of liquidity in the pool.
        """

        # TODO figure out why these can't be gathered.
        # Sometimes `self.coins` is a list not a coroutine?
        #coins, decimals = await gather([
        #    self.__coins__(sync=False),
        #    self.__coins_decimals__(sync=False),
        #])

        coins = await self.__coins__(sync=False)
        decimals = await self.__coins_decimals__(sync=False)

        try:
            factory = await self.__factory__(sync=False)
            source = factory or await curve.__registry__(sync=False)
            balances = await source.get_balances.coroutine(self.address, block_identifier=block)
        # fallback for historical queries where registry was not yet deployed
        except ValueError:
            balances = await asyncio.gather(*[self._get_balance(i, block) for i, _ in enumerate(coins)])

        if not any(balances):
            raise ValueError(f'could not fetch balances {self.__str__()} at {block}')

        return {
            coin: Decimal(balance / 10 ** dec)
            for coin, balance, dec in zip(coins, balances, decimals)
            if coin != ZERO_ADDRESS
        }
    
    async def _get_balance(self, i: int, block: Optional[Block] = None) -> Optional[int]:
        try:
            return await self.contract.balances.coroutine(i, block_identifier=block)
        except ValueError as e:
            if str(e) == "No data was returned - the call likely reverted":
                return None
            raise

    async def get_tvl(self, block: Optional[Block] = None) -> Optional[UsdValue]:
        """
        Get total value in Curve pool.
        """
        try:
            balances = await self.get_balances(block=block, sync=False)
        except ValueError as e:
            if str(e).startswith("could not fetch balances "):
                return None
            raise e
        
        prices = await asyncio.gather(*[coin.price(block=block, sync=False) for coin in balances])

        return UsdValue(
            sum(balance * Decimal(price) for balance, price in zip(balances.values(), prices))
        )
    
    @a_sync.a_sync(ram_cache_maxsize=10_000, ram_cache_ttl=10*60)
    async def check_liquidity(self, token: Address, block: Block) -> int:
        deploy_block = await contract_creation_block_async(self.address)
        if block < deploy_block:
            return 0
        i = await self.get_coin_index(token, sync=False)
        return await self._get_balance(i, block)
    
    #@cached_property
    #def oracle(self) -> Optional[Address]:
    #    '''
    #    If `pool` has method `price_oracle`, returns price_oracle address.
    #    Else, returns `None`.
    #    '''
    #    response = raw_call(self.address, 'price_oracle()', output='address', return_None_on_failure=True)
    #    if response == ZERO_ADDRESS:
    #        return None
    #    return response



class CurveRegistry(a_sync.ASyncGenericSingleton):
    __slots__ = "__task", 
    def __init__(self, asynchronous: bool = False) -> None:
        super().__init__()
        self.asynchronous = asynchronous
        try: 
            self.address_provider = AddressProvider(ADDRESS_PROVIDER, self, asynchronous=self.asynchronous)
            self.address_provider.contract
        except (ContractNotFound, ContractNotVerified) as e:
            raise UnsupportedNetwork("curve is not supported on this network") from e
        except MessedUpBrownieContract as e:
            if chain.id == Network.Cronos:
                raise UnsupportedNetwork("curve is not supported on this network") from e
            else:
                raise

        self.registries = defaultdict(set)  # registry -> pools
        self.factories = defaultdict(set)  # factory -> pools
        self.pools = set()
        self.token_to_pool = dict()  # lp_token -> pool
    
    def __repr__(self) -> str:
        return "<CurveRegistry>"

    @property
    def identifiers(self) -> List[EthAddress]:
        return self.address_provider.identifiers
    @a_sync.aka.cached_property
    async def registry(self) -> brownie.Contract:
        try:
            return await Contract.coroutine(self.identifiers[0][-1])
        except IndexError: # if we couldn't get the registry via logs
            return await Contract.coroutine(await raw_call(self.address_provider, 'get_registry()', output='address', sync=False))
    
    async def load_all(self) -> None:
        await self._done.wait()

    async def get_factory(self, pool: AddressOrContract) -> Contract:
        """
        Get metapool factory that has spawned a pool.
        """
        try:
            factory = next(
                factory
                for factory, factory_pools in self.factories.items()
                if str(pool) in factory_pools
            )
            return await Contract.coroutine(factory)
        except StopIteration:
            return None    
    
    @a_sync.a_sync(cache_type='memory')
    async def get_price(self, token: Address, block: Optional[Block] = None) -> Optional[float]:
        pool = await self.get_pool(token, sync=False)
        tvl = await pool.get_tvl(block=block, sync=False)
        if tvl is None:
            return None
        return tvl / await ERC20(token, asynchronous=True).total_supply_readable(block)

    @a_sync.a_sync(cache_type='memory')
    async def get_pool(self, token: AnyAddressType) -> CurvePool:
        """
        Get Curve pool (swap) address by LP token address. Supports factory pools.
        """
        await self.load_all()
        
        token = convert.to_address(token)
        if token in self.token_to_pool and token != ZERO_ADDRESS:
            return CurvePool(self.token_to_pool[token], asynchronous=self.asynchronous)

    @a_sync.a_sync(cache_type='memory')
    async def get_price_for_underlying(self, token_in: Address, block: Optional[Block] = None, ignore_pools: Tuple[Pool, ...] = ()) -> Optional[UsdPrice]:
        try:
            pools: List[CurvePool] = (await self.__coin_to_pools__(sync=False))[token_in]
        except KeyError:
            return None
        
        pools = [pool for pool in pools if pool not in ignore_pools]

        if block is not None:
            deploy_blocks = await asyncio.gather(*[contract_creation_block_async(pool.address, True) for pool in pools])
            pools = [pool for pool, deploy_block in zip(pools, deploy_blocks) if deploy_block <= block]

        # Choose a pool to use for pricing `token_in`.
        if len(pools) == 1:
            pool = pools[0]
        else:
            # Use the pool with deepest liquidity.
            balances = await asyncio.gather(*[pool.check_liquidity(token_in, block=block, sync=False) for pool in pools], return_exceptions=True)
            deepest_pool, deepest_bal = None, 0
            for pool, depth in zip(pools, balances):
                if depth > deepest_bal:
                    deepest_pool = pool
                    deepest_bal = depth
            pool = deepest_pool

        if pool is None:
            return None

        if len(coins := await pool.__coins__(sync=False)) != 2:
            # TODO: handle this sitch if necessary
            return

        # Get the price for `token_in` using the selected pool.
        # this works for most typical metapools

        token_in_ix = await pool.get_coin_index(token_in, sync=False)
        token_out_ix = 0 if token_in_ix == 1 else 1 if token_in_ix == 0 else None
        dy = await pool.get_dy(token_in_ix, token_out_ix, block=block, ignore_pools=ignore_pools, sync=False)
        if dy is None:
            return None

        try:
            return await dy.__value_usd__(sync=False)
        except PriceError as e:
            logger.debug("%s for %s at block %s", e.__class__.__name__, token_in, block)
            return None
    
    @a_sync.aka.cached_property
    async def coin_to_pools(self) -> Dict[str, List[CurvePool]]:
        mapping = defaultdict(set)
        await self.load_all()
        pools = {CurvePool(pool) for pools in self.factories.values() for pool in pools}
        for pool in pools:
            for coin in await pool.__coins__(sync=False):
                mapping[coin].add(pool)
        return {coin: list(pools) for coin, pools in mapping.items()}
    
    async def check_liquidity(self, token: Address, block: Block, ignore_pools: Tuple[Pool, ...]) -> int:
        pools: List[CurvePool] = await self.__coin_to_pools__(sync=False)
        if token not in pools:
            return 0
        if pools := [pool for pool in pools[token] if pool not in ignore_pools]:
            return max(await asyncio.gather(*[pool.check_liquidity(token, block, sync=False) for pool in pools]))
        return 0
    
    @cached_property
    def _done(self) -> a_sync.Event:
        """A helper function to ensure the Event is attached to the correct loop."""
        self._task
        return a_sync.Event(name="curve")
    
    @cached_property
    def _task(self) -> asyncio.Task:
        logger.debug("creating loader task for %s", self)
        task = asyncio.create_task(coro=self._load_all(), name=f"{self}._load_all()")
        def done_callback(t: asyncio.Task):
            if e := t.exception():
                logger.error("exception while loading %s: %s", self, e)
                logger.exception(e)
                self.__task = None
                raise e
        task.add_done_callback(done_callback)
        return task

    async def _load_all(self) -> None:
        await self.address_provider
        logger.debug("curve address provider events loaded, now loading factories and pools")
        # NOTE: Gnosis chain's address provider fails to provide registry via events. Maybe other chains as well.
        if not self.identifiers[Ids.Main_Registry]:
            self.identifiers[Ids.Main_Registry] = [await self.address_provider.get_registry()]
        while True:
            # Check if any registries were updated, then ensure all old and new are loaded
            await asyncio.gather(*[
                Registry(self.identifiers[i][-1], self, asynchronous=self.asynchronous)
                for i in [Ids.Main_Registry, Ids.CryptoSwap_Registry]
                if self.identifiers[i]
            ])
            # load metapool and curve v5 factories
            await self.address_provider._load_factories()
            await asyncio.sleep(600)
   
try: 
    curve = CurveRegistry(asynchronous=True)
except UnsupportedNetwork: 
    curve = set()
