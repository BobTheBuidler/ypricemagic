
from asyncio import gather
import logging
from typing import Optional

from async_lru import alru_cache
from brownie import ZERO_ADDRESS, chain, multicall, web3
from multicall.utils import await_awaitable
from y import convert
from y.utils.dank_mids import dank_w3
from y.classes.common import ERC20
from y.constants import weth
from y.contracts import Contract
from y.datatypes import AnyAddressType, Block, UsdPrice
from y.prices import magic
from y.utils.logging import yLazyLogger
from y.utils.multicall import multicall2
from y.utils.raw_calls import _decimals, _totalSupplyReadable

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

@yLazyLogger(logger)
def is_mooniswap_pool(token: AnyAddressType) -> bool:
    return await_awaitable(is_mooniswap_pool_async(token))

@yLazyLogger(logger)
@alru_cache(maxsize=None)
async def is_mooniswap_pool_async(token: AnyAddressType) -> bool:
    address = convert.to_address(token)
    if router is None:
        return False
    return await router.isPool.coroutine(address)

def get_pool_price(token: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
    return await_awaitable(get_pool_price_async(token, block=block))

@yLazyLogger(logger)
async def get_pool_price_async(token: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
    address = convert.to_address(token)
    token = Contract(address)
    token0, token1 = await gather([
        token.token0.coroutine(),
        token.token1.coroutine(),
    ])

    bal0, bal1, price0, price1, total_supply = await gather([
        dank_w3.eth.get_balance(token.address) / 10 ** 18 if token0 == ZERO_ADDRESS else ERC20(token0).balance_of_readable_async(token.address, block),
        dank_w3.eth.get_balance(token.address) / 10 ** 18 if token1 == ZERO_ADDRESS else ERC20(token1).balance_of_readable_async(token.address, block),
        magic.get_price_async(gas_coin, block) if token0 == ZERO_ADDRESS else magic.get_price_async(token0, block),
        magic.get_price_async(gas_coin, block) if token1 == ZERO_ADDRESS else magic.get_price_async(token1, block),
        ERC20(address).total_supply_readable_async(block),
    ])

    totalVal = bal0 * price0 + bal1 * price1
    price = totalVal / total_supply
    return price
    
