import logging

from async_lru import alru_cache
from brownie import web3
from cachetools.func import lru_cache
from web3._utils.rpc_abi import RPC

from y.utils.dank_mids import dank_w3
from y.utils.logging import yLazyLogger

logger = logging.getLogger(__name__)

@lru_cache(1)
@yLazyLogger(logger)
def get_ethereum_client() -> str:
    return _get_ethereum_client(web3.clientVersion)

@alru_cache(maxsize=1)
async def get_ethereum_client_async() -> str:
    return _get_ethereum_client(await dank_w3.manager.coro_request(RPC.web3_clientVersion, []))

@yLazyLogger(logger)
def _get_ethereum_client(client: str) -> str:
    logger.debug("client: %s", client)
    if client.startswith('TurboGeth'):
        return 'tg'
    if client.lower().startswith('erigon'):
        return 'erigon'
    if client.lower().startswith('geth'):
        return 'geth'
    return client
