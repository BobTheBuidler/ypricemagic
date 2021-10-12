from brownie import Contract, multicall
import ypricemagic.magic 

def is_gelato_pool(token):
    pool = Contract(token)
    return hasattr(pool, 'gelatoBalance0') and hasattr(pool, 'gelatoBalance1')

def get_price(token, block=None):
    pool = Contract(token)
    with multicall:
        token0 = pool.token0(block_identifier = block)
        token1 = pool.token1(block_identifier = block)
        balance0 = pool.gelatoBalance0(block_identifier = block)
        balance1 = pool.gelatoBalance1(block_identifier = block)
        totalSupply = pool.totalSupply(block_identifier = block)
        decimals = pool.decimals(block_identifier = block)
    balance0 /= 10 ** Contract(token0).decimals()
    balance1 /= 10 ** Contract(token1).decimals()
    totalSupply /= 10 ** decimals
    totalVal = balance0 * ypricemagic.magic.get_price(token0,block) + balance1 * ypricemagic.magic.get_price(token1,block)
    return totalVal / totalSupply
