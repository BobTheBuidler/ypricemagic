import logging
import os
from typing import Any, Callable

import eth_retry
from brownie import chain, web3
from requests import Session
from requests.adapters import HTTPAdapter
from web3 import HTTPProvider, Web3
from web3.middleware import filter
from web3.middleware.geth_poa import geth_poa_middleware

from y import ENVIRONMENT_VARIABLES as ENVS
from y.networks import Network
from y.utils.cache import memory

logger = logging.getLogger(__name__)

provider_specific_batch_sizes = {
    "moralis":  2_000,
    "pokt":     2_000,
    "tenderly": 2_000,
    "ankr":     2_000,
}

chain_specific_max_batch_sizes = {
    Network.Mainnet:    10_000,     # 1.58 days
    Network.Gnosis:     20_000,     # 1.15 days
    Network.Fantom:     100_000,    # 1.03 days
    Network.Arbitrum:   20_000,     # 0.34 days
    Network.Optimism:   800_000,    # 10.02 days
}

fallback_batch_size = 10_000

def _get_batch_size() -> int:
    """
    Determine the appropriate batch size for the current network and provider.

    Returns:
        The determined batch size for log fetching.
    """
    if batch_size := ENVS.GETLOGS_BATCH_SIZE:
        return batch_size
    for provider, size in provider_specific_batch_sizes.items():
        if provider in web3.provider.endpoint_uri:
            return size
    return chain_specific_max_batch_sizes.get(chain.id, fallback_batch_size)

BATCH_SIZE = _get_batch_size()


def should_cache(method: str, params: Any) -> bool:
    """
    Determine if a method call should be cached.

    Args:
        method: The name of the method being called.
        params: The parameters of the method call.

    Returns:
        True if the method call should be cached, False otherwise.
    """
    return method == "eth_getCode" and params[1] == "latest"


def getcode_cache_middleware(make_request: Callable, web3: Web3) -> Callable:
    """
    Middleware for caching eth_getCode calls.

    Args:
        make_request: The original request function.
        web3: The Web3 instance.

    Returns:
        A middleware function that caches eth_getCode calls.
    """
    @eth_retry.auto_retry
    def middleware(method: str, params: Any) -> Any:
        logger.debug("%s %s", method, params)
        if should_cache(method, params):
            return memory.cache(make_request)(method, params)
        return make_request(method, params)
    return middleware


def setup_getcode_cache_middleware() -> None:
    """
    Set up the eth_getCode cache middleware for the current Web3 provider.

    This function modifies the Web3 provider to use a custom session with increased
    connection pool size and timeout, and adds the getcode cache middleware.

    On Optimism, it also adds the POA middleware.
    """
    # patch web3 provider with more connections and higher timeout
    if web3.provider:
        try:
            assert web3.provider.endpoint_uri.startswith("http"), "only http and https providers are supported"
            adapter = HTTPAdapter(pool_connections=100, pool_maxsize=100)
            session = Session()
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            web3.provider = HTTPProvider(web3.provider.endpoint_uri, {"timeout": 600}, session)
        except AttributeError as e:
            if "'IPCProvider' object has no attribute 'endpoint_uri'" not in str(e):
                raise

    web3.middleware_onion.add(getcode_cache_middleware)
    
    if chain.id == Network.Optimism:
        try:
            web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        except ValueError as e:
            if str(e) != "You can't add the same un-named instance twice":
                raise
