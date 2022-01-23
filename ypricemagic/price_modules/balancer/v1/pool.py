
import logging

from y.contracts import has_methods
from y.decorators import log
from y.exceptions import PriceError
from ypricemagic import magic
from ypricemagic.classes import ERC20
from ypricemagic.utils.multicall import fetch_multicall, multicall_decimals
from ypricemagic.utils.raw_calls import _totalSupplyReadable

logger = logging.getLogger(__name__)

class BalancerV1Pool(ERC20):
    def __init__(self, pool_address) -> None:
        super().__init__(pool_address)

    @log(logger)
    def tokens(self, block=None):
        return self.contract.getCurrentTokens(block_identifier=block)

    @log(logger)
    def get_pool_price(self, block=None):
        supply = _totalSupplyReadable(self.contract, block)
        if supply == 0: return 0
        return self.get_tvl(block=block) / supply

    @log(logger)
    def get_tvl(self, block=None):
        balances = self.get_balances(block)
        prices = [_get_price(token, block=block) for token in balances]
        return sum(balance * price for balance, price in zip(balances.values(), prices) if price)

    @log(logger)
    def get_balances(self, block=None):
        tokens = self.tokens(block=block)
        balances = fetch_multicall(*[[self.contract, "getBalance", token] for token in tokens], block=block)
        for position, balance in enumerate(balances):
            if balance is None: balances[position] = 0
        decimals = multicall_decimals(tokens, block)
        return {token:balance / 10 ** decimal for token, balance, decimal in zip(tokens,balances,decimals)}

@log(logger)
def _get_price(token_address, block=None):
    try: return magic.get_price(token_address, block)
    except PriceError: return None
