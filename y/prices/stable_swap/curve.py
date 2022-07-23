import asyncio
import logging
import threading
import time
from collections import defaultdict
from enum import IntEnum
from functools import cached_property, lru_cache
from typing import Any, Dict, List, Optional

import brownie
from async_lru import alru_cache
from async_property import async_cached_property
from brownie import ZERO_ADDRESS, chain
from brownie.convert.datatypes import EthAddress
from brownie.exceptions import ContractNotFound
from cachetools.func import ttl_cache
from multicall.utils import await_awaitable, gather
from y import convert
from y.classes.common import ERC20, WeiBalance
from y.classes.singleton import Singleton
from y.contracts import Contract
from y.datatypes import (Address, AddressOrContract, AnyAddressType, Block,
                         UsdPrice, UsdValue)
from y.decorators import wait_or_exit_after
from y.exceptions import (ContractNotVerified, MessedUpBrownieContract,
                          PriceError, UnsupportedNetwork, call_reverted)
from y.networks import Network
from y.utils.events import create_filter, decode_logs, get_logs_asap
from y.utils.logging import yLazyLogger
from y.utils.middleware import ensure_middleware
from y.utils.multicall import (
    fetch_multicall, multicall_same_func_same_contract_different_inputs_async)
from y.utils.raw_calls import raw_call

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


class CurvePool(ERC20): # this shouldn't be ERC20 but works for inheritance for now
    def __init__(self, address: AnyAddressType, *args: Any, **kwargs: Any) -> None:
        super().__init__(address, *args, **kwargs)
    
    def __repr__(self) -> str:
        return f"<CurvePool '{self.address}'>"
    
    @cached_property
    def contract(self) -> Contract:
        return Contract(self.address)
    
    @cached_property
    def factory(self) -> Contract:
        return curve.get_factory(self)

    @cached_property
    #yLazyLogger(logger)
    def get_coins(self) -> List[ERC20]:
        return await_awaitable(self.get_coins_async) 
    
    #yLazyLogger(logger)
    @async_cached_property
    async def get_coins_async(self) -> List[ERC20]:
        """
        Get coins of pool.
        """
        if self.factory:
            coins = self.factory.get_coins(self.address)
        else:
            coins = curve.registry.get_coins(self.address)
        
        # pool not in registry
        if set(coins) == {ZERO_ADDRESS}:
            coins = await multicall_same_func_same_contract_different_inputs_async(
                self.address, 
                'coins(uint256)(address)', 
                inputs = [i for i in range(8)],
                return_None_on_failure=True
                )

        return [ERC20(coin) for coin in coins if coin not in {None, ZERO_ADDRESS}]
    
    #yLazyLogger(logger)
    def get_coin_index(self, coin: AnyAddressType) -> int:
        return await_awaitable(self.get_coin_index_async(coin))
    
    #yLazyLogger(logger)
    @alru_cache
    async def get_coin_index_async(self, coin: AnyAddressType) -> int:
        return [i for i, _coin in enumerate(await self.get_coins_async) if _coin == coin][0]
    
    @cached_property
    #yLazyLogger(logger)
    def num_coins(self) -> int:
        return len(self.get_coins)
    
    #yLazyLogger(logger)
    def get_dy(self, coin_ix_in: int, coin_ix_out: int, block: Optional[Block] = None) -> Optional[WeiBalance]:
        return await_awaitable(self.get_dy_async(coin_ix_in, coin_ix_out, block=block))
    
    #yLazyLogger(logger)
    async def get_dy_async(self, coin_ix_in: int, coin_ix_out: int, block: Optional[Block] = None) -> Optional[WeiBalance]:
        tokens = await self.get_coins_async
        token_in = tokens[coin_ix_in]
        token_out = tokens[coin_ix_out]
        amount_in = await token_in.scale
        try:
            amount_out = await self.contract.get_dy.coroutine(coin_ix_in, coin_ix_out, amount_in, block_identifier=block)
            return WeiBalance(amount_out, token_out, block=block)
        except Exception as e:
            if call_reverted(e):
                return None
            raise
    
    @cached_property
    #yLazyLogger(logger)
    def get_coins_decimals(self) -> List[int]:
        return await_awaitable(self.get_coins_decimals())
    
    #yLazyLogger(logger)
    @async_cached_property
    async def get_coins_decimals_async(self) -> List[int]:
        source = self.factory if self.factory else curve.registry
        coins_decimals = await source.get_decimals.coroutine(self.address)

        # pool not in registry
        if not any(coins_decimals):
            coins = await self.get_coins_async
            coins_decimals = await gather(coin.decimals for coin in coins)
        
        return [dec for dec in coins_decimals if dec != 0]
    
    @cached_property
    #yLazyLogger(logger)
    def get_underlying_coins(self) -> List[ERC20]:        
        if self.factory:
            # new factory reverts for non-meta pools
            if not hasattr(self.factory, 'is_meta') or self.factory.is_meta(self.address):
                coins = self.factory.get_underlying_coins(self.address)
            else:
                coins = self.factory.get_coins(self.address)
        else:
            coins = curve.registry.get_underlying_coins(self.address)
        
        # pool not in registry, not checking for underlying_coins here
        if set(coins) == {ZERO_ADDRESS}:
            return self.get_coins

        return [ERC20(coin) for coin in coins if coin != ZERO_ADDRESS]
    
    #yLazyLogger(logger)
    @lru_cache(maxsize=None)
    def get_balances(self, block: Optional[Block] = None) -> Dict[ERC20, int]:
        return await_awaitable(self.get_balances_async(block=block)) 
    
    #yLazyLogger(logger)
    @alru_cache(maxsize=None)
    async def get_balances_async(self, block: Optional[Block] = None) -> Dict[ERC20, int]:
        """
        Get {token: balance} of liquidity in the pool.
        """
        try:
            source = self.factory if self.factory else curve.registry
            balances = await source.get_balances.coroutine(self.address, block_identifier=block)
        # fallback for historical queries
        except ValueError:
            balances = await multicall_same_func_same_contract_different_inputs_async(
                self.address, 'balances(uint256)(uint256)', inputs = (i for i, _ in enumerate(await self.get_coins_async)), block=block)

        if not any(balances):
            raise ValueError(f'could not fetch balances {self.__str__()} at {block}')

        coins, decimals = await gather([
            self.get_coins_async,
            self.get_coins_decimals_async,
        ])

        return {
            coin: balance / 10 ** dec
            for coin, balance, dec in zip(coins, balances, decimals)
            if coin != ZERO_ADDRESS
        }
    
    #yLazyLogger(logger)
    def get_tvl(self, block: Optional[Block] = None) -> Optional[UsdValue]:
        """
        Get total value in Curve pool.
        """
        return await_awaitable(self.get_tvl_async(block=block))

    #yLazyLogger(logger)
    async def get_tvl_async(self, block: Optional[Block] = None) -> Optional[UsdValue]:
        """
        Get total value in Curve pool.
        """
        balances = await self.get_balances_async(block=block)
        if balances is None:
            return None
        
        prices = await gather([coin.price_async(block=block) for coin in balances.keys()])

        return UsdValue(
            sum(balance * price for balance, price in zip(balances.values(),prices))
        )
    
    @cached_property
    #yLazyLogger(logger)
    def oracle(self) -> Optional[Address]:
        '''
        If `pool` has method `price_oracle`, returns price_oracle address.
        Else, returns `None`.
        '''
        response = raw_call(self.address, 'price_oracle()', output='address', return_None_on_failure=True)
        if response == ZERO_ADDRESS:
            return None
        return response
    
    #yLazyLogger(logger)
    @lru_cache(maxsize=None)
    def gauge(self) -> Optional[brownie.Contract]:
        """
        Get liquidity gauge address by pool.
        """
        if self.factory and hasattr(self.factory, 'get_gauge'):
            gauge = self.factory.get_gauge(self.address)
            if gauge != ZERO_ADDRESS:
                return Contract(gauge)

        gauges, types = curve.registry.get_gauges(self.address)
        if gauges[0] != ZERO_ADDRESS:
            return Contract(gauges[0])
        return None


class CurveRegistry(metaclass=Singleton):
    @wait_or_exit_after
    def __init__(self) -> None:
        try: self.address_provider = Contract(ADDRESS_PROVIDER)
        except (ContractNotFound, ContractNotVerified):
            raise UnsupportedNetwork("curve is not supported on this network")
        except MessedUpBrownieContract:
            if chain.id == Network.Cronos:
                raise UnsupportedNetwork("curve is not supported on this network")
            else:
                raise

        self.identifiers = defaultdict(list)
        self.registries = defaultdict(set)  # registry -> pools
        self.factories = defaultdict(set)  # factory -> pools
        self.pools = set()
        self.token_to_pool = dict()  # lp_token -> pool
        
        self._done = threading.Event()
        self._thread = threading.Thread(target=self.watch_events, daemon=True)
        self._has_exception = False
        self._thread.start()
    
    def __repr__(self) -> str:
        return "<CurveRegistry>"

    def watch_events(self) -> None:
        # fetch all registries and factories from address provider
        try:
            address_provider_filter = create_filter(str(self.address_provider))
            address_provider_logs = address_provider_filter.get_all_entries()
        except: # Some nodes have issues with filters and/or rate limiting
            address_provider_logs = []
        if not address_provider_logs:
            address_provider_logs = get_logs_asap(str(self.address_provider), None)
        
        registries = []
        registries_filter = None
        registry_logs = []
        while True:
            for event in decode_logs(address_provider_logs):
                if event.name == 'NewAddressIdentifier':
                    self.identifiers[Ids(event['id'])].append(event['addr'])
                elif event.name == 'AddressModified':
                    self.identifiers[Ids(event['id'])].append(event['new_address'])

            # NOTE: Gnosis chain's address provider fails to provide registry via events.
            if not self.identifiers[Ids.Main_Registry]:
                self.identifiers[Ids.Main_Registry] = self.address_provider.get_registry()

            # if registries were updated, recreate the filter
            _registries = [
                self.identifiers[i][-1]
                for i in [Ids.Main_Registry, Ids.CryptoSwap_Registry]
                if self.identifiers[i]
            ]
            if _registries != registries:
                registries = _registries
                registries_filter = create_filter(registries)
                registry_logs = registries_filter.get_all_entries()
            
            # fetch pools from the latest registries
            for event in decode_logs(registry_logs):
                if event.name == 'PoolAdded':
                    self.registries[event.address].add(event['pool'])
                    lp_token = Contract(event.address).get_lp_token(event['pool'])
                    self.token_to_pool[lp_token] = event['pool']
                elif event.name == 'PoolRemoved':
                    self.registries[event.address].discard(event['pool'])
            
            # load metapool and curve v5 factories
            self.load_factories()

            if not self._done.is_set():
                self._done.set()
                logger.info(f'loaded {len(self.token_to_pool)} pools from {len(self.registries)} registries and {len(self.factories)} factories')

            time.sleep(600)

            # read new logs at end of loop
            address_provider_logs = address_provider_filter.get_new_entries()
            if registries_filter:
                registry_logs = registries_filter.get_new_entries()
    
    def load_factories(self) -> None:
        # factory events are quite useless, so we use a different method
        for factory in self.identifiers[Ids.Metapool_Factory]:
            pool_list = self.read_pools(factory)
            for pool in pool_list:
                # for metpool factories pool is the same as lp token
                self.token_to_pool[pool] = pool
                self.factories[factory].add(pool)

        # if there are factories that haven't yet been added to the on-chain address provider,
        # please refer to commit 3f70c4246615017d87602e03272b3ed18d594d3c to see how to add them manually
        for factory in self.identifiers[Ids.CryptoPool_Factory]:
            pool_list = self.read_pools(factory)
            for pool in pool_list:
                if pool in self.factories[factory]:
                    continue
                # for curve v5 pools, pool and lp token are separate
                lp_token = Contract(factory).get_token(pool)
                self.token_to_pool[lp_token] = pool
                self.factories[factory].add(pool)
    
    def read_pools(self, registry: Address) -> List[EthAddress]:
        registry = Contract(registry)
        return fetch_multicall(
            *[[registry, 'pool_list', i] for i in range(registry.pool_count())]
        )

    @property
    #yLazyLogger(logger)
    def registry(self) -> brownie.Contract:
        try:
            return Contract(self.identifiers[0][-1])
        except IndexError: # if we couldn't get the registry via logs
            return Contract(raw_call(self.address_provider, 'get_registry()', output='address'))

    #yLazyLogger(logger)
    def get_factory(self, pool: AddressOrContract) -> Contract:
        """
        Get metapool factory that has spawned a pool.
        """
        try:
            factory = next(
                factory
                for factory, factory_pools in self.factories.items()
                if str(pool) in factory_pools
            )
            return Contract(factory)
        except StopIteration:
            return None

    #yLazyLogger(logger)
    def __contains__(self, token: Address) -> bool:
        return self.get_pool(token) is not None
    
    
    @ttl_cache(maxsize=None)
    def get_price(self, token: Address, block: Optional[Block] = None) -> Optional[float]:
        return await_awaitable(self.get_price_async(token, block=block))
    
    #yLazyLogger(logger)
    @alru_cache(maxsize=None)
    async def get_price_async(self, token: Address, block: Optional[Block] = None) -> Optional[float]:
        tvl = await self.get_pool(token).get_tvl_async(block=block)
        if tvl is None:
            return None
        return tvl / await ERC20(token).total_supply_readable_async(block)

    #yLazyLogger(logger)
    @lru_cache(maxsize=None)
    def get_pool(self, token: AnyAddressType) -> CurvePool:
        """
        Get Curve pool (swap) address by LP token address. Supports factory pools.
        """
        token = convert.to_address(token)
        if token in self.token_to_pool:
            return CurvePool(self.token_to_pool[token])

    #yLazyLogger(logger)
    @lru_cache(maxsize=None)
    def get_price_for_underlying(self, token_in: Address, block: Optional[Block] = None) -> Optional[UsdPrice]:
        return await_awaitable(self.get_price_for_underlying_async(token_in, block=block))
    
    #yLazyLogger(logger)
    @alru_cache(maxsize=None)
    async def get_price_for_underlying_async(self, token_in: Address, block: Optional[Block] = None) -> Optional[UsdPrice]:
        try:
            pools = (await self.coin_to_pools_async)[token_in]
        except KeyError:
            return None

        if len(pools) == 1:
            pool = pools[0]
        else:
            # TODO: handle this sitch if/when needed
            return None
            #for pool in self.coin_to_pools[token_in]:
            #    for stable in STABLECOINS:
            #        if stable != token_in and stable in pool.get_coins:
            #            pool = pool
        
        if len(await pool.get_coins_async) == 2:
            # this works for most typical metapools
            token_in_ix = await pool.get_coin_index_async(token_in)
            token_out_ix = 0 if token_in_ix == 1 else 1 if token_in_ix == 0 else None
            dy = await pool.get_dy_async(token_in_ix, token_out_ix, block = block)
            if dy is None:
                return None
            try:
                for p in asyncio.as_completed([dy.value_usd_async],timeout=1):
                    return await p
            except (PriceError, asyncio.TimeoutError):
                return None
        else:
            # TODO: handle this sitch if necessary
            return


    @cached_property
    def coin_to_pools(self) -> Dict[str, List[CurvePool]]:
        return await_awaitable(self.coin_to_pools_async)
    
    @async_cached_property
    async def coin_to_pools_async(self) -> Dict[str, List[CurvePool]]:
        mapping = defaultdict(set)
        pools = {CurvePool(pool) for pools in self.factories.values() for pool in pools}
        for pool in pools:
            for coin in await pool.get_coins_async:
                mapping[coin].add(pool)
        return {coin: list(pools) for coin, pools in mapping.items()}

try: curve = CurveRegistry()
except UnsupportedNetwork: curve = set()
