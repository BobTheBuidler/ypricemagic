from brownie import Contract
from cachetools.func import ttl_cache

from . import magic
from .utils.cache import memory
from .utils.events import decode_logs, get_logs_asap
from .utils.multicall2 import fetch_multicall
from .constants import usdc, weth
from .interfaces.balancer.WeightedPool import WeightedPoolABI
from joblib import Parallel, delayed


@memory.cache()
def is_balancer_pool(address):
    pool = Contract(address)
    required = {"getCurrentTokens", "getBalance", "totalSupply"}
    if set(pool.__dict__) & required == required:
        return True
    return False


@ttl_cache(ttl=600)
def list_pools_v2(block):
    topics = ['0x3c13bc30b8e878c53fd2a36b679409c073afd75950be43d8858768e956fbc20e'] 
    events = decode_logs(get_logs_asap('0xBA12222222228d8Ba445958a75a0704d566BF2C8', topics, from_block= 12272146, to_block=block))
    pools = [(event['poolAddress'],event['poolId']) for event in events]
    return pools


@ttl_cache(ttl=600)
def list_pools_for_token_v2(token, block):
    def query_pools(pool, block):
        for pooltoken in bal_vault_v2.getPoolTokens(pool[1], block_identifier = block)[0]:
            if pooltoken == token:
                pools.append(pool)
    
    pools, bal_vault_v2 = [], Contract('0xBA12222222228d8Ba445958a75a0704d566BF2C8')
    Parallel(4,'threading')(delayed(query_pools)(pool, block) for pool in list_pools_v2(block))
    return pools


@ttl_cache(ttl=600)
def get_price(token, block=None):
    if is_balancer_pool(token):
        pool = Contract(token)
        tokens, supply = fetch_multicall([pool, "getCurrentTokens"], [pool, "totalSupply"], block=block)
        supply = supply / 1e18
        balances = fetch_multicall(*[[pool, "getBalance", token] for token in tokens], block=block)
        balances = [balance / 10 ** Contract(token).decimals() for balance, token in zip(balances, tokens)]
        total = sum(balance * magic.get_price(token, block=block) for balance, token in zip(balances, tokens))
        return total / supply

    # NOTE: If token is not BPTv1 (or BPTv2, but this isn't implemented yet...), continue  
    if block < 12272146: # NOTE: skips if block queried < v2 deploy block
        return None

    def query_pool_price(pooladdress, poolid):
        pooltokens = Contract('0xBA12222222228d8Ba445958a75a0704d566BF2C8').getPoolTokens(poolid, block_identifier = block)

        try:
            poolcontract = Contract(pooladdress)
        except:
            poolcontract = Contract.from_abi("Balancer Pool V2", pooladdress, WeightedPoolABI)

        try:
            weights = poolcontract.getNormalizedWeights(block_identifier = block)
        except ValueError:
            weights = []
            for pooltoken in pooltokens[0]:
                weights.append(1)
            
        pooltokens = list(zip(pooltokens[0],pooltokens[1], weights))
        wethBal, usdcBal, pairedTokenBal = None, None, None
        for pooltoken, balance, weight in pooltokens:
            if pooltoken == usdc:
                usdcBal = balance
                usdcWeight = weight
            if pooltoken == weth:
                wethBal = balance
                wethWeight = weight
            if pooltoken == token:
                tokenBal = balance
                tokenWeight = weight
            if len(pooltokens) == 2 and pooltoken != token:
                pairedTokenBal = balance
                pairedTokenWeight = weight
                pairedToken = pooltoken
                
        if usdcBal:
            usdcValueUSD = (usdcBal / 10 ** 6) * magic.get_price(usdc, block)
            tokenValueUSD = usdcValueUSD / usdcWeight * tokenWeight
            tokenPrice = tokenValueUSD / (tokenBal / 10 ** Contract(token).decimals(block_identifier = block))
        elif wethBal:
            wethValueUSD = (wethBal / 10 ** 18) * magic.get_price(weth, block)
            tokenValueUSD = wethValueUSD / wethWeight * tokenWeight
            tokenPrice = tokenValueUSD / (tokenBal / 10 ** Contract(token).decimals(block_identifier = block))
        elif pairedTokenBal:
            pairedTokenValueUSD = (pairedTokenBal / 10 ** Contract(pairedToken).decimals(block_identifier = block)) * magic.get_price(pairedToken, block)
            tokenValueUSD = pairedTokenValueUSD / pairedTokenWeight * tokenWeight
            tokenPrice = tokenValueUSD / (tokenBal / 10 ** Contract(token).decimals(block_identifier = block))

        nonlocal priceSum, priceCt
        priceSum += tokenPrice
        priceCt += 1
    
    priceSum, priceCt = 0, 0
    Parallel(4,'threading')(delayed(query_pool_price)(pooladdress, poolid) for pooladdress, poolid in list_pools_for_token_v2(token, block))
    if priceCt > 0:
        return priceSum/priceCt
    return None



