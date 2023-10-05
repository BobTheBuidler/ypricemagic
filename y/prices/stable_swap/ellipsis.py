
import asyncio
import logging
from decimal import Decimal
from typing import Optional

import a_sync

from y.classes.common import ERC20, WeiBalance
from y.contracts import Contract, has_methods
from y.datatypes import AddressOrContract, AnyAddressType, Block, UsdPrice
from y.utils.raw_calls import raw_call

logger = logging.getLogger(__name__)


@a_sync.a_sync(default='sync', cache_type='memory')
async def is_eps_rewards_pool(token_address: AnyAddressType) -> bool:
    return await has_methods(token_address, ('lpStaker()(address)','rewardTokens(uint)(address)','rewardPerToken(address)(uint)','minter()(address)'), sync=False)

@a_sync.a_sync(default='sync')
async def get_price(token_address: AddressOrContract, block: Optional[Block] = None) -> UsdPrice:
    minter = await raw_call(token_address,'minter()',output='address', block=block, sync=False)
    minter = await Contract.coroutine(minter)
    i, balances = 0, []
    while True:
        try:
            coin, balance = await asyncio.gather(
                minter.coins.coroutine(i, block_identifier = block),
                minter.balances.coroutine(i, block_identifier = block),
            )
            balance /= await ERC20(coin, asynchronous=True).scale
            balances.append(WeiBalance(balance, coin, block))
            i += 1
        except:
            break
    coin_values, total_supply = await asyncio.gather(
        asyncio.gather(*[b.__value_usd__(sync=False) for b in balances]),
        ERC20(token_address, asynchronous=True).total_supply_readable(block),
    )
    tvl = sum(coin_values)
    return UsdPrice(tvl / Decimal(total_supply))
