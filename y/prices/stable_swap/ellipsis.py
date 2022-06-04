
import logging
from typing import Optional

from async_lru import alru_cache
from multicall.utils import await_awaitable
from y.contracts import Contract, has_methods_async
from y.datatypes import AddressOrContract, AnyAddressType, Block, UsdPrice
from y.prices import magic
from y.utils.logging import yLazyLogger
from y.utils.raw_calls import _decimals, _totalSupplyReadable, raw_call

logger = logging.getLogger(__name__)

@yLazyLogger(logger)
def is_eps_rewards_pool(token_address: AnyAddressType) -> bool:
    return await_awaitable(is_eps_rewards_pool_async(token_address))

@yLazyLogger(logger)
@alru_cache(maxsize=None)
async def is_eps_rewards_pool_async(token_address: AnyAddressType) -> bool:
    return await has_methods_async(token_address, ('lpStaker()(address)','rewardTokens(uint)(address)','rewardPerToken(address)(uint)','minter()(address)'))

@yLazyLogger(logger)
def get_price(token_address: AddressOrContract, block: Optional[Block] = None) -> UsdPrice:
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
    return UsdPrice(tvl / totalSupply)
    
