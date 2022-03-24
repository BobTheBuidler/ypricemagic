
import logging
from typing import Dict, List, Optional

from y.classes.common import ERC20
from y.datatypes import UsdPrice, UsdValue
from y.decorators import log
from y.typing import Block
from y.utils.multicall import fetch_multicall, multicall_decimals

logger = logging.getLogger(__name__)

class BalancerV1Pool(ERC20):
    def __init__(self, pool_address) -> None:
        super().__init__(pool_address)

    @log(logger)
    def tokens(self, block: Optional[Block] = None) -> List[ERC20]:
        tokens = self.contract.getCurrentTokens(block_identifier=block)
        return [ERC20(token) for token in tokens]

    @log(logger)
    def get_pool_price(self, block: Optional[Block] = None) -> UsdPrice:
        supply = self.total_supply_readable(block=block)
        if supply == 0:
            return 0
        return UsdPrice(self.get_tvl(block=block) / supply)

    @log(logger)
    def get_tvl(self, block: Optional[Block] = None) -> Optional[UsdValue]:
        token_balances = self.get_balances()
        good_balances = {
            token: balance
            for token, balance
            in token_balances.items()
            if token.price(block=block, return_None_on_failure=True) is not None
        }
        
        # in case we couldn't get prices for all tokens, we can extrapolate from the prices we did get
        good_value = sum(balance * token.price(block=block, return_None_on_failure=True) for token, balance in good_balances.items())
        if len(good_balances):
            return good_value / len(good_balances) * len(token_balances)
        return None

    @log(logger)
    def get_balances(self, block: Optional[Block] = None) -> Dict[ERC20, float]:
        tokens = self.tokens(block=block)
        balances = fetch_multicall(*[[self.contract, "getBalance", token] for token in tokens], block=block)
        balances = [balance if balance else 0 for balance in balances]
        decimals = multicall_decimals(tokens, block)
        return {token:balance / 10 ** decimal for token, balance, decimal in zip(tokens,balances,decimals)}
