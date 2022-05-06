import logging
from functools import lru_cache
from typing import Optional, Tuple

from multicall import Call, Multicall
from y import convert
from y.classes.common import WeiBalance
from y.contracts import has_methods
from y.datatypes import UsdPrice, UsdValue
from y.exceptions import call_reverted
from y.typing import AnyAddressType, Block
from y.utils.logging import yLazyLogger
from y.utils.raw_calls import _totalSupplyReadable

logger = logging.getLogger(__name__)

@yLazyLogger(logger)
@lru_cache
def is_popsicle_lp(token_address: AnyAddressType) -> bool:
    # NOTE: contract to check for reference (mainnet): 0xd2C5A739ebfE3E00CFa88A51749d367d7c496CCf
    return has_methods(token_address, ['token0()(address)','token1()(address)','usersAmounts()((uint,uint))'])

@yLazyLogger(logger)
def get_price(token: AnyAddressType, block: Optional[Block] = None) -> Optional[UsdPrice]:
    address = convert.to_address(token)
    total_val = get_tvl(address, block)
    if total_val is None:
        return None
    total_supply = _totalSupplyReadable(address,block)
    return UsdPrice(total_val / total_supply)

@yLazyLogger(logger)
def get_tvl(token: AnyAddressType, block: Optional[Block] = None) -> Optional[UsdValue]:
    balances = get_balances(token, block)
    if balances is None:
        return None
    balance0, balance1 = balances
    return UsdValue(balance0.value_usd() + balance1.value_usd())

@yLazyLogger(logger)
def get_balances(token: AnyAddressType, block: Optional[Block] = None) -> Optional[Tuple[WeiBalance,WeiBalance]]:
    address = convert.to_address(token)
    methods = 'token0()(address)','token1()(address)','usersAmounts()((uint,uint))'
    calls = [Call(address, method, [[method,None]]) for method in methods]
    try:
        token0, token1, (balance0, balance1) = Multicall(calls, block_id=block)().values()
    except Exception as e:
        if call_reverted(e):
            return None
        elif str(e) == "not enough values to unpack (expected 3, got 2)":
            # TODO determine if this is regular behavior when no tvl in pool or if this is bug to fix
            return None
        raise
    balance0 = WeiBalance(balance0, token0, block=block)
    balance1 = WeiBalance(balance1, token1, block=block)
    return balance0, balance1
