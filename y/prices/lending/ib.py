
import logging
from typing import Optional

from y import convert
from y.contracts import Contract, has_methods
from y.datatypes import UsdPrice
from y.decorators import log
from y.prices import magic
from y.typing import AnyAddressType, Block
from y.utils.cache import memory
from y.utils.multicall import fetch_multicall

logger = logging.getLogger(__name__)

@log(logger)
@memory.cache()
def is_ib_token(token: AnyAddressType) -> bool:
    return has_methods(token, ['debtShareToVal(uint)(uint)','debtValToShare(uint)(uint)'])

@log(logger)
def get_price(token: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
    address = convert.to_address(token)
    contract = Contract(address)
    token, total_bal, total_supply = fetch_multicall([contract,'token'],[contract,'totalToken'],[contract,'totalSupply'], block=block)
    token_decimals, pool_decimals = fetch_multicall([Contract(token),'decimals'],[contract,'decimals'], block=block)
    total_bal /= 10 ** token_decimals
    total_supply /= 10 ** pool_decimals
    share_price = total_bal/total_supply
    token_price = magic.get_price(token, block)
    price = share_price * token_price
    return price
