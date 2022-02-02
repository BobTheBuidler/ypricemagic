
import logging
from typing import Dict, List

from y.classes.common import ERC20
from y.decorators import log
from y.utils.multicall import fetch_multicall, multicall_decimals

logger = logging.getLogger(__name__)

class BalancerV1Pool(ERC20):
    def __init__(self, pool_address) -> None:
        super().__init__(pool_address)

    @log(logger)
    def tokens(self, block=None) -> List[ERC20]:
        tokens = self.contract.getCurrentTokens(block_identifier=block)
        return [ERC20(token) for token in tokens]

    @log(logger)
    def get_pool_price(self, block: int = None) -> float:
        supply = self.total_supply_readable(block=block)
        if supply == 0: return 0
        return self.get_tvl(block=block) / supply

    @log(logger)
    def get_tvl(self, block: int = None) -> float:
        return sum(balance * token.price(block=block) for token, balance in self.get_balances.items())

    @log(logger)
    def get_balances(self, block: int = None) -> Dict[ERC20, float]:
        tokens = self.tokens(block=block)
        balances = fetch_multicall(*[[self.contract, "getBalance", token] for token in tokens], block=block)
        balances = [balance if balance else 0 for balance in balances]
        decimals = multicall_decimals(tokens, block)
        return {token:balance / 10 ** decimal for token, balance, decimal in zip(tokens,balances,decimals)}
