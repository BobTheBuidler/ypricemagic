from brownie import Contract
from ypricemagic import magic
from .utils.cache import memory

@memory.cache()
def is_eps_rewards_pool(token):
    token = Contract(token)
    return hasattr(token, 'lpStaker') and hasattr(token, 'rewardTokens')\
        and hasattr(token, 'rewardPerToken') and hasattr(token, 'minter')

def get_price(token, block=None):
    token = Contract(token)
    minter = Contract(token.minter(block_identifier=block))
    i, balances = 0, []
    while True:
        try:
            coin = minter.coins(i, block_identifier = block)
            balances.append((coin,minter.balances(i, block_identifier = block) / 10 ** Contract(coin).decimals(block_identifier = block)))
            i += 1
        except:
            break
    tvl = sum(balance * magic.get_price(coin, block) for coin, balance in balances)
    totalSupply = token.totalSupply(block_identifier = block) / 10 ** token.decimals(block_identifier=block)
    return tvl / totalSupply
    
