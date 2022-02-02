
import logging
from functools import lru_cache

from y.contracts import Contract, has_methods
from y.decorators import log
from y.prices import magic
from y.utils.raw_calls import _decimals, _totalSupplyReadable, raw_call

logger = logging.getLogger(__name__)

@log(logger)
@lru_cache
def is_eps_rewards_pool(token_address: str) -> bool:
    return has_methods(token_address, ['lpStaker()(address)','rewardTokens(uint)(address)','rewardPerToken(address)(uint)','minter()(address)'])

@log(logger)
def get_price(token_address: str, block=None):
    minter = Contract(raw_call(token_address,'minter()',output='address', block=block))
    i, balances = 0, []
    while True:
        try:
            coin = minter.coins(i, block_identifier = block)
            balances.append((coin,minter.balances(i, block_identifier = block) / 10 ** _decimals(coin,block)))
            i += 1
        except:
            break
    tvl = sum(balance * magic.get_price(coin, block) for coin, balance in balances)
    totalSupply = _totalSupplyReadable(token_address,block)
    return tvl / totalSupply
    
