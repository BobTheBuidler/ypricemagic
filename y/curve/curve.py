import logging
from collections import defaultdict
from functools import cached_property, lru_cache
from itertools import islice
from typing import Dict, List

from brownie import ZERO_ADDRESS, chain
from brownie.exceptions import ContractNotFound
from cachetools.func import ttl_cache
from y.classes.common import ERC20
from y.classes.singleton import Singleton
from y.constants import dai
from y.contracts import Contract
from y.curve.pool import CurvePool
from y.decorators import log
from y.exceptions import (ContractNotVerified, MessedUpBrownieContract,
                          PriceError, UnsupportedNetwork, call_reverted)
from y.networks import Network
from y.utils.events import create_filter, decode_logs, get_logs_asap
from y.utils.middleware import ensure_middleware
from y.utils.multicall import fetch_multicall
from y.utils.raw_calls import raw_call

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


class CurveRegistry(metaclass=Singleton):
    def __init__(self):
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

    def watch_events(self):
        # TODO keep fresh in background

        # fetch all registries and factories from address provider
        log_filter = create_filter(str(self.address_provider))
        new_entries = log_filter.get_new_entries()

        if not len(new_entries): # if your setup is unable to correctly utilize filters
            new_entries = get_logs_asap(str(self.address_provider), None)

        for event in decode_logs(new_entries):
            if event.name == 'NewAddressIdentifier':
                self.identifiers[event['id']].append(event['addr'])
            elif event.name == 'AddressModified':
                self.identifiers[event['id']].append(event['new_address'])

        self.pools = {pool for pools in self.metapools_by_factory.values() for pool in pools}

        # fetch pools from the latest registry
        log_filter = create_filter(str(self.registry))
        new_entries = log_filter.get_new_entries()
        
        if not len(new_entries): # if your setup is unable to correctly utilize filters
            new_entries = get_logs_asap(str(self.registry), None)

        for event in decode_logs(new_entries):
            if event.name == 'PoolAdded':
                self.pools.add(event['pool'])
        
        logger.info(f'loaded {len(self.pools)} pools')

    @property
    @log(logger)
    def registry(self):
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

    @log(logger)
    def get_factory(self, pool: str) -> Contract:
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

    @log(logger)
    @lru_cache(maxsize=None)
    def _pool_from_lp_token(self, token: str) -> str:
        return self.registry.get_pool_from_lp_token(token)

    @log(logger)
    def __contains__(self, token: str) -> bool:
        return self.get_pool(token) is not None
    
    @log(logger)
    @ttl_cache(maxsize=None, ttl=600)
    def get_price(self, token: str, block: int = None) -> float:
        tvl = self.get_pool(token).get_tvl(block=block)
        if tvl is None: return None
        return tvl / ERC20(token).total_supply_readable(block)

    @log(logger)
    @lru_cache(maxsize=None)
    def get_pool(self, token: str) -> CurvePool:
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

    @log(logger)
    def virtual_price(self, token: str, block: int = None) -> int:
        pool = self.get_pool(token)
        try: return pool.contract.get_virtual_price(block_identifier=block)
        except Exception as e:
            if call_reverted(e): return False
            else: raise

    @log(logger)
    def virtual_price_readable(self, token: str, block: int = None) -> float:
        virtual_price = self.virtual_price(token, block)
        if virtual_price is None: return None
        return virtual_price / 1e18

    @log(logger)
    def get_price_for_underlying(self, token_in: str, block: int = None) -> float:
        try:
            pools = self.coin_to_pools[token_in]
        except KeyError:
            return None

        if len(pools) == 1:
            pool = pools[0]
        else:
            # TODO: handle this sitch
            return
            #for pool in self.coin_to_pools[token_in]:
            #    for stable in STABLECOINS:
            #        if stable != token_in and stable in pool.get_coins:
            #            pool = pool
        
        if len(pool.get_coins) == 2:
            # this works for most typical metapools
            token_in_ix = pool.get_coin_index(token_in)
            token_out_ix = 0 if token_in_ix == 1 else 1 if token_in_ix == 0 else None
            dy = pool.get_dy(token_in_ix, token_out_ix, block = block)
            if dy is None:
                return None
            try:
                return dy.value_usd()
            except (PriceError,RecursionError): # TODO handle this case better
                return None
        else:
            # TODO: handle this sitch if necessary
            return


    @cached_property
    def coin_to_pools(self) -> Dict[str, List[CurvePool]]:
        mapping = defaultdict(set)
        pools = {CurvePool(pool) for pools in self.metapools_by_factory.values() for pool in pools}
        for pool in pools:
            for coin in pool.get_coins:
                mapping[coin].add(pool)
        return {coin: list(pools) for coin, pools in mapping.items()}

try: curve = CurveRegistry()
except UnsupportedNetwork: curve = set()
