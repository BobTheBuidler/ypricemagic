import logging
from typing import Any, Callable

import eth_retry
from brownie import web3
from requests import Session
from requests.adapters import HTTPAdapter
from web3 import HTTPProvider, Web3
from web3.middleware import filter
from y.utils.cache import memory

logger = logging.getLogger(__name__)

BATCH_SIZE = (
    2_000 if 'moralis' in web3.provider.endpoint_uri
    else 2_000 if 'pokt' in web3.provider.endpoint_uri
    else 10_000
)


def should_cache(method: str, params: Any) -> bool:
    if method == "eth_getCode" and params[1] == "latest":
        return True
    return False


def cache_middleware(make_request: Callable, web3: Web3) -> Callable:
    @eth_retry.auto_retry
    def middleware(method: str, params: Any) -> Any:
        logger.debug("%s %s", method, params)
        if should_cache(method, params):
            return memory.cache(make_request)(method, params)
        return make_request(method, params)
    return middleware


def setup_middleware() -> None:
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
            if "'IPCProvider' object has no attribute 'endpoint_uri'" in str(e):
                pass 
            else:
                raise

    # patch and inject local filter middleware
    filter.MAX_BLOCK_REQUEST = BATCH_SIZE
    web3.middleware_onion.add(filter.local_filter_middleware)
    web3.middleware_onion.add(cache_middleware)

def ensure_middleware() -> None:
    setup_middleware()
    
