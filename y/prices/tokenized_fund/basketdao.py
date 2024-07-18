
import asyncio
from decimal import Decimal
from typing import Optional

import a_sync
from brownie.convert.datatypes import EthAddress
from multicall import Call
from web3.exceptions import ContractLogicError

from y.classes.common import ERC20, WeiBalance
from y.datatypes import Block, UsdPrice


@a_sync.a_sync(default='sync')
async def is_basketdao_index(address: EthAddress) -> bool:
    try:
        return bool(await Call(address, 'getAssetsAndBalances()(address[],uint[])'))
    except (ContractLogicError, ValueError):
        return False

@a_sync.a_sync(default='sync')
async def get_price(address: EthAddress, block: Optional[Block] = None) -> UsdPrice:
    balances, total_supply = await asyncio.gather(
        Call(address, 'getAssetsAndBalances()(address[],uint[])',block_id=block),
        ERC20(address, asynchronous=True).total_supply_readable(block=block),
    )
    balances = (WeiBalance(balance, token, block) for token, balance in zip(balances[0], balances[1]))
    tvl = await WeiBalance.value_usd.sum(balances, sync=False)
    return UsdPrice(tvl / Decimal(total_supply))
