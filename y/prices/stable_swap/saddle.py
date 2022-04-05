
import logging
from functools import lru_cache
from typing import List, Optional

from brownie import chain
from y import convert
from y.contracts import has_method, has_methods
from y.datatypes import UsdPrice, UsdValue
from y.decorators import log
from y.erc20 import decimals
from y.networks import Network
from y.prices import magic
from y.typing import Address, AddressOrContract, AnyAddressType, Block
from y.utils.multicall import \
    multicall_same_func_same_contract_different_inputs
from y.utils.raw_calls import _totalSupplyReadable

logger = logging.getLogger(__name__)


@lru_cache
@log(logger)
def is_saddle_lp(token_address: AnyAddressType) -> bool:
    pool = get_pool(token_address)
    if pool: return has_methods(pool, ['getVirtualPrice()(uint)', 'getA()(uint)','getAPrecise()(uint)'])


@lru_cache
@log(logger)
def get_pool(token_address: AnyAddressType) -> Address:
    convert.to_address(token_address)
    if chain.id == Network.Mainnet:
        if token_address == '0xc9da65931ABf0Ed1b74Ce5ad8c041C4220940368': # saddle aleth doesn't have swap() function
            return '0xa6018520EAACC06C30fF2e1B3ee2c7c22e64196a'
        elif token_address == '0xd48cF4D7FB0824CC8bAe055dF3092584d0a1726A': # saddle d4
            return '0xC69DDcd4DFeF25D8a793241834d4cc4b3668EAD6'
        elif token_address == '0xF32E91464ca18fc156aB97a697D6f8ae66Cd21a3':
            return '0xdf3309771d2BF82cb2B6C56F9f5365C8bD97c4f2'
    pool = has_method(token_address, 'swap()(address)', return_response=True)
    return pool or None


@log(logger)
def get_price(token_address: AddressOrContract, block: Optional[Block] = None) -> UsdPrice:
    return UsdPrice(tvl(token_address, block) / _totalSupplyReadable(token_address, block))


@log(logger)
def tvl(token_address: AnyAddressType, block: Optional[Block] = None) -> UsdValue:
    tokens = get_tokens(token_address, block)
    pool = get_pool(token_address)
    balances = multicall_same_func_same_contract_different_inputs(
        pool, 'getTokenBalance(uint8)(uint)', inputs=[*range(len(tokens))])
    tokens_decimals = decimals(tokens, block=block)
    balances = [balance / 10 ** decimal for balance, decimal in zip(balances, tokens_decimals)]
    prices = magic.get_prices(tokens, block, silent=True)
    return UsdValue(sum(balance * price for balance, price in zip (balances, prices)))


@log(logger)
def get_tokens(token_address: AnyAddressType, block: Optional[Block] = None) -> List[Address]:
    pool = get_pool(token_address)
    response = multicall_same_func_same_contract_different_inputs(
        pool, 'getToken(uint8)(address)', inputs=[*range(8)], block=block, return_None_on_failure=True)
    return [token for token in response if token is not None]
