import logging
from functools import lru_cache
from typing import Union

import brownie
from eth_typing.evm import Address
from y.balancer.balancer import balancer
from y.chainlink.chainlink import chainlink
from y.constants import STABLECOINS
from y.contracts import Contract
from y.curve.curve import curve
from y.decorators import log
from y.prices import (basketdao, belt, convex, cream, ellipsis, froyo, gelato,
                      ib, mooniswap, mstablefeederpool, one_to_one, piedao, saddle,
                      tokensets, wsteth, yearn)
from y.prices.aave import aave
from y.prices.compound import compound
from y.prices.genericamm import generic_amm
from y.prices.synthetix import synthetix
from y.uniswap.uniswap import uniswap

logger = logging.getLogger(__name__)

@log(logger)
@lru_cache(maxsize=None)
def check_bucket(
    token_address: Union[str, Address, brownie.Contract, Contract]
    ):

    if type(token_address) != str:
        token_address = str(token_address)

    # these require neither calls to the chain nor contract initialization
    if token_address == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE":       return 'wrapped gas coin'
    elif token_address in STABLECOINS:                                      return 'stable usd'
    elif one_to_one.is_one_to_one_token(token_address):                     return 'one to one'
    
    elif wsteth.is_wsteth(token_address):                                   return 'wsteth'
    elif cream.is_creth(token_address):                                     return 'creth'
    elif belt.is_belt_lp(token_address):                                    return 'belt lp'

    elif froyo.is_froyo(token_address):                                     return 'froyo'
    elif aave.is_atoken(token_address):                                     return 'atoken'
    elif convex.is_convex_lp(token_address):                                return 'convex'

    # these just require calls
    elif balancer.is_balancer_pool(token_address):                          return 'balancer pool'
    elif yearn.is_yearn_vault(token_address):                               return 'yearn or yearn-like'
    elif ib.is_ib_token(token_address):                                     return 'ib token'

    elif gelato.is_gelato_pool(token_address):                              return 'gelato'
    elif piedao.is_pie(token_address):                                      return 'piedao lp'
    elif tokensets.is_token_set(token_address):                             return 'token set'

    elif ellipsis.is_eps_rewards_pool(token_address):                       return 'ellipsis lp'
    elif mstablefeederpool.is_mstable_feeder_pool(token_address):           return 'mstable feeder pool'
    elif saddle.is_saddle_lp(token_address):                                return 'saddle'

    elif basketdao.is_basketdao_index(token_address):                       return 'basketdao'

    # these just require contract initialization
    elif token_address in generic_amm:                                      return 'generic amm'

    # these require both calls and contract initializations
    elif uniswap.is_uniswap_pool(token_address):                            return 'uni or uni-like lp'
    elif mooniswap.is_mooniswap_pool(token_address):                        return 'mooniswap lp'
    elif token_address in compound:                                         return 'compound'
    elif token_address in curve:                                            return 'curve lp'
    elif token_address in chainlink:                                        return 'chainlink feed'
    elif token_address in synthetix:                                        return 'synthetix'
