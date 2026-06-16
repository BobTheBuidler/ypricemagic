import logging
from collections.abc import Iterable
from decimal import Decimal
from typing import Optional

import a_sync
from a_sync import as_yielded, cgather
from brownie import ZERO_ADDRESS, chain
from brownie.exceptions import ContractNotFound, ContractNotVerified
from brownie.network.contract import ContractEvents
from brownie's typing import _BrownieContractType
from dank_mids import dank_web3
from eth_utils import is_address
from eth_utils.abi import collapse_if_tuple
from hexbytes import HexBytes
from joblib import Parallel, delayed
from multicall import Call
from web3.exceptions import BadFunctionCallOutput, ContractLogicError

from y import ENVIRONMENT_VARIABLES as ENVS
from y import convert
from y._decorators import stuck_coro_debugger
from y.classes.common import ERC20
from y.contracts import Contract, ContractCreationException, has_method, has_methods
from y.datatypes import AnyAddressType, Block, Pool, UsdPrice
from y.exceptions import CantFetchParam, NonStandardERC20, PriceError, yPriceMagicError
from y.networks import Network
from y.prices import curve
from y.prices.utils.buckets import string_matcher
from y.utils.cache import a_sync_ttl_cache
from y.utils.client import get_ethereum_client
from y.utils.events import ProcessedEvents
from y.utils.logging import get_price_logger
from y.utils.raw_calls import raw_call

logger = logging.getLogger(__name__)


_is_yearn_vaults: set = set()
_is_yswaps: set = set()
_is_belt_vault: set = set()
_is_solidex_deposit: set = set()
_is_rkp3r_token: set = set()
_is_popsicle_lp: set = set()
_is_ib_token: set = set()
_is_ib_yvault: set = set()
_is_gearbox_dtoken: set = set()
_is_cream_crtoken: set = set()

_is_vbtoken: set = set()


@a_sync.a_sync(default="sync", cache_type="memory")
async def is_yearn_vault(token_address: AnyAddressType) -> bool:
    token_address = await convert.to_address_async(token_address)
    if token_address in _is_yearn_vaults:
        return True

    # try each approach until one is successful. In some cases, we may be able to
    # return false early based on certain method tests.
    contract = await Contract.coroutine(token_address)

    try:
        version = await raw_call(
            token_address, "apiVersion()", output="str", sync=False
        )
    except (AttributeError, ContractNotVerified, ContractNotFound):
        version = None

    if version:
        if int(version.split(".")[0]) >= 2:
            _is_yearn_vaults.add(token_address)
            return True

    if await has_method(token_address, "vault()", sync=False):
        _is_yearn_vaults.add(token_address)
        return True

    try:
        token = ERC20(token_address, asynchronous=True)
        if await token.symbol in ["YFI yVault", "yDAI", "yUSDC", "yUSDT", "yTUSD"]:
            _is_yearn_vaults.add(token_address)
            return True
    except NonStandardERC20:
        pass
    return False


@a_sync.a_sync(default="sync", cache_type="memory")
async def is_vbtoken(token_address: AnyAddressType) -> bool:
    # vbTokens use a dedicated allowlist and solvency guard in y.prices.vbtoken.
    from y.prices import vbtoken

    return await vbtoken.is_vbtoken(token_address)


@a_sync.a_sync(default="sync", cache_type="memory")
async def is_yswap(token_address: AnyAddressType) -> bool:
    """Checks if `token_address` is a yswap."""
    token_address = await convert.to_address_async(token_address)
    if token_address in _is_yswaps:
        return True

    try:
        # if it is a yswap it will be it's own balance, with 0% for the underlying
        # not sure if this is a safe way to check so we'll try the other method first
        base_token = await raw_call(token_address, "token()", output="address", sync=False)
    except AttributeError:
        base_token = None

    if base_token and base_token != ZERO_ADDRESS:
        balance = await raw_call(
            token_address, "balanceOf(address)", inputs=base_token, output="int", sync=False
        )
        if balance:
            _is_yswaps.add(token_address)
            return True

    # check if contract has method "getInputPrice" and if it is the same as the token's
    # address
    if await has_method(token_address, "getInputPrice(address,uint256)", sync=False):
        _is_yswaps.add(token_address)
        return True

    return False
