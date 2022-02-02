
import logging

from y.contracts import Contract, has_methods
from y.decorators import log
from y.prices import magic
from y.utils.cache import memory
from y.utils.multicall import fetch_multicall

logger = logging.getLogger(__name__)

@log(logger)
@memory.cache()
def is_ib_token(address):
    return has_methods(address, ['debtShareToVal(uint)(uint)','debtValToShare(uint)(uint)'])

@log(logger)
def get_price(address, block=None):
    contract = Contract(address)
    token, total_bal, total_supply = fetch_multicall([contract,'token'],[contract,'totalToken'],[contract,'totalSupply'], block=block)
    token_decimals, pool_decimals = fetch_multicall([Contract(token),'decimals'],[contract,'decimals'], block=block)
    total_bal /= 10 ** token_decimals
    total_supply /= 10 ** pool_decimals
    share_price = total_bal/total_supply
    token_price = magic.get_price(token, block)
    price = share_price * token_price
    return price
