from brownie import Contract
from .utils.multicall2 import fetch_multicall
from .utils.cache import memory
from ypricemagic import magic

@memory.cache()
def is_ib_token(address):
    token = Contract(address)
    return hasattr(token, 'debtShareToVal') and hasattr(token, 'debtValToShare')

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
