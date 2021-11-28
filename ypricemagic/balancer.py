from inspect import Attribute
import logging

from brownie import Contract, chain
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

chainid = chain.id

if chainid == 1:
    VAULT_V2 = Contract('0xBA12222222228d8Ba445958a75a0704d566BF2C8')
if chainid == 250:
    VAULT_V2 = Contract('0x20dd72Ed959b6147912C2e529F0a0C651c33c9ce')

@memory.cache()
def is_balancer_pool_v1(address):
    pool = Contract(address)
    required = {"getCurrentTokens", "getBalance", "totalSupply"}
    return set(pool.__dict__) & required == required

@memory.cache()
def is_balancer_pool_v2(address):
    pool = Contract(address)
    required = {'getPoolId','getPausedState','getSwapFeePercentage'}
    return set(pool.__dict__) & required == required

@memory.cache()
def is_balancer_pool(address):
    return is_balancer_pool_v1(address) or is_balancer_pool_v2(address)


@ttl_cache(ttl=600)
def list_pools_v2(block):
    topics = ['0x3c13bc30b8e878c53fd2a36b679409c073afd75950be43d8858768e956fbc20e']
    events = decode_logs(get_logs_asap(VAULT_V2.address, topics, to_block=block))
    return [(event['poolAddress'],event['poolId']) for event in events]


@ttl_cache(ttl=1800)
def deepest_pool_for_token_v2(token, block):
    pools = list_pools_v2(block)
    pools_info = fetch_multicall(*[[VAULT_V2,'getPoolTokens',poolId] for poolAddress, poolId in pools])
    pools = [poolAddress for poolAddress, poolId in pools]
    pools = zip(pools,pools_info)
    deepest_pool = {'pool': None, 'balance': 0}
    for pool, info in pools:
        if str(info) != "((), (), 0)":
            for i in range(len(info[0])):
                _token, balance = info[0][i], info[1][i]
                try: 
                    name = Contract(pool).__dict__['_build']['contractName']
                except:
                    name = 'proceed'
                if _token == token and balance > deepest_pool['balance'] and name not in ['ConvergentCurvePool','MetaStablePool']:
                    deepest_pool = {'pool': pool, 'balance': balance}
    return deepest_pool['pool']


def _magic_get_price(token, block=None):
    try:
        return magic.get_price(token, block)
    except magic.PriceError:
        return 0


def get_pool_price_v1(token, block=None):
    pool = Contract(token)
    tokens, supply = fetch_multicall([pool, "getCurrentTokens"], [pool, "totalSupply"], block=block)
    tokens = list(tokens)
    logging.debug(f'pool tokens: {tokens}')
    if supply == 0:
        return 0
    supply = supply / 1e18
    balances = list(fetch_multicall(*[[pool, "getBalance", token] for token in tokens], block=block))
    for position, balance in enumerate(balances):
        if balance is None:
            balances[position] = 0
    balances = [balance / 10 ** get_decimals_with_override(token, block) for balance, token in zip(balances, tokens)]
    logging.debug(f'balancer pool balances: {balances}')
    total = sum([balance * _magic_get_price(token, block=block) for balance, token in zip(balances, tokens)])
    return total / supply

def get_pool_price_v2(pool, block=None):
    pool = Contract(pool)
    poolId, vault, totalSupply, decimals = fetch_multicall([pool, "getPoolId"], [pool, "getVault"], [pool, 'totalSupply'], [pool, 'decimals'], block=block)
    vault = Contract(vault)
    totalSupply = totalSupply / 10 ** decimals
    tokens, balances, lastChangedBlock = vault.getPoolTokens(poolId, block_identifier = block)
    token_decimals = fetch_multicall(*[[Contract(token),'decimals'] for token in tokens], block=block)
    balances = (balance / 10 ** decimal for balance, decimal in zip(balances, token_decimals))
    prices = Parallel(4,'threading')(delayed(magic.get_price)(_token, block) for _token in tokens)
    tvl = sum(balance * price for balance, price in zip(balances, prices))
    price = tvl / totalSupply
    return price
    

def get_token_price_v2(token, block=None):
    def query_pool_price(pooladdress, poolid):
        poolcontract = Contract(pooladdress)
        pooltokens = VAULT_V2.getPoolTokens(poolid, block_identifier = block)
        try:
            weights = poolcontract.getNormalizedWeights(block_identifier = block)
        except (AttributeError,ValueError):
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

        tokenPrice = None
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
        return tokenPrice
    
    deepest_pool = deepest_pool_for_token_v2(token, block)
    if not deepest_pool:
        return
    try:
        deepest_pool = Contract(deepest_pool)
    except:
        deepest_pool = Contract.from_abi("Balancer Pool V2", deepest_pool, WeightedPoolABI)
    poolId = deepest_pool.getPoolId(block_identifier = block)
    return query_pool_price(deepest_pool.address, poolId)

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
    if chainid == 1: # chainid will always be 1, balancer v1 is only on mainnet
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
        logging.debug('price found via balancer v1')
        return price
    # Can we get an output if we try smaller size?
    scale = 0.5
    out, totalOutput = get_output(scale) 
    if out:
        price = (totalOutput / 10 ** Contract(out).decimals()) * magic.get_price(out, block) / scale
        logging.debug('price found via balancer v1')
        return price
    # How about now? 
    scale = 0.1
    out, totalOutput = get_output(scale)
    if out:
        price = (totalOutput / 10 ** Contract(out).decimals()) * magic.get_price(out, block) / scale
        logging.debug('price found via balancer v1')
        return price
    else:
        return
        

@ttl_cache(ttl=600)
def get_price(token, block=None):
    if is_balancer_pool_v1(token):
        return get_pool_price_v1(token, block)

    if is_balancer_pool_v2(token):
        return get_pool_price_v2(token, block)

    price = None    
    # NOTE: Only query v2 if block queried > v2 deploy block plus 100000 blocks
    if (
        (chainid == 1 and (not block or block > 12272146 + 100000))
        or (chainid == 250 and (not block or block > 16896080))
        ): # lets get some liquidity before we use this as price source
        price = get_token_price_v2(token, block)
    if not price and chainid == 1:      
        if not block or block > 10730576:   # v1 registry deploy block
            price = get_token_price_v1(token, block)
    return price



