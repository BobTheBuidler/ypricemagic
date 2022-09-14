
from typing import Optional

from brownie.convert.datatypes import EthAddress
from multicall import Call
from multicall.utils import await_awaitable, gather
from y.classes.common import ERC20, WeiBalance
from y.datatypes import Block, UsdPrice


def is_basketdao_index(address: EthAddress) -> bool:
    return await_awaitable(is_basketdao_index_async(address))

async def is_basketdao_index_async(address: EthAddress) -> bool:
    try:
        if await Call(address, 'getAssetsAndBalances()(address[],uint[])').coroutine():
            return True
    except:
        return False

def get_price(address: EthAddress, block: Optional[Block] = None) -> UsdPrice:
    return await_awaitable(get_price_async(address, block=block))

async def get_price_async(address: EthAddress, block: Optional[Block] = None) -> UsdPrice:
    balances, total_supply = await gather([
        Call(address, 'getAssetsAndBalances()(address[],uint[])',block_id=block).coroutine(),
        ERC20(address).total_supply_readable_async(block=block),
    ])

    balances = [
        WeiBalance(balance, token, block)
        for token, balance
        in zip(balances[0],balances[1])
    ]

    tvl = sum(await gather([bal.value_usd_async for bal in balances]))
    return UsdPrice(tvl / total_supply)
