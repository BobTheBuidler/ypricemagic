
import asyncio
import logging
from decimal import Decimal
from typing import Optional

import a_sync
from brownie import ZERO_ADDRESS, chain

from y import convert
from y.classes.common import ERC20
from y.constants import weth
from y.contracts import Contract
from y.datatypes import AnyAddressType, Block, UsdPrice
from y.prices import magic
from y.utils.dank_mids import dank_w3

logger = logging.getLogger(__name__)

if chain.id == 1:
    router = Contract("0xbAF9A5d4b0052359326A6CDAb54BABAa3a3A9643")
    gas_coin = weth
elif chain.id == 56:
    router = Contract("0xD41B24bbA51fAc0E4827b6F94C0D6DDeB183cD64")
    gas_coin = Contract("0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c") #wbnb
else: 
    router = None
    gas_coin = None

@a_sync.a_sync(default='sync', cache_type='memory')
async def is_mooniswap_pool(token: AnyAddressType) -> bool:
    address = convert.to_address(token)
    if router is None:
        return False
    return await router.isPool.coroutine(address)

@a_sync.a_sync(default='sync')
async def get_pool_price(token: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
    address = convert.to_address(token)
    token = await Contract.coroutine(address)
    token0, token1 = await asyncio.gather(
        token.token0.coroutine(),
        token.token1.coroutine(),
    )

    bal0, bal1, price0, price1, total_supply = await asyncio.gather(
        dank_w3.eth.get_balance(token.address) if token0 == ZERO_ADDRESS else ERC20(token0, asynchronous=True).balance_of_readable(token.address, block),
        dank_w3.eth.get_balance(token.address) if token1 == ZERO_ADDRESS else ERC20(token1, asynchronous=True).balance_of_readable(token.address, block),
        magic.get_price(gas_coin, block, sync=False) if token0 == ZERO_ADDRESS else magic.get_price(token0, block, sync=False),
        magic.get_price(gas_coin, block, sync=False) if token1 == ZERO_ADDRESS else magic.get_price(token1, block, sync=False),
        ERC20(address, asynchronous=True).total_supply_readable(block),
    )

    if token0 == ZERO_ADDRESS:
        bal0 /= 1e18
    elif token1 == ZERO_ADDRESS:
        bal1 /= 1e18

    totalVal = bal0 * float(price0) + bal1 * float(price1)
    price = totalVal / total_supply
    return Decimal(price)
    