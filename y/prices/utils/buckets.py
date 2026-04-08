import logging
from typing import Callable, Optional

import a_sync
from brownie import ZERO_ADDRESS
from typing_extensions import override

from y import convert
from y.constants import WRAPPED_GAS_COIN
from y.contracts import Contract
from y.exceptions import ContractNotFound
from y.networks import Network
from y.prices import curve, ib, popsicle, vbtoken
from y.prices import stargate as stargate_check
from y.prices import synthetix, yearn
from y.prices.convex import CvxDeposit
from y.prices.lending import compound
from y.prices.lending.aave import atokens
from y.prices.lending.ib import ib_tokens
from y.prices.popsicle import PopsicleLp
from y.prices.utils import check_bucket
from y.prices.utils.buckets import string_matcher
from y.utils.early_exit import continue_if

logger = logging.getLogger(__name__)


async def is_curve_pool(token_address: str) -> bool:
    if curve.maybe_curve_lp(token_address):
        pool = await curve.CurvePool.from_lp_token(token_address, sync=False)
        return pool is not None
    return False


async def is_ib(token_address: str) -> bool:
    if ib.maybe_ib_token(token_address):
        token = await ib.IBToken(token_address, sync=False)
        return await token.is_ib_token()
    return False


async def is_atoken(token_address: str) -> bool:
    return await atokens.is_atoken(token_address, sync=False)


async def is_stargate(token_address: str) -> bool:
    return await stargate_check.is_stargate_lp(token_address, sync=False)


STRING_MATCHERS: dict[str, Callable[[str], bool]] = {
    "curve": curve.maybe_curve_lp,
    "yearn": yearn.is_yearn_vault,
    "stargate lp": stargate_check.is_stargate_lp,
    "atoken": is_atoken,
    "ib token": is_ib,
    "compound": compound.is_compound,
    "solidex": yearn.is_solidex_deposit,
    "convex": CvxDeposit.is_convex_deposit,
    "popsicle": PopsicleLp.is_popsicle_lp,
    "rkp3r": yearn.is_rkp3r_token,
    "synthetix": synthetix.is_synth,
    "stargate": stargate_check.is_stargate,
    "vbtoken": vbtoken.is_vbtoken,
}


async def is_pool_token(token: str, caller: Optional[str] = None) -> Optional[str]:
    if token in convert.STABLECOINS.values():
        return None

    for bucket, matcher in STRING_MATCHERS.items():
        if await matcher(token):
            return bucket

    if await is_cream_crtoken(token):
        return "compound"

    if await is_gearbox_dtoken(token):
        return "gearbox"

    if await is_yfi_dai(token):
        return "curve"

    if await is_ypool(token):
        return "curve"

    if await is_belt_crv(token):
        return "curve"

    if await is_yvault(token):
        return "yearn"


async def is_yvault(token_address: str) -> bool:
    # Checks for v2 and v3 vaults
    return await yearn.is_yearn_vault(token_address, sync=False)


async def is_yfi_dai(token_address: str) -> bool:
    # Checks for the yfi/dai pool
    return token_address in [
        # yfi-dai pool
        "0x9b93c29595dd603f758d3fa9a9e436790d96a56c",
        # yvcurve-ib pool
        "0x25e493f94e1a295c1bbc833fd11cb170b274e944",
    ]


async def is_belt_crv(token_address: str) -> bool:
    # Checks for belt-crv pool
    return token_address in [
        # belt-crv pool
        "0x20d5512272a329f5f52b36a4d2e5344c04dba57e"
    ]


async def is_ypool(token_address: str) -> bool:
    # Checks for the ypool
    return token_address in [
        # ypool
        "0xdf5e0e81dff6faf3a7e52ba697820c5e32d806a8"
    ]


@a_sync.a_sync(default="sync", cache_type="memory")
async def check_bucket(token_address: str, caller: Optional[str] = None) -> Optional[str]:
    token_address = await convert.to_address_async(token_address)
    if token_address in convert.STABLECOINS.values() or token_address == WRAPPED_GAS_COIN:
        return None

    bucket: str = await is_pool_token(token_address)
    return bucket


@a_sync.a_sync(default="sync", cache_type="memory")
async def is_gearbox_dtoken(token_address: str) -> bool:
    # Checks for dTokens from Gearbox protocol
    return await yearn.is_dtoken(token_address)


@a_sync.a_sync(default="sync", cache_type="memory")
async def is_cream_crtoken(token_address: str) -> bool:
    # Checks for Cream lending crTokens
    if Network.Mainnet:
        token_address = await convert.to_address_async(token_address)
        if await is_comptroller(token_address):
            return True
    return False


async def is_comptroller(token_address: str) -> bool:
    if token_address in [
        # creams comptroller
        "0x3d5bc3c8d13dcb8bf317092d84783c2697ae9258",
        # iron bank comptroller
        "0xAB1c342C7bf5Ec5F02ADEA1c2270670bCa144CbB",
    ]:
        return True

    try:
        comptroller = await Contract.coroutine(token_address)
    except ContractNotFound:
        return False

    if comptroller is None:
        return False

    # Check if it has a name function and if the name contains "Comptroller".
    if comptroller.address != ZERO_ADDRESS and await string_matcher(comptroller, "Comptroller"):
        return True
    return False
