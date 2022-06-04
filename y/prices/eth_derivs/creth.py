import logging
from typing import Optional

from brownie import chain
from multicall.utils import await_awaitable, gather
from y import convert
from y.constants import weth
from y.datatypes import AnyAddressType, Block, UsdPrice
from y.networks import Network
from y.prices import magic
from y.utils.logging import yLazyLogger
from y.utils.raw_calls import _totalSupply, raw_call_async

logger = logging.getLogger(__name__)

@yLazyLogger(logger)
def is_creth(token: AnyAddressType) -> bool:
    address = convert.to_address(token)
    return chain.id == Network.Mainnet and address == '0xcBc1065255cBc3aB41a6868c22d1f1C573AB89fd'

@yLazyLogger(logger)
def get_price_creth(token: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
    return await_awaitable(get_price_creth_async(token, block=block))

@yLazyLogger(logger)
async def get_price_creth_async(token: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
    address = convert.to_address(token)
    total_balance, total_supply, weth_price = await gather([
        raw_call_async(address, 'accumulated()', output='int', block=block),
        _totalSupply(address,block),
        magic.get_price_async(weth,block),
    ])
    per_share = total_balance / total_supply
    return per_share * weth_price
