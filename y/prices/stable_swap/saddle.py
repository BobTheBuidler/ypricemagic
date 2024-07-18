
import asyncio
import logging
from typing import List, Optional

import a_sync
from brownie import chain

from y import ENVIRONMENT_VARIABLES as ENVS
from y import convert
from y.classes.common import ERC20
from y.contracts import has_method, has_methods
from y.datatypes import (Address, AddressOrContract, AnyAddressType, Block,
                         UsdPrice, UsdValue)
from y.networks import Network
from y.prices import magic
from y.utils.multicall import \
    multicall_same_func_same_contract_different_inputs

logger = logging.getLogger(__name__)


@a_sync.a_sync(default='sync', cache_type='memory', ram_cache_ttl=5*60)
async def is_saddle_lp(token_address: AnyAddressType) -> bool:
    pool = await get_pool(token_address, sync=False)
    return pool is not None and await has_methods(pool, ('getVirtualPrice()(uint)', 'getA()(uint)','getAPrecise()(uint)'), sync=False)

@a_sync.a_sync(default='sync', ram_cache_ttl=ENVS.CACHE_TTL)
async def get_pool(token_address: AnyAddressType) -> Address:
    convert.to_address(token_address)
    if chain.id == Network.Mainnet:
        if token_address == '0xc9da65931ABf0Ed1b74Ce5ad8c041C4220940368': # saddle aleth doesn't have swap() function
            return '0xa6018520EAACC06C30fF2e1B3ee2c7c22e64196a'
        elif token_address == '0xd48cF4D7FB0824CC8bAe055dF3092584d0a1726A': # saddle d4
            return '0xC69DDcd4DFeF25D8a793241834d4cc4b3668EAD6'
        elif token_address == '0xF32E91464ca18fc156aB97a697D6f8ae66Cd21a3':
            return '0xdf3309771d2BF82cb2B6C56F9f5365C8bD97c4f2'
    pool = await has_method(token_address, 'swap()(address)', return_response=True, sync=False)
    return pool or None

@a_sync.a_sync(default='sync')
async def get_price(token_address: AddressOrContract, block: Optional[Block] = None) -> UsdPrice:
    tvl, total_supply = await asyncio.gather(
        get_tvl(token_address, block, sync=False),
        ERC20(token_address, asynchronous=True).total_supply_readable(block),
    )
    return UsdPrice(tvl / total_supply)

@a_sync.a_sync(default='sync')
async def get_tvl(token_address: AnyAddressType, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE) -> UsdValue:
    tokens: List[ERC20]
    pool, tokens, balances = await asyncio.gather(
        get_pool(token_address, sync=False),
        get_tokens(token_address, block, sync=False),
        multicall_same_func_same_contract_different_inputs(
            pool, 'getTokenBalance(uint8)(uint)', inputs=[*range(len(tokens))], sync=False
        ),
    )
    scales, prices = await a_sync.gather(
        ERC20.scale.map(tokens).values(pop=True),
        magic.get_prices(tokens, block, skip_cache=skip_cache, silent=True, sync=False),
    )
    return UsdValue(sum(balance / scale * price for balance, scale, price in zip(balances, scales, prices)))

@a_sync.a_sync(default='sync')
async def get_tokens(token_address: AnyAddressType, block: Optional[Block] = None) -> List[ERC20]:
    pool, response = await asyncio.gather(
        get_pool(token_address, sync=False),
        multicall_same_func_same_contract_different_inputs(
            pool, 'getToken(uint8)(address)', inputs=[*range(8)], block=block, return_None_on_failure=True, sync=False
        ),
    )
    return [ERC20(token) for token in response if token is not None]
