import logging

from brownie import Contract
from cachetools.func import ttl_cache
from joblib import Parallel, delayed

from ypricemagic.utils.utils import (PROXIES_reverse_lookup,
                                     get_decimals_with_override)

from . import magic
from .constants import PROXIES, dai, usdc, wbtc, weth
from .interfaces.balancer.WeightedPool import WeightedPoolABI
from .utils.cache import memory
from .utils.events import decode_logs, get_logs_asap
from .utils.multicall2 import fetch_multicall
from .utils.utils import get_decimals_with_override


@memory.cache()
def is_balancer_pool(address):
    pool = Contract(address)
    required = {"getCurrentTokens", "getBalance", "totalSupply"}
    return set(pool.__dict__) & required == required


@ttl_cache(ttl=600)
def list_pools_v2(block):
    topics = ['0x3c13bc30b8e878c53fd2a36b679409c073afd75950be43d8858768e956fbc20e']
    events = decode_logs(get_logs_asap('0xBA12222222228d8Ba445958a75a0704d566BF2C8', topics, from_block= 12272146, to_block=block))
    return [(event['poolAddress'],event['poolId']) for event in events]


@ttl_cache(ttl=1800)
def list_pools_for_token_v2(token, block):
    def query_pools(pool, block):
        for pooltoken in bal_vault_v2.getPoolTokens(pool[1], block_identifier = block)[0]:
            if pooltoken == token:
                pools.append(pool)
    
    pools, bal_vault_v2 = [], Contract('0xBA12222222228d8Ba445958a75a0704d566BF2C8')
    Parallel(4,'threading')(delayed(query_pools)(pool, block) for pool in list_pools_v2(block))
    return pools


def get_pool_price_v1(token, block=None):
    pool = Contract(token)
    tokens, supply = fetch_multicall([pool, "getCurrentTokens"], [pool, "totalSupply"], block=block)
    tokens = list(tokens)
    for position, token in enumerate(tokens):
        if token in PROXIES:
            tokens[position] = PROXIES[token]
    logging.debug(f'pool tokens: {tokens}')
    supply = supply / 1e18
    if supply == 0:
        return None
    balances = list(fetch_multicall(*[[pool, "getBalance", token] for token in tokens], block=block))
    for position, balance in enumerate(balances):
        if balance is None:
            balances[position] = 0
    balances = [balance / 10 ** get_decimals_with_override(token, block) for balance, token in zip(balances, tokens)]
    logging.debug(f'balancer pool balances: {balances}')
    total = sum([balance * magic.get_price(token, block=block) for balance, token in zip(balances, tokens)])
    return total / supply

def get_token_price_v2(token, block=None):
    def query_pool_price(pooladdress, poolid):
        pooltokens = Contract('0xBA12222222228d8Ba445958a75a0704d566BF2C8').getPoolTokens(poolid, block_identifier = block)

        try:
            poolcontract = Contract(pooladdress)
        except:
            poolcontract = Contract.from_abi("Balancer Pool V2", pooladdress, WeightedPoolABI)

        try:
            weights = poolcontract.getNormalizedWeights(block_identifier = block)
        except ValueError:
            weights = [1 for _ in pooltokens[0]]
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

def get_token_price_v1(token, block=None):
    def get_output(scale=1):
        def check_against(out, scale=1):
            totalOutput = exchange_proxy.viewSplitExactIn(
                token, out, 10 ** get_decimals_with_override(token) * scale, 32 # NOTE: 32 is max
                , block_identifier = block
            )['totalOutput']
            return out, totalOutput

        try:
            out, totalOutput = check_against(weth)
        except ValueError:
            try:
                out, totalOutput = check_against(dai)
            except ValueError:
                try:
                    out, totalOutput = check_against(usdc)
                except ValueError:
                    try:
                        out, totalOutput = check_against(wbtc)
                    except ValueError:
                        out = None
                        totalOutput = None
        return out, totalOutput

    exchange_proxy = Contract('0x3E66B66Fd1d0b02fDa6C811Da9E0547970DB2f21')

    # NOTE: Reverse lookup
    # NOTE: we might not need this when all is said and done
    logging.debug(f'token: {token}')
    token = PROXIES_reverse_lookup(token)
    logging.debug(f'token after proxy reverse lookup: {token}')
    price = None
    out, totalOutput = get_output()
    if out:
        price = (totalOutput / 10 ** Contract(out).decimals()) * magic.get_price(out, block)
    if not price: # Can we get an output if we try smaller size?
        scale = 0.5
        out, totalOutput = get_output(scale) 
    if out:
        price = (totalOutput / 10 ** Contract(out).decimals()) * magic.get_price(out, block) / scale
    if not price: # How about now? 
        scale = 0.1
        out, totalOutput = get_output(scale)
    if out:
        price = (totalOutput / 10 ** Contract(out).decimals()) * magic.get_price(out, block) / scale
    if not price:
        return
    logging.debug('price found via balancer v1')
    return price
        

@ttl_cache(ttl=600)
def get_price(token, block=None):
    if is_balancer_pool(token):
        return get_pool_price_v1(token, block)
    # NOTE: If token is not BPTv1, continue  (or BPTv2, but this isn't implemented yet...)
    
    # NOTE: Only query v2 if block queried > v2 deploy block plus 100000 blocks
    #       (to let v2 gain some liquidity before we query prices from there, we still have v1 available)
    
    # NOTE Gotta troubleshoot brownie Contract db
    # if not block or block > 12272146: #+ 100000: 
    #    return get_token_price_v2(token, block)

    if not block or block > 10730576:   # v1 registry deploy block
        return get_token_price_v1(token, block)
    return



