from hashlib import new
import logging
from collections import defaultdict
from functools import lru_cache
from itertools import islice

from brownie import ZERO_ADDRESS, chain
from cachetools.func import ttl_cache
from y.constants import dai
from y.contracts import Contract, Singleton
from y.exceptions import UnsupportedNetwork
from y.networks import Network
from y.utils.middleware import ensure_middleware
from ypricemagic import magic
from ypricemagic.utils.events import create_filter, decode_logs, get_logs_asap
from ypricemagic.utils.multicall import fetch_multicall, multicall_same_func_same_contract_different_inputs
from ypricemagic.utils.raw_calls import _totalSupply, raw_call

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

CURVE_CONTRACTS = {
    Network.Mainnet: {
        'address_provider': ADDRESS_PROVIDER,
        'crv': '0xD533a949740bb3306d119CC777fa900bA034cd52',
        'voting_escrow': '0x5f3b5DfEb7B28CDbD7FAba78963EE202a494e2A2',
        'gauge_controller': '0x2F50D538606Fa9EDD2B11E2446BEb18C9D5846bB',
    },
    Network.Fantom: {
        'address_provider': ADDRESS_PROVIDER,
    },
    Network.Polygon: {
        'address_provider': ADDRESS_PROVIDER,
    },
    Network.Arbitrum: {
        'address_provider': ADDRESS_PROVIDER,
    },
}

OVERRIDES = {
    Network.Mainnet: {
        '0xc4AD29ba4B3c580e6D59105FFf484999997675Ff': '0xd51a44d3fae010294c616388b506acda1bfaae46', # crv3crypto
        "0x3D229E1B4faab62F621eF2F6A610961f7BD7b23B": "0x98a7f18d4e56cfe84e3d081b40001b3d5bd3eb8b", # crvEURSUSDC
        "0x3b6831c0077a1e44ED0a21841C3bC4dC11bCE833": "0x9838eccc42659fa8aa7daf2ad134b53984c9427b", # crvEURTUSD
        "0xEd4064f376cB8d68F770FB1Ff088a3d0F3FF5c4d": "0x8301ae4fc9c624d1d396cbdaa1ed877821d7c511", # crvCRVETH
        "0x3A283D9c08E8b55966afb64C515f5143cf907611": "0xb576491f1e6e5e62f1d8f26062ee822b40b0e0d4", # crvCVXETH
        "0x8484673cA7BfF40F82B041916881aeA15ee84834": "0xadcfcf9894335dc340f6cd182afa45999f45fc44", # crvXAUTUSD
    },
    Network.Fantom: {
        "0x58e57cA18B7A47112b877E31929798Cd3D703b0f": "0x3a1659ddcf2339be3aea159ca010979fb49155ff", # crv3crypto
    }
}.get(chain.id, {})


class CurveRegistry(metaclass=Singleton):
    def __init__(self):
        if chain.id not in CURVE_CONTRACTS:
            raise UnsupportedNetwork("curve is not supported on this network")

        addrs = CURVE_CONTRACTS[chain.id]
        if chain.id == Network.Mainnet:
            self.crv = Contract(addrs['crv'])
            self.voting_escrow = Contract(addrs['voting_escrow'])
            self.gauge_controller = Contract(addrs['gauge_controller'])

        self.pools = set()
        self.identifiers = defaultdict(list)
        self.address_provider = Contract(addrs['address_provider'])
        self.watch_events()

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
            if event.name == 'AddressModified':
                self.identifiers[event['id']].append(event['new_address'])


        # fetch pools from the latest registry
        log_filter = create_filter(str(self.registry))
        new_entries = log_filter.get_new_entries()

        if not len(new_entries):
            new_entries = get_logs_asap(str(self.registry), None)
            
        for event in decode_logs(new_entries):
            if event.name == 'PoolAdded':
                self.pools.add(event['pool'])

        logger.info(f'loaded {len(self.pools)} pools')

    @property
    def registry(self):
        return Contract(self.identifiers[0][-1])

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

    def get_factory(self, pool):
        """
        Get metapool factory that has spawned a pool.
        """
        try:
            return next(
                factory
                for factory, factory_pools in self.metapools_by_factory.items()
                if str(pool) in factory_pools
            )
        except StopIteration:
            return None

    @lru_cache(maxsize=None)
    def _pool_from_lp_token(self, token):
        return self.registry.get_pool_from_lp_token(token)

    def __contains__(self, token):
        return self.get_pool(token) is not None

    @lru_cache(maxsize=None)
    def get_pool(self, token):
        """
        Get Curve pool (swap) address by LP token address. Supports factory pools.
        """
        if self.get_factory(token): return token
            
        if token in OVERRIDES: pool = OVERRIDES[token]

        else: pool = self._pool_from_lp_token(token)

        if pool != ZERO_ADDRESS: return pool
            

    @lru_cache(maxsize=None)
    def get_gauge(self, pool):
        """
        Get liquidity gauge address by pool.
        """
        factory = self.get_factory(pool)
        if factory and hasattr(Contract(factory), 'get_gauge'):
            gauge = Contract(factory).get_gauge(pool)
            if gauge != ZERO_ADDRESS:
                return gauge

        gauges, types = self.registry.get_gauges(pool)
        if gauges[0] != ZERO_ADDRESS:
            return gauges[0]

    @lru_cache(maxsize=None)
    def get_coins(self, pool):
        """
        Get coins of pool.
        """
        factory = self.get_factory(pool)

        if factory:
            coins = Contract(factory).get_coins(pool)
        else:
            coins = self.registry.get_coins(pool)
        
        # pool not in registry
        if set(coins) == {ZERO_ADDRESS}:
            coins = multicall_same_func_same_contract_different_inputs(
                pool, 
                'coins(uint256)(address)', 
                inputs = [i for i in range(8)],
                return_None_on_failure=True
                )

        return [coin for coin in coins if coin not in {None, ZERO_ADDRESS}]

    @lru_cache(maxsize=None)
    def get_underlying_coins(self, pool):
        factory = self.get_factory(pool)
        
        if factory:
            factory = Contract(factory)
            # new factory reverts for non-meta pools
            if not hasattr(factory, 'is_meta') or factory.is_meta(pool):
                coins = factory.get_underlying_coins(pool)
            else:
                coins = factory.get_coins(pool)
        else:
            coins = self.registry.get_underlying_coins(pool)
        
        # pool not in registry, not checking for underlying_coins here
        if set(coins) == {ZERO_ADDRESS}:
            return self.get_coins(pool)

        return [coin for coin in coins if coin != ZERO_ADDRESS]

    @lru_cache(maxsize=None)
    def get_decimals(self, pool):
        factory = self.get_factory(pool)
        source = Contract(factory) if factory else self.registry
        decimals = source.get_decimals(pool)

        # pool not in registry
        if not any(decimals):
            coins = self.get_coins(pool)
            decimals = fetch_multicall(
                *[[Contract(token), 'decimals'] for token in coins]
            )
        
        return [dec for dec in decimals if dec != 0]

    def get_balances(self, pool, block=None):
        """
        Get {token: balance} of liquidity in the pool.
        """
        factory = self.get_factory(pool)
        coins = self.get_coins(pool)
        decimals = self.get_decimals(pool)

        try:
            source = Contract(factory) if factory else self.registry
            balances = source.get_balances(pool, block_identifier=block)
        # fallback for historical queries
        except ValueError:
            balances = fetch_multicall(
                *[[Contract(pool), 'balances', i] for i, _ in enumerate(coins)]
            )

        if not any(balances):
            raise ValueError(f'could not fetch balances {pool} at {block}')

        return {
            coin: balance / 10 ** dec
            for coin, balance, dec in zip(coins, balances, decimals)
            if coin != ZERO_ADDRESS
        }

    def get_tvl(self, pool, block=None):
        """
        Get total value in Curve pool.
        """
        balances = self.get_balances(pool, block=block)
        if balances is None:
            return None

        return sum(
            balances[coin] * magic.get_price(coin, block=block) for coin in balances
        )

    @ttl_cache(maxsize=None, ttl=600)
    def get_price(self, token, block=None):
        pool = self.get_pool(token)

        # crypto pools can have different tokens, use slow method
        if self.has_oracle(pool):
            tvl = self.get_tvl(pool, block=block)
            if tvl is None:
                return None
            supply = _totalSupply(token, block) / 1e18
            price = tvl / supply
            logger.debug("curve lp -> %s", price)
            return price

        # approximate by using the most common base token we find
        coins = self.get_underlying_coins(pool)
        try:
            coin = (set(coins) & BASIC_TOKENS).pop()
        except KeyError:
            coin = coins[0]

        virtual_price = Contract(pool).get_virtual_price(block_identifier=block) / 1e18
        price = virtual_price * magic.get_price(coin, block)
        logger.debug("curve lp -> %s", price)
        return price

    def calculate_boost(self, gauge, addr, block=None):
        results = fetch_multicall(
            [gauge, "balanceOf", addr],
            [gauge, "totalSupply"],
            [gauge, "working_balances", addr],
            [gauge, "working_supply"],
            [self.voting_escrow, "balanceOf", addr],
            [self.voting_escrow, "totalSupply"],
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

    def calculate_apy(self, gauge, lp_token, block=None):
        crv_price = magic.get_price(self.crv)
        pool = Contract(self.get_pool(lp_token))
        results = fetch_multicall(
            [gauge, "working_supply"],
            [self.gauge_controller, "gauge_relative_weight", gauge],
            [gauge, "inflation_rate"],
            [pool, "get_virtual_price"],
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
    
    def has_oracle(self, pool):
        try: return raw_call(pool,'price_oracle()')
        except ValueError as e:
            if 'execution reverted' in str(e): return False
            else: raise


curve = None
try:
    curve = CurveRegistry()
except UnsupportedNetwork:
    pass
