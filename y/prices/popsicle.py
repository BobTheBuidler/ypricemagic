import logging
from functools import lru_cache
from typing import Optional

from multicall import Call, Multicall
from y import convert
from y.classes.common import WeiBalance
from y.contracts import has_methods
from y.datatypes import UsdPrice
from y.decorators import log
from y.typing import AnyAddressType, Block
from y.utils.raw_calls import _totalSupplyReadable

logger = logging.getLogger(__name__)

@log(logger)
@lru_cache
def is_popsicle_lp(token_address: AnyAddressType) -> bool:
    # NOTE: contract to check for reference (mainnet): 0xd2C5A739ebfE3E00CFa88A51749d367d7c496CCf
    return has_methods(token_address, ['token0()(address)','token1()(address)','usersAmounts()((uint,uint))'])

@log(logger)
def get_price(token: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
    address = convert.to_address(token)
    methods = 'token0()(address)','token1()(address)','usersAmounts()((uint,uint))'
    calls = [Call(address, method, [[method,None]]) for method in methods]
    token0, token1, (balance0, balance1) = Multicall(calls, block_id=block)().values()
    balance0 = WeiBalance(balance0, token0, block=block)
    balance1 = WeiBalance(balance1, token1, block=block)
    totalVal = balance0.value_usd() + balance1.value_usd()
    totalSupply = _totalSupplyReadable(address,block)
    return UsdPrice(totalVal / totalSupply)
