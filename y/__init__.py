import os
from contextlib import suppress

from brownie import chain, network

try:
    # leaving this in here for backward compatability with older brownie versions
    # TODO: remove me when eetherscan disables v1 api
    from brownie.network.contract import _explorer_tokens
except ImportError:
    pass
else:
    # this helps ensure backwards compatability with older versions of brownie
    if "base" not in _explorer_tokens:
        _explorer_tokens["base"] = "BASESCAN_TOKEN"
    if "optimistic" not in _explorer_tokens:
        _explorer_tokens["optimistic"] = "OPTIMISMSCAN_TOKEN"


class NetworkNotSpecified(Exception):
    pass


if not network.is_connected():
    if "BROWNIE_NETWORK_ID" not in os.environ:
        raise NetworkNotSpecified(
            "In order to use pricemagic outside of a brownie project directory, you will need to set $BROWNIE_NETWORK_ID environment variable with the id of your preferred brownie network connection."
        )
    network.connect(os.environ["BROWNIE_NETWORK_ID"])

# for backwards-compatability
from dank_mids import dank_web3 as dank_w3


from y import convert, time
from y.classes.common import ERC20
from y.constants import EEE_ADDRESS, WRAPPED_GAS_COIN, dai, usdc, wbtc, weth
from y.contracts import (
    Contract,
    Contract_erc20,
    Contract_with_erc20_fallback,
    contract_creation_block,
    contract_creation_block_async,
    has_method,
    has_methods,
)
from y.datatypes import Address, Block
from y.exceptions import (
    CalldataPreparationError,
    CallReverted,
    ContractNotVerified,
    MessedUpBrownieContract,
    NonStandardERC20,
    NotABalancerV2Pool,
    NotAUniswapV2Pool,
    PriceError,
    UnsupportedNetwork,
)
from y import exceptions, monkey_patches
from y.networks import Network
from y.prices import magic
from y.prices.magic import get_price, get_prices, map_prices
from y.prices.utils import check_bucket
from y.time import (
    get_block_at_timestamp,
    get_block_timestamp,
    get_block_timestamp_async,
)
from y.utils.events import Events, LogFilter, ProcessedEvents
from y.utils.logging import enable_debug_logging
from y.utils.middleware import setup_getcode_cache_middleware, setup_geth_poa_middleware
from y.utils.multicall import fetch_multicall
from y.utils.raw_calls import balanceOf, raw_call

setup_getcode_cache_middleware()

monkey_patches.monkey_patch_checksum_cache()

if chain.id == Network.Optimism:
    setup_geth_poa_middleware()

__all__ = [
    ### you can reach the below functions, classes, and variables using ###
    ###  `y.__name__` or `from y import __name__`.  ###
    # prices
    "get_price",
    "get_prices",
    "map_prices",
    "check_bucket",
    # erc20
    "ERC20",
    # logs filter,
    "LogFilter",
    # decoded events filter
    "Events",
    "ProcessedEvents",
    # contract stuff
    "Contract",
    "contract_creation_block",
    "contract_creation_block_async",
    "has_method",
    "has_methods",
    # network stuff
    "Network",
    # constants
    "EEE_ADDRESS",
    "WRAPPED_GAS_COIN",
    "weth",
    "dai",
    "usdc",
    "wbtc",
    # magic
    "magic",
    # raw calls
    "raw_call",
    # convert
    "convert",
    # time
    "time",
    "get_block_at_timestamp",
    "get_block_timestamp",
    "get_block_timestamp_async",
    # monkey patches,
    "monkey_patches",
]

with suppress(ModuleNotFoundError):
    """If eth_portfolio is also installed in this env, we will use its extended version of our db schema"""
    from eth_portfolio._db import entities as _db_entities
