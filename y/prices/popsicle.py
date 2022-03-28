import logging
from functools import lru_cache
from typing import Optional

import y.prices.magic
from multicall import Call, Multicall
from y import convert
from y.contracts import has_methods
from y.datatypes import UsdPrice
from y.decorators import log
from y.typing import AnyAddressType, Block
from y.utils.raw_calls import _decimals, _totalSupplyReadable, raw_call

logger = logging.getLogger(__name__)

@log(logger)
@lru_cache
def is_popsicle_lp(token_address: AnyAddressType) -> bool:
    # NOTE: contract to check for reference (mainnet): 0xd2C5A739ebfE3E00CFa88A51749d367d7c496CCf
    return has_methods(token_address, ['rerange()(uint)','rebalance()(uint)', 'userAmounts()(uint, uint)'])

@log(logger)
def get_price(token: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
    address = convert.to_address(token)
    methods = 'token0()(address)','token1()(address)','usersAmounts()((uint,uint))'
    calls = [Call(address, method, [[method,None]]) for method in methods]
    token0, token1, (balance0, balance1) = Multicall(calls, block_id=block)().values()
    balance0 /= 10 ** _decimals(token0,block)
    balance1 /= 10 ** _decimals(token1,block)
    totalSupply = _totalSupplyReadable(address,block)
    totalVal = balance0 * y.prices.magic.get_price(token0,block) + balance1 * y.prices.magic.get_price(token1,block)
    return UsdPrice(totalVal / totalSupply)
