import asyncio
import logging
from typing import Optional

import a_sync
from brownie import chain

from y import ENVIRONMENT_VARIABLES as ENVS
from y import convert
from y.classes.common import ERC20
from y.constants import weth
from y.datatypes import AnyAddressType, Block, UsdPrice
from y.networks import Network
from y.prices import magic
from y.utils.raw_calls import raw_call

logger = logging.getLogger(__name__)

def is_creth(token: AnyAddressType) -> bool:
    address = convert.to_address(token)
    return chain.id == Network.Mainnet and address == '0xcBc1065255cBc3aB41a6868c22d1f1C573AB89fd'

@a_sync.a_sync(default='sync')
async def get_price_creth(token: AnyAddressType, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE) -> UsdPrice:
    address = convert.to_address(token)
    total_balance, total_supply, weth_price = await asyncio.gather(
        raw_call(address, 'accumulated()', output='int', block=block, sync=False),
        ERC20(address, asynchronous=True).total_supply(block),
        magic.get_price(weth, block, skip_cache=skip_cache, sync=False),
    )
    per_share = total_balance / total_supply
    return per_share * weth_price
