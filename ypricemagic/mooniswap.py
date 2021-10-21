from brownie import ZERO_ADDRESS, chain, Contract, multicall, web3
from .utils.cache import memory
from .constants import weth
from .magic import get_price

if chain.id == 1:
    router = Contract("0xbAF9A5d4b0052359326A6CDAb54BABAa3a3A9643")
    gas_coin = weth
elif chain.id == 56:
    router = Contract("0xD41B24bbA51fAc0E4827b6F94C0D6DDeB183cD64")
    gas_coin = Contract("0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c") #wbnb

@memory.cache()
def is_mooniswap_pool(token):
    pools = router.getAllPools()
    return token in pools

def get_pool_price(token, block=None):
    token = Contract(token)
    if block >= 12336033 and chain.id == 1:
        with multicall(address=multicall.address, block_identifier = block):
            token0 = token.token0()
            token1 = token.token1()
            totalSupply = token.totalSupply() / 10 ** token.decimals()
            if token0 == ZERO_ADDRESS:
                token1 = Contract(token1)
                bal0 = web3.eth.get_balance(token.address) / 10 ** 18
                bal1 = token1.balanceOf(token) / 10 ** token1.decimals()
            elif token1 == ZERO_ADDRESS:
                token0 = Contract(token0)
                bal0 = token0.balanceOf(token) / 10 ** token0.decimals()
                bal1 = web3.eth.get_balance(token.address) / 10 ** 18
            else:
                token0, token1 = Contract(token0), Contract(token1)
                bal0 = token0.balanceOf(token) / 10 ** token0.decimals()
                bal1 = token1.balanceOf(token) / 10 ** token1.decimals()
    else:
        token0 = token.token0(block_identifier = block)
        token1 = token.token1(block_identifier = block)
        totalSupply = token.totalSupply(block_identifier = block) / 10 ** token.decimals(block_identifier = block)
        if token0 == ZERO_ADDRESS:
            token1 = Contract(token1)
            bal0 = web3.eth.get_balance(token.address, block_identifier = block) / 10 ** 18
            bal1 = token1.balanceOf(token, block_identifier = block) / 10 ** token1.decimals(block_identifier = block)
        elif token1 == ZERO_ADDRESS:
            token0 = Contract(token0)
            bal0 = token0.balanceOf(token, block_identifier = block) / 10 ** token0.decimals(block_identifier = block)
            bal1 = web3.eth.get_balance(token.address, block_identifier = block) / 10 ** 18
        else:
            token0, token1 = Contract(token0), Contract(token1)
            bal0 = token0.balanceOf(token,block_identifier = block) / 10 ** token0.decimals(block_identifier = block)
            bal1 = token1.balanceOf(token,block_identifier = block) / 10 ** token1.decimals(block_identifier = block)

    if token0 == ZERO_ADDRESS:
        token0 = gas_coin
    if token1 == ZERO_ADDRESS:
        token1 = gas_coin
    val0 = bal0 * get_price(token0.address, block)
    val1 = bal1 * get_price(token1.address, block)
    totalVal = val0 + val1
    price = totalVal / totalSupply
    return price
    
