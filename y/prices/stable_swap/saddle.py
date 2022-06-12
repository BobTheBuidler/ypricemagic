
import logging
from typing import List, Optional

from async_lru import alru_cache
from brownie import chain
from multicall.utils import await_awaitable, gather
from y import convert
from y.classes.common import ERC20
from y.contracts import has_method_async, has_methods_async
from y.datatypes import (Address, AddressOrContract, AnyAddressType, Block,
                         UsdPrice, UsdValue)
from y.networks import Network
from y.prices import magic
from y.utils.logging import yLazyLogger
from y.utils.multicall import \
    multicall_same_func_same_contract_different_inputs_async

logger = logging.getLogger(__name__)


@yLazyLogger(logger)
def is_saddle_lp(token_address: AnyAddressType) -> bool:
    return await_awaitable(is_saddle_lp_async(token_address))

@yLazyLogger(logger)
@alru_cache(maxsize=None)
async def is_saddle_lp_async(token_address: AnyAddressType) -> bool:
    pool = await get_pool(token_address)
    if pool:
        return await has_methods_async(pool, ('getVirtualPrice()(uint)', 'getA()(uint)','getAPrecise()(uint)'))


@yLazyLogger(logger)
@alru_cache(maxsize=None)
async def get_pool(token_address: AnyAddressType) -> Address:
    convert.to_address(token_address)
    if chain.id == Network.Mainnet:
        if token_address == '0xc9da65931ABf0Ed1b74Ce5ad8c041C4220940368': # saddle aleth doesn't have swap() function
            return '0xa6018520EAACC06C30fF2e1B3ee2c7c22e64196a'
        elif token_address == '0xd48cF4D7FB0824CC8bAe055dF3092584d0a1726A': # saddle d4
            return '0xC69DDcd4DFeF25D8a793241834d4cc4b3668EAD6'
        elif token_address == '0xF32E91464ca18fc156aB97a697D6f8ae66Cd21a3':
            return '0xdf3309771d2BF82cb2B6C56F9f5365C8bD97c4f2'
    pool = await has_method_async(token_address, 'swap()(address)', return_response=True)
    return pool or None

@yLazyLogger(logger)
def get_price(token_address: AddressOrContract, block: Optional[Block] = None) -> UsdPrice:
    return await_awaitable(get_price_async(token_address, block))

async def get_price_async(token_address: AddressOrContract, block: Optional[Block] = None) -> UsdPrice:
    tvl, total_supply = await gather([
        get_tvl(token_address, block),
        ERC20(token_address).total_supply_readable_async(block),
    ])
    return UsdPrice(tvl / total_supply)

@yLazyLogger(logger)
async def get_tvl(token_address: AnyAddressType, block: Optional[Block] = None) -> UsdValue:
    pool, tokens, balances = await gather([
        get_pool(token_address),
        get_tokens(token_address, block),
        multicall_same_func_same_contract_different_inputs_async(
            pool, 'getTokenBalance(uint8)(uint)', inputs=[*range(len(tokens))]
        ),
    ])
    tokens_scale, prices = await gather([
        gather([token.scale for token in tokens]),
        magic.get_prices_async(tokens, block, silent=True),
    ])
    balances = [balance / scale for balance, scale in zip(balances, tokens_scale)]
    return UsdValue(sum(balance * price for balance, price in zip (balances, prices)))


@yLazyLogger(logger)
async def get_tokens(token_address: AnyAddressType, block: Optional[Block] = None) -> List[ERC20]:
    pool, response = await gather([
        get_pool(token_address),
        multicall_same_func_same_contract_different_inputs_async(
            pool, 'getToken(uint8)(address)', inputs=[*range(8)], block=block, return_None_on_failure=True
        ),
    ])
    return [ERC20(token) for token in response if token is not None]
