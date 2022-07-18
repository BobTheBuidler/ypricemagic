import asyncio
import logging
from collections import defaultdict
from functools import cached_property, lru_cache
from itertools import islice
from typing import Any, Dict, List, Optional

import brownie
from async_lru import alru_cache
from async_property import async_cached_property
from brownie import ZERO_ADDRESS, chain
from brownie.exceptions import ContractNotFound
from cachetools.func import ttl_cache
from multicall.utils import await_awaitable, gather
from y.classes.common import ERC20, WeiBalance
from y.classes.singleton import Singleton
from y.constants import dai
from y.contracts import Contract
from y.datatypes import (Address, AddressOrContract, AnyAddressType, Block,
                         UsdPrice, UsdValue)
from y.exceptions import (ContractNotVerified, MessedUpBrownieContract,
                          PriceError, UnsupportedNetwork, call_reverted)
from y.networks import Network
from y.prices import magic
from y.utils.events import create_filter, decode_logs, get_logs_asap
from y.utils.logging import yLazyLogger
from y.utils.middleware import ensure_middleware
from y.utils.multicall import (
    fetch_multicall, multicall_same_func_same_contract_different_inputs_async)
from y.utils.raw_calls import raw_call

logger = logging.getLogger(__name__)

ensure_middleware()

logger = logging.getLogger(__name__)

# curve registry documentation https://curve.readthedocs.io/registry-address-provider.html

ADDRESS_PROVIDER = '0x0000000022D53366457F9d5E68Ec105046FC4383'

# fold underlying tokens into one of the basic tokens

BASIC_TOKENS = {
    Network.Mainnet: {
        dai.address,  # dai
        "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # weth
        "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",  # eth
        "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",  # wbtc
        "0xD71eCFF9342A5Ced620049e616c5035F1dB98620",  # seur
        "0x514910771AF9Ca656af840dff83E8264EcF986CA",  # link
    },
    Network.Polygon: {
        dai.address
    },
    Network.Fantom: {
        dai.address
    }
}.get(chain.id, set())

CURVE_MAINNET_CONTRACTS = {
    'crv': '0xD533a949740bb3306d119CC777fa900bA034cd52',
    'voting_escrow': '0x5f3b5DfEb7B28CDbD7FAba78963EE202a494e2A2',
    'gauge_controller': '0x2F50D538606Fa9EDD2B11E2446BEb18C9D5846bB',
    }

OVERRIDES = {
    Network.Mainnet: {
        '0xc4AD29ba4B3c580e6D59105FFf484999997675Ff': '0xd51a44d3fae010294c616388b506acda1bfaae46', # crv3crypto
        "0x3D229E1B4faab62F621eF2F6A610961f7BD7b23B": "0x98a7f18d4e56cfe84e3d081b40001b3d5bd3eb8b", # crvEURSUSDC
        "0x3b6831c0077a1e44ED0a21841C3bC4dC11bCE833": "0x9838eccc42659fa8aa7daf2ad134b53984c9427b", # crvEURTUSD
        "0xEd4064f376cB8d68F770FB1Ff088a3d0F3FF5c4d": "0x8301ae4fc9c624d1d396cbdaa1ed877821d7c511", # crvCRVETH
        "0x3A283D9c08E8b55966afb64C515f5143cf907611": "0xb576491f1e6e5e62f1d8f26062ee822b40b0e0d4", # crvCVXETH
        "0x8484673cA7BfF40F82B041916881aeA15ee84834": "0xadcfcf9894335dc340f6cd182afa45999f45fc44", # crvXAUTUSD
        "0x8282BD15dcA2EA2bDf24163E8f2781B30C43A2ef": "0x98638FAcf9a3865cd033F36548713183f6996122", # crvSPELLETH
    },
    Network.Polygon: {
        "0x600743B1d8A96438bD46836fD34977a00293f6Aa": "0xb446bf7b8d6d4276d0c75ec0e3ee8dd7fe15783a", # crvEURTUSD
        "0xbece5d20A8a104c54183CC316C8286E3F00ffC71": "0x92577943c7ac4accb35288ab2cc84d75fec330af", # crvUSDBTCETH
    },
    Network.Fantom: {
        "0x58e57cA18B7A47112b877E31929798Cd3D703b0f": "0x3a1659ddcf2339be3aea159ca010979fb49155ff", # crv3crypto
    },
    Network.Arbitrum: {
        "0x3dFe1324A0ee9d86337d06aEB829dEb4528DB9CA": "0xA827a652Ead76c6B0b3D19dba05452E06e25c27e", # crvEURSUSD
    },
    Network.Avalanche: {
        "0x1daB6560494B04473A0BE3E7D83CF3Fdf3a51828": "0xB755B949C126C04e0348DD881a5cF55d424742B2", # crvUSDBTCETH
    }
}.get(chain.id, {})


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
    @yLazyLogger(logger)
    def get_coins(self) -> List[ERC20]:
        return await_awaitable(self.get_coins_async) 
    
    @yLazyLogger(logger)
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
    
    @yLazyLogger(logger)
    def get_coin_index(self, coin: AnyAddressType) -> int:
        return await_awaitable(self.get_coin_index_async(coin))
    
    @yLazyLogger(logger)
    @alru_cache
    async def get_coin_index_async(self, coin: AnyAddressType) -> int:
        return [i for i, _coin in enumerate(await self.get_coins_async) if _coin == coin][0]
    
    @cached_property
    @yLazyLogger(logger)
    def num_coins(self) -> int:
        return len(self.get_coins)
    
    @yLazyLogger(logger)
    def get_dy(self, coin_ix_in: int, coin_ix_out: int, block: Optional[Block] = None) -> Optional[WeiBalance]:
        return await_awaitable(self.get_dy_async(coin_ix_in, coin_ix_out, block=block))
    
    @yLazyLogger(logger)
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
    @yLazyLogger(logger)
    def get_coins_decimals(self) -> List[int]:
        return await_awaitable(self.get_coins_decimals())
    
    @yLazyLogger(logger)
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
    @yLazyLogger(logger)
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
    
    @yLazyLogger(logger)
    @lru_cache(maxsize=None)
    def get_balances(self, block: Optional[Block] = None) -> Dict[ERC20, int]:
        return await_awaitable(self.get_balances_async(block=block)) 
    
    @yLazyLogger(logger)
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
    
    @yLazyLogger(logger)
    def get_tvl(self, block: Optional[Block] = None) -> Optional[UsdValue]:
        """
        Get total value in Curve pool.
        """
        return await_awaitable(self.get_tvl_async(block=block))

    @yLazyLogger(logger)
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
    @yLazyLogger(logger)
    def oracle(self) -> Optional[Address]:
        '''
        If `pool` has method `price_oracle`, returns price_oracle address.
        Else, returns `None`.
        '''
        response = raw_call(self.address, 'price_oracle()', output='address', return_None_on_failure=True)
        if response == ZERO_ADDRESS:
            return None
        return response
    
    @yLazyLogger(logger)
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
    
    @yLazyLogger(logger)
    def calculate_apy(self, lp_token: AnyAddressType, block: Optional[Block] = None) -> Dict[str,float]:
        if not chain.id == Network.Mainnet:
            raise UnsupportedNetwork(f'apy calculations only available on Mainnet')

        crv_price = magic.get_price(curve.crv)
        results = fetch_multicall(
            [self.gauge, "working_supply"],
            [curve.gauge_controller, "gauge_relative_weight", self.gauge],
            [self.gauge, "inflation_rate"],
            [self.contract, "get_virtual_price"],
            block=block,
        )
        results = [x / 1e18 for x in results]
        working_supply, relative_weight, inflation_rate, virtual_price = results
        token_price = magic.get_price(lp_token, block=block)
        try:
            rate = (inflation_rate * relative_weight * 86400 * 365 / working_supply * 0.4) / token_price
        except ZeroDivisionError:
            rate = 0

        return {
            "crv price": crv_price,
            "relative weight": relative_weight,
            "inflation rate": inflation_rate,
            "virtual price": virtual_price,
            "crv reward rate": rate,
            "crv apy": rate * crv_price,
            "token price": token_price,
        }
    
    @yLazyLogger(logger)
    def calculate_boost(self, addr: AddressOrContract, block: Optional[Block] = None) -> Dict[str,float]:
        if not chain.id == Network.Mainnet:
            raise UnsupportedNetwork(f'boost calculations only available on Mainnet')

        results = fetch_multicall(
            [self.gauge, "balanceOf", addr],
            [self.gauge, "totalSupply"],
            [self.gauge, "working_balances", addr],
            [self.gauge, "working_supply"],
            [curve.voting_escrow, "balanceOf", addr],
            [curve.voting_escrow, "totalSupply"],
            block=block,
        )
        results = [x / 1e18 for x in results]
        gauge_balance, gauge_total, working_balance, working_supply, vecrv_balance, vecrv_total = results
        try:
            boost = working_balance / gauge_balance * 2.5
        except ZeroDivisionError:
            boost = 1

        min_vecrv = vecrv_total * gauge_balance / gauge_total
        lim = gauge_balance * 0.4 + gauge_total * min_vecrv / vecrv_total * 0.6
        lim = min(gauge_balance, lim)

        _working_supply = working_supply + lim - working_balance
        noboost_lim = gauge_balance * 0.4
        noboost_supply = working_supply + noboost_lim - working_balance
        try:
            max_boost_possible = (lim / _working_supply) / (noboost_lim / noboost_supply)
        except ZeroDivisionError:
            max_boost_possible = 1

        return {
            "gauge balance": gauge_balance,
            "gauge total": gauge_total,
            "vecrv balance": vecrv_balance,
            "vecrv total": vecrv_total,
            "working balance": working_balance,
            "working total": working_supply,
            "boost": boost,
            "max boost": max_boost_possible,
            "min vecrv": min_vecrv,
        }


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

        if chain.id == Network.Mainnet:
            self.crv = Contract(CURVE_MAINNET_CONTRACTS['crv'])
            self.voting_escrow = Contract(CURVE_MAINNET_CONTRACTS['voting_escrow'])
            self.gauge_controller = Contract(CURVE_MAINNET_CONTRACTS['gauge_controller'])

        self.pools = set()
        self.identifiers = defaultdict(list)
        self.watch_events()
    
    def __repr__(self) -> str:
        return "<CurveRegistry>"

    def watch_events(self) -> None:
        # TODO keep fresh in background

        # fetch all registries and factories from address provider
        try:
            log_filter = create_filter(str(self.address_provider))
            new_entries = log_filter.get_new_entries()
        except: # Some nodes have issues with filters and/or rate limiting
            new_entries = []
        if not new_entries:
            new_entries = get_logs_asap(str(self.address_provider), None)
        
        for event in decode_logs(new_entries):
            if event.name == 'NewAddressIdentifier':
                self.identifiers[event['id']].append(event['addr'])
            elif event.name == 'AddressModified':
                self.identifiers[event['id']].append(event['new_address'])

        self.pools = {pool for pools in self.metapools_by_factory.values() for pool in pools}

        # fetch pools from the latest registry
        try:
            log_filter = create_filter(str(self.registry))
            new_entries = log_filter.get_new_entries()
        except: # Some nodes have issues with filters and/or rate limiting
            new_entries = []
        if not new_entries:
            new_entries = get_logs_asap(str(self.registry), None)

        for event in decode_logs(new_entries):
            if event.name == 'PoolAdded':
                self.pools.add(event['pool'])
        
        logger.info(f'loaded {len(self.pools)} pools')

    @property
    @yLazyLogger(logger)
    def registry(self) -> brownie.Contract:
        try:
            return Contract(self.identifiers[0][-1])
        except IndexError: # if we couldn't get the registry via logs
            return Contract(raw_call(self.address_provider, 'get_registry()', output='address'))

    @property
    @ttl_cache(ttl=3600)
    def metapools_by_factory(self):
        """
        Read cached pools spawned by each factory.
        TODO Update on factory events
        """
        metapool_factories = [Contract(factory) for factory in self.identifiers[3]]
        pool_counts = fetch_multicall(
            *[[factory, 'pool_count'] for factory in metapool_factories]
        )
        pool_lists = iter(
            fetch_multicall(
                *[
                    [factory, 'pool_list', i]
                    for factory, pool_count in zip(metapool_factories, pool_counts)
                    for i in range(pool_count)
                ]
            )
        )
        return {
            str(factory): list(islice(pool_lists, pool_count))
            for factory, pool_count in zip(metapool_factories, pool_counts)
        }

    @yLazyLogger(logger)
    def get_factory(self, pool: AddressOrContract) -> Contract:
        """
        Get metapool factory that has spawned a pool.
        """
        try:
            factory = next(
                factory
                for factory, factory_pools in self.metapools_by_factory.items()
                if str(pool) in factory_pools
            )
            return Contract(factory)
        except StopIteration:
            return None

    @yLazyLogger(logger)
    @lru_cache(maxsize=None)
    def _pool_from_lp_token(self, token: AddressOrContract) -> str:
        return self.registry.get_pool_from_lp_token(token)

    @yLazyLogger(logger)
    def __contains__(self, token: Address) -> bool:
        return self.get_pool(token) is not None
    
    
    @ttl_cache(maxsize=None)
    def get_price(self, token: Address, block: Optional[Block] = None) -> Optional[float]:
        return await_awaitable(self.get_price_async(token, block=block))
    
    @yLazyLogger(logger)
    @alru_cache(maxsize=None)
    async def get_price_async(self, token: Address, block: Optional[Block] = None) -> Optional[float]:
        tvl = await self.get_pool(token).get_tvl_async(block=block)
        if tvl is None:
            return None
        return tvl / await ERC20(token).total_supply_readable_async(block)

    @yLazyLogger(logger)
    @lru_cache(maxsize=None)
    def get_pool(self, token: Address) -> CurvePool:
        """
        Get Curve pool (swap) address by LP token address. Supports factory pools.
        """
        if self.get_factory(token):
            return CurvePool(token)
            
        if token in OVERRIDES:
            pool = OVERRIDES[token]
        else:
            pool = self._pool_from_lp_token(token)

        if pool != ZERO_ADDRESS:
            return CurvePool(pool)

    @yLazyLogger(logger)
    @lru_cache(maxsize=None)
    def get_price_for_underlying(self, token_in: Address, block: Optional[Block] = None) -> Optional[UsdPrice]:
        return await_awaitable(self.get_price_for_underlying_async(token_in, block=block))
    
    @yLazyLogger(logger)
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
        pools = {CurvePool(pool) for pools in self.metapools_by_factory.values() for pool in pools}
        for pool in pools:
            for coin in await pool.get_coins_async:
                mapping[coin].add(pool)
        return {coin: list(pools) for coin, pools in mapping.items()}

try: curve = CurveRegistry()
except UnsupportedNetwork: curve = set()
