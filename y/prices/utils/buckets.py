import asyncio
import logging
from typing import Awaitable, Callable, Tuple

import a_sync

from y import convert
from y.constants import STABLECOINS
from y.datatypes import Address, AnyAddressType
from y.prices import convex, one_to_one, popsicle, solidex, yearn
from y.prices.band import band
from y.prices.chainlink import chainlink
from y.prices.dex import mooniswap
from y.prices.dex.balancer import balancer_multiplexer
from y.prices.dex.genericamm import generic_amm
from y.prices.dex.uniswap import uniswap_multiplexer
from y.prices.eth_derivs import creth, wsteth
from y.prices.gearbox import gearbox
from y.prices.lending import ib
from y.prices.lending.aave import aave
from y.prices.lending.compound import compound
from y.prices.stable_swap import (belt, ellipsis, froyo, mstablefeederpool,
                                  saddle)
from y.prices.stable_swap.curve import curve
from y.prices.synthetix import synthetix
from y.prices.tokenized_fund import basketdao, gelato, piedao, tokensets
from y.utils.logging import get_price_logger

logger = logging.getLogger(__name__)

@a_sync.a_sync(default='sync', cache_type='memory')
async def check_bucket(
    token: AnyAddressType
    ) -> str:

    import y._db.utils.token as db

    token_address = convert.to_address(token)
    logger = get_price_logger(token_address, block=None, extra='buckets')
    
    bucket = await db.get_bucket(token_address)
    if bucket:
        logger.debug('returning bucket %s from ydb', bucket)
        return bucket

    # these require neither calls to the chain nor contract initialization, just string comparisons (pretty sure)
    for bucket, check in string_matchers.items():
        if check(token):
            logger.debug("%s is %s", token_address, bucket)
            await db.set_bucket(token, bucket)
            return bucket
        else:
            logger.debug("%s is not %s", token_address, bucket)

    # check these first, these just require calls
    futs = [asyncio.ensure_future(_check_bucket_helper(bucket, check, token_address)) for bucket, check in calls_only.items()]
    for fut in asyncio.as_completed(futs):
        try:
            bucket, is_member = await fut
        except Exception as e:
            logger.warning("%s when checking %s. This will probably not impact your run.", e, fut)
            logger.warning(e, exc_info=True)
            continue

        if is_member:
            logger.debug("%s is %s", token_address, bucket)
            for fut in futs:
                fut.cancel()
            await db.set_bucket(token, bucket)
            return bucket
        else:
            logger.debug("%s is not %s", token_address, bucket)
            bucket = None

    # TODO: Refactor the below like the above
    # these require both calls and contract initializations
    if await solidex.is_solidex_deposit(token_address, sync=False):
        bucket = 'solidex'
    if await uniswap_multiplexer.is_uniswap_pool(token_address, sync=False):
        bucket = 'uni or uni-like lp'
    elif gearbox and await gearbox.is_diesel_token(token_address, sync=False):
        bucket = 'gearbox'

    # this just requires contract initialization but should go behind uniswap
    elif await aave.is_wrapped_atoken_v2(token_address, sync=False):
        bucket = 'wrapped atoken v2'
    elif await aave.is_wrapped_atoken_v3(token_address, sync=False):
        bucket = 'wrapped atoken v3'
    elif token_address in generic_amm:                                      
        bucket = 'generic amm'
    elif await mooniswap.is_mooniswap_pool(token_address, sync=False):      
        bucket = 'mooniswap lp'
    elif await compound.is_compound_market(token_address, sync=False):      
        bucket = 'compound'
    elif await _chainlink_and_band(token_address):                          
        bucket = 'chainlink and band'
    elif chainlink and await chainlink.has_feed(token_address, sync=False): 
        bucket = 'chainlink feed'
    elif synthetix and await synthetix.is_synth(token_address, sync=False): 
        bucket = 'synthetix'
    elif await yearn.is_yearn_vault(token_address, sync=False):             
        bucket = 'yearn or yearn-like'
    elif curve and await curve.get_pool(token_address, sync=False):                   
        bucket = 'curve lp'
    logger.debug("%s bucket is %s", token_address, bucket)
    if bucket:
        await db.set_bucket(token, bucket)
    return bucket

# these require neither calls to the chain nor contract initialization, just string comparisons (pretty sure)
string_matchers = {
    'wrapped gas coin': lambda address: address == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
    'stable usd': lambda address: address in STABLECOINS,
    'one to one': one_to_one.is_one_to_one_token,
    'wsteth': wsteth.is_wsteth,
    'creth': creth.is_creth,
    'belt lp': belt.is_belt_lp,
    'froyo': froyo.is_froyo,
    'convex': convex.is_convex_lp,
}

# these just require calls
calls_only = {
    'atoken': aave.is_atoken,
    'balancer pool': balancer_multiplexer.is_balancer_pool,
    'ib token': ib.is_ib_token,
    'gelato': gelato.is_gelato_pool,
    'piedao lp': piedao.is_pie,
    'token set': tokensets.is_token_set,
    'ellipsis lp': ellipsis.is_eps_rewards_pool,
    'mstable feeder pool': mstablefeederpool.is_mstable_feeder_pool,
    'saddle': saddle.is_saddle_lp,
    'basketdao': basketdao.is_basketdao_index,
    'popsicle': popsicle.is_popsicle_lp,
}

async def _chainlink_and_band(token_address) -> bool:
    """ We only really need band for a short period in the beginning of fantom's history, and then we will default to chainlink once available. """
    return chainlink and await chainlink.has_feed(token_address, sync=False) and token_address in band

async def _check_bucket_helper(bucket: str, check: Callable[[Address], Awaitable[bool]], address: Address) -> Tuple[str, bool]:
    return bucket, await check(address, sync=False)
