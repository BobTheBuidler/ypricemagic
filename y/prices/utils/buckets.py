import logging
from functools import lru_cache

from y import convert
from y.constants import STABLECOINS
from y.decorators import log
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
from y.typing import AnyAddressType

logger = logging.getLogger(__name__)

@log(logger)
@lru_cache(maxsize=None)
def check_bucket(
    token_address: AnyAddressType
    ) -> str:

    token_address = convert.to_address(token_address)

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
    elif balancer_multiplexer.is_balancer_pool(token_address):              return 'balancer pool'
    elif yearn.is_yearn_vault(token_address):                               return 'yearn or yearn-like'
    elif ib.is_ib_token(token_address):                                     return 'ib token'

    elif gelato.is_gelato_pool(token_address):                              return 'gelato'
    elif piedao.is_pie(token_address):                                      return 'piedao lp'
    elif tokensets.is_token_set(token_address):                             return 'token set'

    elif ellipsis.is_eps_rewards_pool(token_address):                       return 'ellipsis lp'
    elif mstablefeederpool.is_mstable_feeder_pool(token_address):           return 'mstable feeder pool'
    elif saddle.is_saddle_lp(token_address):                                return 'saddle'

    elif basketdao.is_basketdao_index(token_address):                       return 'basketdao'
    elif popsicle.is_popsicle_lp(token_address):                            return 'popsicle'

    # these just require contract initialization
    elif token_address in generic_amm:                                      return 'generic amm'

    # these require both calls and contract initializations
    elif uniswap_multiplexer.is_uniswap_pool(token_address):                return 'uni or uni-like lp'
    elif mooniswap.is_mooniswap_pool(token_address):                        return 'mooniswap lp'
    elif token_address in compound:                                         return 'compound'
    elif token_address in curve:                                            return 'curve lp'
    elif token_address in chainlink:                                        return 'chainlink feed'
    elif token_address in synthetix:                                        return 'synthetix'
