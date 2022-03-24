
import logging
from functools import cached_property, lru_cache
from typing import Any, Dict, List, Optional

import brownie
from brownie import ZERO_ADDRESS, chain
from y.classes.common import ERC20, WeiBalance
from y.contracts import Contract
from y.datatypes import UsdValue
from y.decorators import log
from y.exceptions import UnsupportedNetwork, call_reverted
from y.networks import Network
from y.prices import magic
from y.typing import Address, Block
from y.utils.multicall import (
    fetch_multicall, multicall_same_func_same_contract_different_inputs)
from y.utils.raw_calls import raw_call

logger = logging.getLogger(__name__)


class CurvePool(ERC20): # this shouldn't be ERC20 but works for inheritance for now
    def __init__(self, address: str, *args: Any, **kwargs: Any) -> None:
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
    @log(logger)
    def get_coins(self) -> List[ERC20]:
        """
        Get coins of pool.
        """
        if self.factory:
            coins = self.factory.get_coins(self.address)
        else:
            coins = curve.registry.get_coins(self.address)
        
        # pool not in registry
        if set(coins) == {ZERO_ADDRESS}:
            coins = multicall_same_func_same_contract_different_inputs(
                self.address, 
                'coins(uint256)(address)', 
                inputs = [i for i in range(8)],
                return_None_on_failure=True
                )

        return [ERC20(coin) for coin in coins if coin not in {None, ZERO_ADDRESS}]
    
    @log(logger)
    @lru_cache
    def get_coin_index(self, coin: str) -> int:
        return [i for i, coin in enumerate(self.get_coins) if coin == coin][0]
    
    @cached_property
    @log(logger)
    def num_coins(self) -> int:
        return len(self.get_coins)
    
    @log(logger)
    def get_dy(self, coin_ix_in: int, coin_ix_out: int, block: Optional[Block] = None) -> Optional[WeiBalance]:
        token_in = self.get_coins[coin_ix_in]
        amount_in = token_in.scale
        try:
            amount_out = self.contract.get_dy.call(coin_ix_in, coin_ix_out, amount_in, block_identifier=block)
            return WeiBalance(amount_out, self.get_coins[coin_ix_out], block=block)
        except Exception as e:
            if call_reverted(e):
                return None
            raise
    
    @cached_property
    @log(logger)
    def get_coins_decimals(self) -> List[int]:
        source = self.factory if self.factory else curve.registry
        coins_decimals = source.get_decimals(self.address)

        # pool not in registry
        if not any(coins_decimals):
            coins_decimals = [coin.decimals for coin in self.get_coins]
        
        return [dec for dec in coins_decimals if dec != 0]
    
    @cached_property
    @log(logger)
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
    
    @log(logger)
    @lru_cache
    def get_balances(self, block: Optional[Block] = None) -> Dict[ERC20, int]:
        """
        Get {token: balance} of liquidity in the pool.
        """
        try:
            source = self.factory if self.factory else curve.registry
            balances = source.get_balances(self.address, block_identifier=block)
        # fallback for historical queries
        except ValueError:
            balances = multicall_same_func_same_contract_different_inputs(
                self.address, 'balances(uint256)(uint256)', inputs = (i for i, _ in enumerate(self.get_coins)), block=block)

        if not any(balances):
            raise ValueError(f'could not fetch balances {self.__str__()} at {block}')

        return {
            coin: balance / 10 ** dec
            for coin, balance, dec in zip(self.get_coins, balances, self.get_coins_decimals)
            if coin != ZERO_ADDRESS
        }
    
    @log(logger)
    def get_tvl(self, block: Optional[Block] = None) -> Optional[UsdValue]:
        """
        Get total value in Curve pool.
        """
        balances = self.get_balances(block=block)
        if balances is None:
            return None

        return UsdValue(
            sum(balances[coin] * magic.get_price(coin, block=block) for coin in balances)
        )
    
    @cached_property
    @log(logger)
    def oracle(self) -> Optional[Address]:
        '''
        If `pool` has method `price_oracle`, returns price_oracle address.
        Else, returns `None`.
        '''
        response = raw_call(self.address, 'price_oracle()', output='address', return_None_on_failure=True)
        if response == ZERO_ADDRESS:
            return None
        return response
    
    @log(logger)
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
    
    @log(logger)
    def calculate_apy(self, lp_token: str, block: Optional[Block] = None) -> Dict[str,float]:
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
    
    @log(logger)
    def calculate_boost(self, addr: str, block: Optional[Block] = None) -> Dict[str,float]:
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

from y.curve.curve import CurveRegistry

try:
    curve = CurveRegistry()
except UnsupportedNetwork:
    curve = set()
