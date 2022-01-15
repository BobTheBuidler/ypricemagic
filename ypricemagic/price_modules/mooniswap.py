
from brownie import ZERO_ADDRESS, chain, multicall, web3
from y.constants import weth
from y.contracts import Contract
from y.utils.cache import memory
from ypricemagic import magic
from ypricemagic.utils.multicall import multicall2
from ypricemagic.utils.raw_calls import _decimals, _totalSupplyReadable

if chain.id == 1:
    router = Contract("0xbAF9A5d4b0052359326A6CDAb54BABAa3a3A9643")
    gas_coin = weth
elif chain.id == 56:
    router = Contract("0xD41B24bbA51fAc0E4827b6F94C0D6DDeB183cD64")
    gas_coin = Contract("0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c") #wbnb
else: 
    router = None
    gas_coin = None

@memory.cache()
def is_mooniswap_pool(token):
    if router is None: return False
    return router.isPool(token)

def get_pool_price(token_address, block=None):
    token = Contract(token_address)
    if block >= 12336033 and chain.id == 1:
        with multicall(address=multicall2.address, block_identifier = block):
            token0_address = token.token0()
            token1_address = token.token1()
            totalSupply = _totalSupplyReadable(token_address,block)
            if token0_address == ZERO_ADDRESS:
                token1 = Contract(token1_address)
                bal0 = web3.eth.get_balance(token.address) / 10 ** 18
                bal1 = token1.balanceOf(token) / 10 ** _decimals(token1_address,block)
            elif token1_address == ZERO_ADDRESS:
                token0 = Contract(token0_address)
                bal0 = token0.balanceOf(token) / 10 ** _decimals(token0_address,block)
                bal1 = web3.eth.get_balance(token.address) / 10 ** 18
            else:
                token0, token1 = Contract(token0_address), Contract(token1_address)
                bal0 = token0.balanceOf(token) / 10 ** _decimals(token0_address,block)
                bal1 = token1.balanceOf(token) / 10 ** _decimals(token1_address,block)
    else:
        token0_address = token.token0(block_identifier = block)
        token1_address = token.token1(block_identifier = block)
        totalSupply = _totalSupplyReadable(token_address,block)
        if token0_address == ZERO_ADDRESS:
            token1 = Contract(token1_address)
            bal0 = web3.eth.get_balance(token.address, block_identifier = block) / 10 ** 18
            bal1 = token1.balanceOf(token, block_identifier = block) / 10 ** _decimals(token1_address,block)
        elif token1_address == ZERO_ADDRESS:
            token0 = Contract(token0_address)
            bal0 = token0.balanceOf(token, block_identifier = block) / 10 ** _decimals(token0_address,block)
            bal1 = web3.eth.get_balance(token.address, block_identifier = block) / 10 ** 18
        else:
            token0, token1 = Contract(token0_address), Contract(token1_address)
            bal0 = token0.balanceOf(token,block_identifier = block) / 10 ** _decimals(token0_address,block)
            bal1 = token1.balanceOf(token,block_identifier = block) / 10 ** _decimals(token1_address,block)

    if token0_address == ZERO_ADDRESS:
        token0 = gas_coin
    if token1_address == ZERO_ADDRESS:
        token1 = gas_coin
    val0 = bal0 * magic.get_price(token0.address, block)
    val1 = bal1 * magic.get_price(token1.address, block)
    totalVal = val0 + val1
    price = totalVal / totalSupply
    return price
    
