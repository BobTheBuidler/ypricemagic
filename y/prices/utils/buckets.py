import logging
from functools import lru_cache

from async_lru import alru_cache
from multicall.utils import await_awaitable
from y import convert
from y.constants import STABLECOINS
from y.datatypes import AnyAddressType
from y.prices import convex, one_to_one, popsicle, yearn
from y.prices.chainlink import chainlink
from y.prices.dex import mooniswap
from y.prices.dex.balancer import balancer_multiplexer
from y.prices.dex.genericamm import generic_amm
from y.prices.dex.uniswap import uniswap_multiplexer
from y.prices.eth_derivs import creth, wsteth
from y.prices.lending import ib
from y.prices.lending.aave import aave
from y.prices.lending.compound import compound
from y.prices.stable_swap import (belt, ellipsis, froyo, mstablefeederpool,
                                  saddle)
from y.prices.stable_swap.curve import curve
from y.prices.synthetix import synthetix
from y.prices.tokenized_fund import basketdao, gelato, piedao, tokensets
from y.utils.logging import yLazyLogger

logger = logging.getLogger(__name__)

@lru_cache(maxsize=None)
def check_bucket(
    token: AnyAddressType
    ) -> str:
    return await_awaitable(check_bucket_async(token))

@yLazyLogger(logger)
@alru_cache(maxsize=None)
async def check_bucket_async(
    token: AnyAddressType
    ) -> str:

    token_address = convert.to_address(token)

    # these require neither calls to the chain nor contract initialization
    if token_address == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE":       return 'wrapped gas coin'
    elif token_address in STABLECOINS:                                      return 'stable usd'
    elif one_to_one.is_one_to_one_token(token_address):                     return 'one to one'
    
    elif wsteth.is_wsteth(token_address):                                   return 'wsteth'
    elif creth.is_creth(token_address):                                     return 'creth'
    elif belt.is_belt_lp(token_address):                                    return 'belt lp'

    elif froyo.is_froyo(token_address):                                     return 'froyo'
    elif aave.is_atoken(token_address):                                     return 'atoken'
    elif convex.is_convex_lp(token_address):                                return 'convex'

    # these just require calls
    elif await balancer_multiplexer.is_balancer_pool_async(token_address):  return 'balancer pool'
    elif await ib.is_ib_token_async(token_address):                         return 'ib token'

    elif await gelato.is_gelato_pool_async(token_address):                  return 'gelato'
    elif await piedao.is_pie_async(token_address):                          return 'piedao lp'
    elif await tokensets.is_token_set_async(token_address):                 return 'token set'

    elif await ellipsis.is_eps_rewards_pool_async(token_address):           return 'ellipsis lp'
    elif await mstablefeederpool.is_mstable_feeder_pool(token_address):     return 'mstable feeder pool'
    elif await saddle.is_saddle_lp_async(token_address):                    return 'saddle'

    elif await basketdao.is_basketdao_index_async(token_address):           return 'basketdao'
    elif await popsicle.is_popsicle_lp_async(token_address):                return 'popsicle'


    # these require both calls and contract initializations
    elif await uniswap_multiplexer.is_uniswap_pool_async(token_address):    return 'uni or uni-like lp'
    # this just requires contract initialization but should go behind uniswap
    elif token_address in generic_amm:                                      return 'generic amm'
    elif await mooniswap.is_mooniswap_pool_async(token_address):            return 'mooniswap lp'
    elif await compound.is_compound_market_async(token_address):            return 'compound'
    elif token_address in curve:                                            return 'curve lp'
    elif chainlink and await chainlink.has_feed(token_address):                           return 'chainlink feed'
    elif synthetix and await synthetix.is_synth(token_address):             return 'synthetix'
    elif await yearn.is_yearn_vault_async(token_address):                   return 'yearn or yearn-like'
