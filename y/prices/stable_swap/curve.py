
import asyncio
import logging
from collections import defaultdict
from decimal import Decimal
from enum import IntEnum
from functools import cached_property
from typing import Dict, List, Optional, Tuple, TypeVar

import a_sync
import brownie
from a_sync.a_sync import HiddenMethodDescriptor
from brownie import ZERO_ADDRESS, chain
from brownie.convert.datatypes import EthAddress
from brownie.exceptions import ContractNotFound, EventLookupError
from brownie.network.event import _EventItem
from typing_extensions import Self
from web3.exceptions import ContractLogicError

from y import ENVIRONMENT_VARIABLES as ENVS
from y import convert
from y.classes.common import ERC20, WeiBalance, _EventsLoader, _Loader
from y.contracts import Contract, contract_creation_block_async
from y.datatypes import (Address, AddressOrContract, AnyAddressType, Block,
                         Pool, UsdPrice, UsdValue)
from y.exceptions import (ContractNotVerified, MessedUpBrownieContract,
                          PriceError, UnsupportedNetwork, call_reverted)
from y.interfaces.curve.CurveRegistry import CURVE_REGISTRY_ABI
from y.networks import Network
from y.utils import a_sync_ttl_cache
from y.utils.events import ProcessedEvents
from y.utils.multicall import \
    multicall_same_func_same_contract_different_inputs
from y.utils.raw_calls import raw_call

T = TypeVar('T')

logger = logging.getLogger(__name__)

# curve registry documentation https://curve.readthedocs.io/registry-address-provider.html
ADDRESS_PROVIDER = '0x0000000022D53366457F9d5E68Ec105046FC4383'
"Curve's address provider contract on all chains."

DED_POOLS = {
    Network.Mainnet: {
        "0x8301AE4fc9c624d1D396cbDAa1ed877821D7C511": "0xEd4064f376cB8d68F770FB1Ff088a3d0F3FF5c4d",
    },
}.get(chain.id, {})
"The on chain registry no longer returns the lp token address for these dead pools, so we need to provide it manually."

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
    CurveStableswapFactoryNG = 12


_LT = TypeVar("_LT", bound=_Loader)

class _CurveEventsLoader(_EventsLoader):
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
            try:
                pool = event['pool']
            except EventLookupError:
                pool = event['newPool']
            self._tasks.append(asyncio.create_task(coro=self._add_pool(pool), name=f"Registry._add_pool for pool {pool}"))
            curve.registries[event.address].add(pool)
        elif event.name == 'PoolRemoved':
            curve.registries[event.address].discard(event['pool'])
        logger.debug("%s loaded event %s at block %s", self, event, event.block_number)
        return event
    async def _add_pool(self, pool: Address) -> EthAddress:
        if pool in DED_POOLS:
            # The on chain registry no longer returns the lp token address for these dead pools, so we need to provide it manually.
            lp_token = DED_POOLS[pool]
        else:
            lp_token = await self.registry.contract.get_lp_token.coroutine(pool)
        curve.token_to_pool[lp_token] = pool
    async def _set_lock(self, block: int) -> None:
        await asyncio.gather(*self._tasks)
        self._tasks.clear()
        self._lock.set(block)



class AddressProvider(_CurveEventsLoader):
    __slots__ = "identifiers", "_events", 
    def __init__(self, address: Address, asynchronous: bool = False):
        super().__init__(address, asynchronous=asynchronous)
        self.identifiers = defaultdict(list)
        self._events = AddressProviderEvents(self)
    async def get_registry(self) -> EthAddress:
        contract = await Contract.coroutine(self.address)
        return await contract.get_registry
    async def _load_factories(self) -> None:
        # factory events are quite useless, so we use a different method
        logger.debug("loading pools from metapool factories")
        # TODO: remove this once curve adds to address provider
        if chain.id == Network.Mainnet:
            self.identifiers[Ids.CurveStableswapFactoryNG] = ['0x6A8cbed756804B16E05E741eDaBd5cB544AE21bf']

        if metapool_factories := [
            Factory(factory, asynchronous=self.asynchronous)
            for i in [Ids.Metapool_Factory, Ids.crvUSD_Plain_Pools, Ids.Curve_Tricrypto_Factory, Ids.CurveStableswapFactoryNG]
            for factory in self.identifiers[i]
        ]:
            async for factory, pool_list in a_sync.map(Factory.read_pools, metapool_factories):
                for pool in pool_list:
                    # for metpool factories pool is the same as lp token
                    curve.token_to_pool[pool] = pool
                    curve.factories[factory].add(pool)

        # if there are factories that haven't yet been added to the on-chain address provider,
        # please refer to commit 3f70c4246615017d87602e03272b3ed18d594d3c to see how to add them manually
        if identifiers := self.identifiers[Ids.CryptoPool_Factory] + self.identifiers[Ids.Cryptopool_Factory]:
            logger.debug("loading pools from cryptopool factories")
            await a_sync.map(Factory, identifiers, asynchronous=self.asynchronous)

        if not curve._done.is_set():
            logger.info('loaded %s pools from %s registries and %s factories', len(curve.token_to_pool), len(curve.registries), len(curve.factories))
            curve._done.set()

class Registry(_CurveEventsLoader):
    __slots__ = "_events"
    def __init__(self, address: Address, curve: "CurveRegistry", asynchronous: bool = False):
        super().__init__(address, asynchronous=asynchronous)
        self._events = RegistryEvents(self)

class Factory(_Loader):
    async def get_pool(self, i: int) -> EthAddress:
        contract = await Contract.coroutine(self.address)
        return await contract.pool_list.coroutine(i)
    async def pool_count(self, block: Optional[int] = None) -> int:
        contract = await Contract.coroutine(self.address)
        return await contract.pool_count.coroutine(block_identifier=block)
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
        pool_count = await self.pool_count()
        return await a_sync.map(self.get_pool, range(pool_count)).values(pop=True)
    async def _load(self) -> None:
        pool_list = await self.read_pools(sync=False)
        await asyncio.gather(*[self._load_pool(pool) for pool in pool_list if pool not in curve.factories[self.address]])
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
        curve.token_to_pool[lp_token] = pool
        curve.factories[factory.address].add(pool)
        logger.debug("loaded %s pool %s", self, pool)
        


class CurvePool(ERC20): # this shouldn't be ERC20 but works for inheritance for now
    @a_sync.aka.cached_property
    async def factory(self) -> Contract:
        return await curve.get_factory(self, sync=False)
    __factory__: HiddenMethodDescriptor[Self, Contract]
    @a_sync.aka.cached_property
    async def coins(self) -> List[ERC20]:
        """
        Get coins of pool.
        """
        factory = await self.__factory__
        if factory:
            coins = await factory.get_coins.coroutine(self.address)
        else:
            registry = await curve.__registry__
            coins = await registry.get_coins.coroutine(self.address)

        # pool not in registry
        if set(coins) == {ZERO_ADDRESS}:
            coins = await multicall_same_func_same_contract_different_inputs(
                self.address,
                'coins(uint256)(address)',
                inputs=list(range(8)),
                return_None_on_failure=True,
                sync=False,
            )

        return [ERC20(coin, asynchronous=self.asynchronous) for coin in coins if coin not in {None, ZERO_ADDRESS}]
    __coins__: HiddenMethodDescriptor[Self, List[ERC20]]

    @a_sync.a_sync(ram_cache_maxsize=256)
    async def get_coin_index(self, coin: AnyAddressType) -> int:
        return [i for i, _coin in enumerate(await self.__coins__) if _coin == coin][0]
    
    @a_sync.aka.cached_property
    async def num_coins(self) -> int:
        return len(await self.__coins__)
    __num_coins__: HiddenMethodDescriptor[Self, int]
    
    async def get_dy(
        self, 
        coin_ix_in: int, 
        coin_ix_out: int, 
        block: Optional[Block] = None, 
        ignore_pools: Tuple[Pool, ...] = (),
        skip_cache: bool = ENVS.SKIP_CACHE,
    ) -> Optional[WeiBalance]:
        tokens = await self.__coins__
        token_in: ERC20 = tokens[coin_ix_in]
        token_out: ERC20 = tokens[coin_ix_out]
        amount_in = await token_in.__scale__
        contract = await Contract.coroutine(self.address)
        try:
            amount_out = await contract.get_dy.coroutine(coin_ix_in, coin_ix_out, amount_in, block_identifier=block)
            return WeiBalance(amount_out, token_out, block=block, ignore_pools=(*ignore_pools, self), skip_cache=skip_cache)
        except Exception as e:
            if call_reverted(e):
                return None
            raise
    
    @a_sync.aka.cached_property
    async def coins_decimals(self) -> List[int]:
        factory = await self.__factory__
        source = factory or await curve.registry
        coins_decimals = await source.get_decimals.coroutine(self.address)

        # pool not in registry
        if not any(coins_decimals):
            coins_decimals = await a_sync.map(ERC20.decimals, await self.__coins__).values(pop=True)
        
        return [dec for dec in coins_decimals if dec != 0]
    __coins_decimals__: HiddenMethodDescriptor[Self, List[int]]

    @a_sync.aka.cached_property
    async def get_underlying_coins(self) -> List[ERC20]:    
        factory = await self.__factory__    
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
            return await self.__coins__

        return [ERC20(coin, asynchronous=self.asynchronous) for coin in coins if coin != ZERO_ADDRESS]
    __get_underlying_coins__: HiddenMethodDescriptor[Self, List[ERC20]]
    
    @a_sync.a_sync(ram_cache_maxsize=1000)
    async def get_balances(self, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE) -> List[WeiBalance]:
        """
        Get {token: balance} of liquidity in the pool.
        """
        coins = await self.__coins__
        try:
            factory = await self.__factory__
            source = factory or await curve.__registry__
            balances = await source.get_balances.coroutine(self.address, block_identifier=block)
        except (ContractLogicError, ValueError):
            # ContractLogicError in web3>=6.0, ValueError in <6.0
            # fallback for historical queries where registry was not yet deployed
            balances = await a_sync.map(self._get_balance, range(len(coins)), block=block).values(pop=True)

        if not any(balances):
            raise ValueError(f'could not fetch balances {self.__str__()} at {block}')

        return [
            WeiBalance(balance, coin, block, skip_cache=skip_cache) 
            for coin, balance in zip(coins, balances) 
            if coin != ZERO_ADDRESS
        ]
    
    async def _get_balance(self, i: int, block: Optional[Block] = None) -> Optional[int]:
        try:
            contract = await Contract.coroutine(self.address)
        except ContractNotVerified:
            # TODO: figure out if we need to build this, usually they get verified quickly 
            return None
        try:
            return await contract.balances.coroutine(i, block_identifier=block)
        except ContractLogicError as e:
            # happens on web3py>=6.0
            if str(e) == "execution reverted":
                return None
            raise
        except ValueError as e:
            # happens on web3py<6.0
            if str(e) == "No data was returned - the call likely reverted":
                return None
            raise

    async def get_tvl(self, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE) -> Optional[UsdValue]:
        """
        Get total value in Curve pool.
        """
        try:
            price = await WeiBalance.value_usd.sum(
                self.get_balances(block=block, skip_cache=skip_cache, sync=False), 
                sync=False,
            )
            return UsdValue(price)
        except ValueError as e:
            if str(e).startswith("could not fetch balances "):
                return None
            raise
    
    @a_sync.a_sync(ram_cache_maxsize=100_000, ram_cache_ttl=60*60)
    async def check_liquidity(self, token: Address, block: Block) -> int:
        if block < await contract_creation_block_async(self.address):
            return 0
        index = await self.get_coin_index(token, sync=False)
        if balance := await self._get_balance(index, block):
            return balance
        return 0



class CurveRegistry(a_sync.ASyncGenericSingleton):
    __slots__ = "__task", 
    def __init__(self, asynchronous: bool = False) -> None:
        super().__init__()
        self.asynchronous = asynchronous
        try: 
            self.address_provider = AddressProvider(ADDRESS_PROVIDER, asynchronous=self.asynchronous)
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
    async def registry(self) -> Contract:
        try:
            return await Contract.coroutine(self.identifiers[0][-1])
        except IndexError: # if we couldn't get the registry via logs
            return await Contract.coroutine(await raw_call(self.address_provider, 'get_registry()', output='address', sync=False))
    __registry__: HiddenMethodDescriptor[Self, Contract]

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
    
    @a_sync_ttl_cache
    async def get_price(self, token: Address, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE) -> Optional[float]:
        pool: CurvePool = await self.get_pool(token, sync=False)
        if pool is None:
            return None
        tvl = await pool.get_tvl(block=block, skip_cache=skip_cache, sync=False)
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
    async def get_price_for_underlying(
        self, 
        token_in: Address, 
        block: Optional[Block] = None, 
        ignore_pools: Tuple[Pool, ...] = (),
        skip_cache: bool = ENVS.SKIP_CACHE,
    ) -> Optional[UsdPrice]:
        try:
            pools = (await self.__coin_to_pools__)[token_in]
        except KeyError:
            return None
        
        for pool in ignore_pools:
            try:
                pools.remove(pool)
            except ValueError:
                continue

        if pools and block is not None:
            pools = [
                pool 
                async for pool, deploy_block 
                in CurvePool.deploy_block.map(pools, when_no_history_return_0=True) 
                if deploy_block <= block
            ]

        if not pools:
            return None
        # Choose a pool to use for pricing `token_in`.
        elif len(pools) == 1:
            pool = pools[0]
        else:
            # Use the pool with deepest liquidity.
            deepest_pool, deepest_bal = None, 0
            async for pool, depth in CurvePool.check_liquidity.map(pools, token=token_in, block=block).map():
                if depth > deepest_bal:
                    deepest_pool = pool
                    deepest_bal = depth
            pool = deepest_pool

        if pool is None:
            return None

        if len(await pool.__coins__) != 2:
            # TODO: handle this sitch if necessary
            return

        # Get the price for `token_in` using the selected pool.
        # this works for most typical metapools

        token_in_ix = await pool.get_coin_index(token_in, sync=False)
        token_out_ix = 0 if token_in_ix == 1 else 1 if token_in_ix == 0 else None
        dy: Optional[WeiBalance] = await pool.get_dy(token_in_ix, token_out_ix, block=block, ignore_pools=ignore_pools, skip_cache=skip_cache, sync=False)
        if dy is None:
            return None

        try:
            return await dy.__value_usd__
        except PriceError as e:
            logger.debug("%s for %s at block %s", e.__class__.__name__, token_in, block)
            return None
    
    @a_sync.aka.cached_property
    async def coin_to_pools(self) -> Dict[str, List[CurvePool]]:
        mapping = defaultdict(set)
        await self.load_all()
        for pool in {CurvePool(pool) for pools in self.factories.values() for pool in pools}:
            for coin in await pool.__coins__:
                mapping[coin].add(pool)
        return {coin: list(pools) for coin, pools in mapping.items()}
    __coin_to_pools__: HiddenMethodDescriptor[Self, Dict[str, List[CurvePool]]]
    
    async def check_liquidity(self, token: Address, block: Block, ignore_pools: Tuple[Pool, ...]) -> int:
        if pools := [pool for pool in (await self.__coin_to_pools__).get(token, []) if pool not in ignore_pools]:
            return await CurvePool.check_liquidity.max(pools, token=token, block=block, sync=False)
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
        if not self.identifiers[Ids.Main_Registry] and (registry := await self.address_provider.get_registry()) != ZERO_ADDRESS:
            self.identifiers[Ids.Main_Registry] = [registry]
        while True:
            # Check if any registries were updated, then ensure all old and new are loaded
            if registries := [self.identifiers[i][-1] for i in [Ids.Main_Registry, Ids.CryptoSwap_Registry] if self.identifiers[i]]:
                await a_sync.map(Registry, registries, curve=self, asynchronous=self.asynchronous)
            # load metapool and curve v5 factories
            await self.address_provider._load_factories()
            await asyncio.sleep(600)
   
try: 
    curve: CurveRegistry = CurveRegistry(asynchronous=True)
except UnsupportedNetwork: 
    curve = set()
