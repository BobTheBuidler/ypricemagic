
import logging
from typing import Optional

from async_lru import alru_cache
from multicall.utils import await_awaitable, gather
from y.classes.common import ERC20, WeiBalance
from y.contracts import Contract, has_methods_async
from y.datatypes import AddressOrContract, AnyAddressType, Block, UsdPrice
from y.utils.logging import yLazyLogger
from y.utils.raw_calls import raw_call_async

logger = logging.getLogger(__name__)

#yLazyLogger(logger)
def is_eps_rewards_pool(token_address: AnyAddressType) -> bool:
    return await_awaitable(is_eps_rewards_pool_async(token_address))

#yLazyLogger(logger)
@alru_cache(maxsize=None)
async def is_eps_rewards_pool_async(token_address: AnyAddressType) -> bool:
    return await has_methods_async(token_address, ('lpStaker()(address)','rewardTokens(uint)(address)','rewardPerToken(address)(uint)','minter()(address)'))

#yLazyLogger(logger)
def get_price(token_address: AddressOrContract, block: Optional[Block] = None) -> UsdPrice:
    return await_awaitable(get_price_async(token_address, block))

async def get_price_async(token_address: AddressOrContract, block: Optional[Block] = None) -> UsdPrice:
    minter = Contract(await raw_call_async(token_address,'minter()',output='address', block=block))
    i, balances = 0, []
    while True:
        try:
            coin, balance = await gather([
                minter.coins.coroutine(i, block_identifier = block),
                minter.balances(i, block_identifier = block),
            ])
            balance /= await ERC20(coin).scale
            balances.append(WeiBalance(balance, coin, block))
            i += 1
        except:
            break
    coin_values, total_supply = await gather([
        gather([b.value_usd_async for b in balances]),
        ERC20(token_address).total_supply_readable_async(block),
    ])
    tvl = sum(coin_values)
    return UsdPrice(tvl / total_supply)
