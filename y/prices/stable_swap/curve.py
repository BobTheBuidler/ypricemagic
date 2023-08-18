import asyncio
import logging
from collections import defaultdict
from contextlib import suppress
from enum import IntEnum
from typing import Dict, List, NoReturn, Optional

import a_sync
import brownie
from brownie import ZERO_ADDRESS, chain
from brownie.convert.datatypes import EthAddress
from brownie.exceptions import ContractNotFound

from y import convert
from y.classes.common import ERC20, WeiBalance
from y.constants import RECURSION_TIMEOUT, log_possible_recursion_err
from y.contracts import Contract, contract_creation_block_async
from y.datatypes import (Address, AddressOrContract, AnyAddressType, Block,
                         UsdPrice, UsdValue)
from y.exceptions import (ContractNotVerified, MessedUpBrownieContract,
                          PriceError, UnsupportedNetwork, call_reverted)
from y.interfaces.curve.CurveRegistry import CURVE_REGISTRY_ABI
from y.networks import Network
from y.utils.dank_mids import dank_w3
from y.utils.events import decode_logs, get_logs_asap_generator
from y.utils.middleware import ensure_middleware
from y.utils.multicall import \
    multicall_same_func_same_contract_different_inputs
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
    crvUSD_Plain_Pools_deprecated_1 = 8
    crvUSD_Plain_Pools_deprecated_2 = 9
    crvUSD_Plain_Pools = 10
    Curve_Tricrypto_Factory = 11


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
    
    async def get_dy(self, coin_ix_in: int, coin_ix_out: int, block: Optional[Block] = None) -> Optional[WeiBalance]:
        tokens = await self.__coins__(sync=False)
        token_in = tokens[coin_ix_in]
        token_out = tokens[coin_ix_out]
        amount_in = await token_in.__scale__(sync=False)
        try:
            amount_out = await self.contract.get_dy.coroutine(coin_ix_in, coin_ix_out, amount_in, block_identifier=block)
            return WeiBalance(amount_out, token_out, block=block)
        except Exception as e:
            if call_reverted(e):
                return None
            raise
    
    @a_sync.aka.cached_property
    async def coins_decimals(self) -> List[int]:
        factory = await self.__factory__(sync=False)
        source = factory if factory else await curve.registry
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
    async def get_balances(self, block: Optional[Block] = None) -> Dict[ERC20, int]:
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
            source = factory if factory else await curve.__registry__(sync=False)
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
            sum(balance * price for balance, price in zip(balances.values(),prices))
        )
    
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
    def __init__(self, asynchronous: bool = False) -> None:
        super().__init__()
        self.asynchronous = asynchronous
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

        self._address_providers_loading = a_sync.Event()
        self._address_providers_loaded = a_sync.Event()
        self._registries_loaded = a_sync.Event()
        self._loaded_registries = set()
        self._all_loading = a_sync.Event()
        self._all_loaded = a_sync.Event()
    
    def __repr__(self) -> str:
        return "<CurveRegistry>"
    
    def _load_address_provider_event(self, event) -> None:
        if event.name == 'NewAddressIdentifier' and event['addr'] != ZERO_ADDRESS:
            self.identifiers[Ids(event['id'])].append(event['addr'])
        elif event.name == 'AddressModified' and event['new_address'] != ZERO_ADDRESS:
            self.identifiers[Ids(event['id'])].append(event['new_address'])

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

    async def _load_registries(self) -> None:
        if self._all_loading.is_set():
            return
        self._all_loading.set()
        if not self._address_providers_loading.is_set():
            task = asyncio.get_event_loop().create_task(self._load_address_providers())
            def _on_completion(fut):
                if e := fut.exception():
                    self._all_loading.clear()
                    logger.exception(e)
                    raise e
            task.add_done_callback(_on_completion)
        await self._address_providers_loaded.wait()
        
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
                for registry in registries:
                    if registry not in known_registries:
                        asyncio.get_event_loop().create_task(self._load_registry(registry))
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
        metapool_factories = [
            factory 
            for i in [Ids.Metapool_Factory, Ids.crvUSD_Plain_Pools, Ids.Curve_Tricrypto_Factory]
            for factory in self.identifiers[i]
        ]

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
            asyncio.get_event_loop().create_task(self._load_registries())
        await self._all_loaded.wait()
    
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

    @a_sync.aka.cached_property
    async def registry(self) -> brownie.Contract:
        try:
            return await Contract.coroutine(self.identifiers[0][-1])
        except IndexError: # if we couldn't get the registry via logs
            return await Contract.coroutine(await raw_call(self.address_provider, 'get_registry()', output='address', sync=False))

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
    async def get_price_for_underlying(self, token_in: Address, block: Optional[Block] = None) -> Optional[UsdPrice]:
        try:
            pools: List[CurvePool] = (await self.__coin_to_pools__(sync=False))[token_in]
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
            balances = await asyncio.gather(*[pool.get_balances(block=block, sync=False) for pool in pools], return_exceptions=True)
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

        if len(coins := await pool.__coins__(sync=False)) != 2:
            # TODO: handle this sitch if necessary
            return

        # Get the price for `token_in` using the selected pool.
        # this works for most typical metapools

        from y.prices.utils.buckets import check_bucket

        token_in_ix = await pool.get_coin_index(token_in, sync=False)
        token_out_ix = 0 if token_in_ix == 1 else 1 if token_in_ix == 0 else None
        dy = await pool.get_dy(token_in_ix, token_out_ix, block = block, sync=False)
        if dy is None:
            return None

        with suppress(PriceError, asyncio.TimeoutError):
            token_out = coins[token_out_ix]
            # We include a timeout here in case we create a recursive loop.
            log_possible_recursion_err(f"Possible recursion error for {token_in} at block {block}")
            return await asyncio.wait_for(dy.__value_usd__(sync=False), timeout=RECURSION_TIMEOUT)
    
    @a_sync.aka.cached_property
    async def coin_to_pools(self) -> Dict[str, List[CurvePool]]:
        mapping = defaultdict(set)
        await self.load_all()
        pools = {CurvePool(pool) for pools in self.factories.values() for pool in pools}
        for pool in pools:
            for coin in await pool.__coins__(sync=False):
                mapping[coin].add(pool)
        return {coin: list(pools) for coin, pools in mapping.items()}

try: curve = CurveRegistry(asynchronous=True)
except UnsupportedNetwork: curve = set()
