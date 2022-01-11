import ypricemagic.magic
from brownie import multicall
from ypricemagic.utils.contracts import Contract
from ypricemagic.utils.raw_calls import _decimals, _totalSupplyReadable


def is_gelato_pool(token_address: str) -> bool:
    pool = Contract(token_address)
    return hasattr(pool, 'gelatoBalance0') and hasattr(pool, 'gelatoBalance1')

def get_price(token_address: str, block=None):
    pool = Contract(token_address)
    with multicall:
        token0 = pool.token0(block_identifier = block)
        token1 = pool.token1(block_identifier = block)
        balance0 = pool.gelatoBalance0(block_identifier = block)
        balance1 = pool.gelatoBalance1(block_identifier = block)
    balance0 /= 10 ** _decimals(token0,block)
    balance1 /= 10 ** _decimals(token1,block)
    totalSupply = _totalSupplyReadable(token_address,block)
    totalVal = balance0 * ypricemagic.magic.get_price(token0,block) + balance1 * ypricemagic.magic.get_price(token1,block)
    return totalVal / totalSupply
