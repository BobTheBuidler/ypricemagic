
import asyncio
from decimal import Decimal
from typing import Optional

import a_sync
from brownie.convert.datatypes import EthAddress
from multicall import Call

from y.classes.common import ERC20, WeiBalance
from y.datatypes import Block, UsdPrice


@a_sync.a_sync(default='sync')
async def is_basketdao_index(address: EthAddress) -> bool:
    try:
        if await Call(address, 'getAssetsAndBalances()(address[],uint[])').coroutine():
            return True
    except:
        return False

@a_sync.a_sync(default='sync')
async def get_price(address: EthAddress, block: Optional[Block] = None) -> UsdPrice:
    balances, total_supply = await asyncio.gather(
        Call(address, 'getAssetsAndBalances()(address[],uint[])',block_id=block).coroutine(),
        ERC20(address, asynchronous=True).total_supply_readable(block=block),
    )

    balances = [
        WeiBalance(balance, token, block)
        for token, balance
        in zip(balances[0],balances[1])
    ]

    tvl = sum(await asyncio.gather(*[bal.__value_usd__(sync=False) for bal in balances]))
    return UsdPrice(tvl / Decimal(total_supply))
