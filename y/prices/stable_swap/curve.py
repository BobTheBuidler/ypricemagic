import asyncio
import logging
import threading
import time
from collections import defaultdict
from enum import IntEnum
from functools import cached_property, lru_cache
from typing import Any, Dict, List, NoReturn, Optional

import brownie
from async_lru import alru_cache
from async_property import async_cached_property
from brownie import ZERO_ADDRESS, chain
from brownie.convert.datatypes import EthAddress
from brownie.exceptions import ContractNotFound
from cachetools.func import ttl_cache
from multicall.utils import await_awaitable

from y import convert
from y.classes.common import ERC20, WeiBalance
from y.classes.singleton import Singleton
from y.constants import RECURSION_TIMEOUT, log_possible_recursion_err
from y.contracts import Contract, contract_creation_block_async
from y.datatypes import (Address, AddressOrContract, AnyAddressType, Block,
                         UsdPrice, UsdValue)
from y.decorators import event_daemon_task
from y.exceptions import (ContractNotVerified, MessedUpBrownieContract,
                          PriceError, UnsupportedNetwork, call_reverted)
from y.interfaces.curve.CurveRegistry import CURVE_REGISTRY_ABI
from y.networks import Network
from y.utils.dank_mids import dank_w3
from y.utils.events import decode_logs, get_logs_asap_generator
from y.utils.middleware import ensure_middleware
from y.utils.multicall import \
    multicall_same_func_same_contract_different_inputs_async
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
    # On Mainnet, id 7 is listed as "metafactory".
    # On Polygon, id 7 is listed as "cryptopool factory".
    # On other chains, "cryptopool factory" is id 6.
    # On Polygon, id 6 is "crypto factory".
    # I've only seen this on Mainnet and Polygon so far, for now will treat `7` == `6`.
    Cryptopool_Factory = 7


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
            coins_decimals = await asyncio.gather(*[coin.decimals for coin in coins])
        
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

        # TODO figure out why these can't be gathered.
        # Sometimes `self.get_coins_async` is a list not a coroutine?
        #coins, decimals = await gather([
        #    self.get_coins_async,
        #    self.get_coins_decimals_async,
        #])
        coins = await self.get_coins_async
        decimals = await self.get_coins_decimals_async

        try:
            source = self.factory if self.factory else curve.registry
            balances = await source.get_balances.coroutine(self.address, block_identifier=block)
        # fallback for historical queries where registry was not yet deployed
        except ValueError:
            balances = await asyncio.gather(*[self._get_balance(i, block) for i, _ in enumerate(coins)])

        if not any(balances):
            raise ValueError(f'could not fetch balances {self.__str__()} at {block}')

        return {
            coin: balance / 10 ** dec
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
        
        prices = await asyncio.gather(*[coin.price_async(block=block) for coin in balances])

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

        self._address_providers_loading = asyncio.Event()
        self._address_providers_loaded = threading.Event()
        self._registries_loaded = threading.Event()
        self._loaded_registries = set()
        self._all_loading = threading.Event()
        self._all_loaded = threading.Event()
    
    def __repr__(self) -> str:
        return "<CurveRegistry>"
    
    def _load_address_provider_event(self, event) -> None:
        if event.name == 'NewAddressIdentifier':
            self.identifiers[Ids(event['id'])].append(event['addr'])
        elif event.name == 'AddressModified':
            self.identifiers[Ids(event['id'])].append(event['new_address'])

    @event_daemon_task
    async def _load_address_providers(self) -> NoReturn:
        """ Fetch all address providers. """
        if self._address_providers_loading.is_set():
            return
        self._address_providers_loading.set()
        block = await dank_w3.eth.block_number            
        async for logs in get_logs_asap_generator(str(self.address_provider), None, to_block=block, chronological=True):
            for event in decode_logs(logs):
                self._load_address_provider_event(event)
        self._address_providers_loaded.set()

        while await dank_w3.eth.block_number < block+1:
            await asyncio.sleep(15)
            
        async for logs in get_logs_asap_generator(str(self.address_provider), None, from_block=block+1, chronological=True, run_forever=True):
            for event in decode_logs(logs):
                self._load_address_provider_event(event)
    
    async def _load_registry_event(self, registry: Contract, event) -> None:
        if event.name == 'PoolAdded':
            lp_token = await registry.get_lp_token.coroutine(event['pool'])
            self.registries[event.address].add(event['pool'])
            self.token_to_pool[lp_token] = event['pool']
        elif event.name == 'PoolRemoved':
            self.registries[event.address].discard(event['pool'])

    @event_daemon_task
    async def _load_registry(self, registry: Address) -> NoReturn:
        """ Fetch all pools from a particular registry. """ 
        contract, block = await asyncio.gather(Contract.coroutine(registry), dank_w3.eth.block_number)
        async for logs in get_logs_asap_generator(registry, to_block=block, chronological=True):
            for event in decode_logs(logs):
                # Must go one-by-one for chronological order, no gather
                await self._load_registry_event(contract, event)
        self._loaded_registries.add(registry)
        while await dank_w3.eth.block_number < block+1:
            await asyncio.sleep(15)
        async for logs in get_logs_asap_generator(registry, from_block=block+1, chronological=True, run_forever=True):
            for event in decode_logs(logs):
                # Must go one-by-one for chronological order, no gather
                await self._load_registry_event(contract, event)

    @event_daemon_task   
    async def _load_registries(self) -> None:
        if self._all_loading.is_set():
            return
        self._all_loading.set()
        if not self._address_providers_loading.is_set():
            await self._load_address_providers()
        while not self._address_providers_loaded.is_set():
            await asyncio.sleep(0)
        
        known_registries = []
        while True:
            # NOTE: Gnosis chain's address provider fails to provide registry via events. Maybe other chains as well.
            if not self.identifiers[Ids.Main_Registry]:
                self.identifiers[Ids.Main_Registry] = [await self.address_provider.get_registry.coroutine()]
            
            # Check if any registries were updated
            registries = [
                self.identifiers[i][-1]
                for i in [Ids.Main_Registry, Ids.CryptoSwap_Registry]
                if self.identifiers[i]
            ]
            if registries != known_registries:
                # For any updated registries, fetch logs
                await asyncio.gather(*[self._load_registry(registry) for registry in registries if registry not in known_registries])
                known_registries = registries
            
            if not self._registries_loaded.is_set():
                for registry in registries:
                    while registry not in self._loaded_registries:
                        await asyncio.sleep(0)
                self._registries_loaded.set()
            
            # load metapool and curve v5 factories
            await self._load_factories()

            await asyncio.sleep(600)
    
    async def _load_factory_pool(self, factory: Contract, pool: Address) -> None:
        # for curve v5 pools, pool and lp token are separate
        if hasattr(factory, 'get_token'):
            lp_token = await factory.get_token.coroutine(pool)
        elif hasattr(factory, 'get_lp_token'):
            lp_token = await factory.get_lp_token.coroutine(pool)
        else:
            raise NotImplementedError(f"New factory {factory.address} is not yet supported. Please notify a ypricemagic maintainer.")
        self.token_to_pool[lp_token] = pool
        self.factories[factory.address].add(pool)

    async def _load_factory(self, factory: Address) -> None:
        factory_contract, pool_list = await asyncio.gather(
            Contract.coroutine(factory),
            self.read_pools(factory),
        )
        await asyncio.gather(*[self._load_factory_pool(factory_contract, pool) for pool in pool_list if pool not in self.factories[factory]])
            
    
    async def _load_factories(self) -> None:
        # factory events are quite useless, so we use a different method
        metapool_factories = self.identifiers[Ids.Metapool_Factory]
        metapool_factory_pools = await asyncio.gather(*[self.read_pools(factory) for factory in metapool_factories])
        for factory, pool_list in zip(metapool_factories, metapool_factory_pools):
            for pool in pool_list:
                # for metpool factories pool is the same as lp token
                self.token_to_pool[pool] = pool
                self.factories[factory].add(pool)

        # if there are factories that haven't yet been added to the on-chain address provider,
        # please refer to commit 3f70c4246615017d87602e03272b3ed18d594d3c to see how to add them manually
        await asyncio.gather(*[self._load_factory(factory) for factory in self.identifiers[Ids.CryptoPool_Factory] + self.identifiers[Ids.Cryptopool_Factory]])
        if not self._all_loaded.is_set():
            logger.info(f'loaded {len(self.token_to_pool)} pools from {len(self.registries)} registries and {len(self.factories)} factories')
            self._all_loaded.set()
    
    async def load_all(self) -> None:
        if not self._all_loading.is_set():
            await self._load_registries()
        while not self._all_loaded.is_set():
            await asyncio.sleep(0)
    
    async def read_pools(self, registry: Address) -> List[EthAddress]:
        try:
            registry = await Contract.coroutine(registry)
        except ContractNotVerified:
            if chain.id == Network.xDai:
                registry = Contract.from_abi("Vyper_contract", registry, CURVE_REGISTRY_ABI)
            else:
                # This happens sometimes, not sure why as the contract is verified.
                registry = brownie.Contract.from_explorer(registry)
        pool_count = await registry.pool_count.coroutine()
        return await asyncio.gather(*[registry.pool_list.coroutine(i) for i in range(pool_count)])

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
    
    @ttl_cache(maxsize=None)
    def get_price(self, token: Address, block: Optional[Block] = None) -> Optional[float]:
        return await_awaitable(self.get_price_async(token, block=block))
    
    #yLazyLogger(logger)
    @alru_cache(maxsize=None)
    async def get_price_async(self, token: Address, block: Optional[Block] = None) -> Optional[float]:
        pool = await self.get_pool(token)
        tvl = await pool.get_tvl_async(block=block)
        if tvl is None:
            return None
        return tvl / await ERC20(token).total_supply_readable_async(block)

    #yLazyLogger(logger)
    @alru_cache(maxsize=None)
    async def get_pool(self, token: AnyAddressType) -> CurvePool:
        """
        Get Curve pool (swap) address by LP token address. Supports factory pools.
        """
        await self.load_all()
        
        token = convert.to_address(token)
        if token in self.token_to_pool and token != ZERO_ADDRESS:
            return CurvePool(self.token_to_pool[token])

    #yLazyLogger(logger)
    @lru_cache(maxsize=None)
    def get_price_for_underlying(self, token_in: Address, block: Optional[Block] = None) -> Optional[UsdPrice]:
        return await_awaitable(self.get_price_for_underlying_async(token_in, block=block))
    
    #yLazyLogger(logger)
    @alru_cache(maxsize=None)
    async def get_price_for_underlying_async(self, token_in: Address, block: Optional[Block] = None) -> Optional[UsdPrice]:
        try:
            pools: List[CurvePool] = (await self.coin_to_pools_async)[token_in]
        except KeyError:
            return None
        
        if block is not None:
            deploy_blocks = await asyncio.gather(*[contract_creation_block_async(pool.address, True) for pool in pools])
            pools = [pool for pool, deploy_block in zip(pools, deploy_blocks) if deploy_block <= block]

        # Choose a pool to use for pricing `token_in`.
        if len(pools) == 1:
            pool = pools[0]
        else:
            # Use the pool with deepest liquidity.
            balances = await asyncio.gather(*[pool.get_balances_async(block=block) for pool in pools], return_exceptions=True)
            deepest_pool, deepest_bal = None, 0
            for pool, pool_bals in zip(pools, balances):
                if isinstance(pool_bals, Exception):
                    if str(pool_bals).startswith("could not fetch balances"):
                        continue
                    raise pool_bals
                for token, bal in pool_bals.items():
                    if token == token_in and bal > deepest_bal:
                        deepest_pool = pool
                        deepest_bal = bal
            pool = deepest_pool
        
        if pool is None:
            return None
        
        # Get the price for `token_in` using the selected pool.
        if len(coins := await pool.get_coins_async) == 2:
            # this works for most typical metapools
            from y.prices.utils.buckets import check_bucket_async

            token_in_ix = await pool.get_coin_index_async(token_in)
            token_out_ix = 0 if token_in_ix == 1 else 1 if token_in_ix == 0 else None
            dy = await pool.get_dy_async(token_in_ix, token_out_ix, block = block)
            if dy is None:
                return None
            coro = dy.value_usd_async
            try:
                token_out = coins[token_out_ix]
                # If we know we won't have issues with recursion, we can await directly.
                if await check_bucket_async(token_out):
                    return await coro
                # We include a timeout here in case we create a recursive loop.
                for p in asyncio.as_completed([coro],timeout=RECURSION_TIMEOUT):
                    log_possible_recursion_err(f"Possible recursion error for {token_in} at block {block}")
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
        await self.load_all()
        pools = {CurvePool(pool) for pools in self.factories.values() for pool in pools}
        for pool in pools:
            for coin in await pool.get_coins_async:
                mapping[coin].add(pool)
        return {coin: list(pools) for coin, pools in mapping.items()}

try: curve = CurveRegistry()
except UnsupportedNetwork: curve = set()
