
from y.contracts import Contract
from y.utils.cache import memory
from ypricemagic import magic
from ypricemagic.utils.raw_calls import _decimals, _totalSupplyReadable


@memory.cache()
def is_eps_rewards_pool(token_address: str) -> bool:
    token = Contract(token_address)
    methods = ['lpStaker','rewardTokens','rewardPerToken','minter']
    return all(hasattr(token,method) for method in methods)

def get_price(token_address: str, block=None):
    token = Contract(token_address)
    minter = Contract(token.minter(block_identifier=block))
    i, balances = 0, []
    while True:
        try:
            coin = minter.coins(i, block_identifier = block)
            balances.append((coin,minter.balances(i, block_identifier = block) / 10 ** _decimals(coin,block)))
            i += 1
        except:
            break
    tvl = sum(balance * magic.get_price(coin, block) for coin, balance in balances)
    totalSupply = _totalSupplyReadable(token_address,block)
    return tvl / totalSupply
    
