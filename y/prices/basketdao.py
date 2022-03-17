
from brownie.convert.datatypes import EthAddress
from multicall import Call
from y.classes.common import ERC20, WeiBalance


def is_basketdao_index(address: EthAddress) -> bool:
    try:
        Call(address, 'getAssetsAndBalances()(address[],uint[])')()
        return True
    except:
        return False

def get_price(address: EthAddress, block: int = None):
    balances = [
        WeiBalance(balance, token, block)
        for balance, token
        in Call(address, 'getAssetsAndBalances()(address[],uint[])',block_id=block)()
    ]
    tvl = sum(bal.value_usd() for bal in balances)
    return tvl / ERC20(address).total_supply_readable(block=block)