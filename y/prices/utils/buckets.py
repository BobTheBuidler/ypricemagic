import logging

import a_sync

from y import convert
from y.constants import STABLECOINS
from y.datatypes import AnyAddressType
from y.prices import convex, one_to_one, popsicle, yearn
from y.prices.band import band
from y.prices.chainlink import chainlink
from y.prices.gearbox import gearbox
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

logger = logging.getLogger(__name__)


@a_sync.a_sync(default='sync', cache_type='memory')
async def check_bucket(
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
    elif await aave.is_atoken(token_address, sync=False):                   return 'atoken'
    elif convex.is_convex_lp(token_address):                                return 'convex'

    # these just require calls
    elif await balancer_multiplexer.is_balancer_pool(token_address, sync=False):  return 'balancer pool'
    elif await ib.is_ib_token(token_address, sync=False):                         return 'ib token'

    elif await gelato.is_gelato_pool(token_address, sync=False):                        return 'gelato'
    elif await piedao.is_pie(token_address, sync=False):                          return 'piedao lp'
    elif await tokensets.is_token_set(token_address, sync=False):           return 'token set'

    elif await ellipsis.is_eps_rewards_pool(token_address, sync=False):           return 'ellipsis lp'
    elif await mstablefeederpool.is_mstable_feeder_pool(token_address, sync=False):     return 'mstable feeder pool'
    elif await saddle.is_saddle_lp(token_address, sync=False):                    return 'saddle'

    elif await basketdao.is_basketdao_index(token_address, sync=False):     return 'basketdao'
    elif await popsicle.is_popsicle_lp(token_address, sync=False):                return 'popsicle'

    # these require both calls and contract initializations
    elif await uniswap_multiplexer.is_uniswap_pool(token_address, sync=False):    return 'uni or uni-like lp'
    elif gearbox and await gearbox.is_diesel_token(token_address, sync=False):    return 'gearbox'

    # this just requires contract initialization but should go behind uniswap
    elif await aave.is_wrapped_atoken(token_address, sync=False):           return 'wrapped atoken'
    elif token_address in generic_amm:                                      return 'generic amm'
    elif await mooniswap.is_mooniswap_pool(token_address, sync=False):      return 'mooniswap lp'
    elif await compound.is_compound_market(token_address, sync=False):      return 'compound'
    elif await _chainlink_and_band(token_address):                          return 'chainlink and band'
    elif chainlink and await chainlink.has_feed(token_address, sync=False): return 'chainlink feed'
    elif synthetix and await synthetix.is_synth(token_address, sync=False): return 'synthetix'
    elif await yearn.is_yearn_vault(token_address, sync=False):             return 'yearn or yearn-like'
    elif await curve.get_pool(token_address, sync=False):                   return 'curve lp'

async def _chainlink_and_band(token_address) -> bool:
    """ We only really need band for a short period in the beginning of fantom's history, and then we will default to chainlink once available. """
    return chainlink and await chainlink.has_feed(token_address, sync=False) and token_address in band