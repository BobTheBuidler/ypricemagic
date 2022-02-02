
import logging
from functools import cached_property, lru_cache
from typing import Dict, List

from brownie import ZERO_ADDRESS
from y.classes.common import WeiBalance
from y.classes.erc20 import ERC20
from y.contracts import Contract
from y.decorators import log
from ypricemagic import magic
from ypricemagic.utils.multicall import (
    fetch_multicall, multicall_same_func_same_contract_different_inputs)
from ypricemagic.utils.raw_calls import raw_call

logger = logging.getLogger(__name__)


class CurvePool(ERC20):
    def __init__(self, address: str, *args, **kwargs):
        super().__init__(address, *args, **kwargs)
    
    @cached_property
    def contract(self) -> Contract:
        return Contract(self.address)
    
    @log(logger)
    @cached_property
    def factory(self) -> Contract:
        return curve.get_factory(self)

    @log(logger)
    @cached_property
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
        return [i for i in enumerate(self.get_coins) if coin == coin][0]
    
    @log(logger)
    def get_dy(self, token_in: str, token_out: str, block: int = None) -> WeiBalance:
        ix_in = self.get_coin_index(token_in)
        ix_out = self.get_coin_index(token_out)
        amount_in = ERC20(token_in).scale(block=block)
        amount_out = self.get_dy(ix_in, ix_out, amount_in)
        return WeiBalance(amount_out, token_out, block=block)
    
    @log(logger)
    @cached_property
    def get_coins_decimals(self, pool: str) -> List[int]:
        source = self.factory if self.factory else curve.registry
        coins_decimals = source.get_decimals(pool)

        # pool not in registry
        if not any(coins_decimals):
            coins_decimals = [coin.decimals() for coin in self.get_coins]
        
        return [dec for dec in coins_decimals if dec != 0]
    
    @log(logger)
    @cached_property
    def get_underlying_coins(self) -> List[ERC20]:        
        if self.factory:
            # new factory reverts for non-meta pools
            if not hasattr(self.factory, 'is_meta') or self.factory.is_meta(self.address):
                coins = self.factory.get_underlying_coins(self.address)
            else:
                coins = self.factory.get_coins(self.address)
        else:
            coins = self.registry.get_underlying_coins(self.address)
        
        # pool not in registry, not checking for underlying_coins here
        if set(coins) == {ZERO_ADDRESS}:
            return self.get_coins

        return [ERC20(coin) for coin in coins if coin != ZERO_ADDRESS]
    
    @log(logger)
    @lru_cache
    def get_balances(self, block=None) -> Dict[ERC20, int]:
        """
        Get {token: balance} of liquidity in the pool.
        """
        try:
            source = self.factory if self.factory else curve.registry
            balances = source.get_balances(self.address, block_identifier=block)
        # fallback for historical queries
        except ValueError:
            balances = fetch_multicall(
                *[[self.contract, 'balances', i] for i, _ in enumerate(self.get_coins)]
            )

        if not any(balances):
            raise ValueError(f'could not fetch balances {self.__str__()} at {block}')

        return {
            coin: balance / 10 ** dec
            for coin, balance, dec in zip(self.get_coins, balances, self.get_coins_decimals)
            if coin != ZERO_ADDRESS
        }
    
    @log(logger)
    def get_tvl(self, block=None):
        """
        Get total value in Curve pool.
        """
        balances = self.get_balances(block=block)
        if balances is None: return None

        return sum(
            balances[coin] * magic.get_price(coin, block=block) for coin in balances
        )
    
    @log(logger)
    @cached_property
    def oracle(self) -> str:
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
    def get_gauge(self, pool):
        """
        Get liquidity gauge address by pool.
        """
        if self.factory and hasattr(self.factory, 'get_gauge'):
            gauge = self.factory.get_gauge(pool)
            if gauge != ZERO_ADDRESS:
                return gauge

        gauges, types = curve.registry.get_gauges(pool)
        if gauges[0] != ZERO_ADDRESS:
            return gauges[0]
    

    def __str__(self) -> str:
        return self.address

from ypricemagic.price_modules.curve.curve import CurveRegistry

curve = CurveRegistry()
