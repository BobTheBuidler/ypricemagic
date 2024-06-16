
import logging
import threading
from typing import Dict, Optional

import a_sync
from brownie import chain
from cachetools import TTLCache, cached
from pony.orm import select
from y._db.decorators import a_sync_read_db_session, a_sync_write_db_session, log_result_count
from y._db.entities import Contract
from y._db.utils._ep import _get_get_token
from y._db.utils.utils import ensure_block
from y.datatypes import Address, Block


logger = logging.getLogger(__name__)

_get_get_token()

@a_sync_read_db_session
def get_deploy_block(address: str) -> Optional[int]:
    if deploy_block := known_deploy_blocks().pop(address, None):
        logger.debug('%s deploy block from cache: %s', address, deploy_block)
        return deploy_block
    get_token = _get_get_token()
    if deploy_block := get_token(address, sync=True).deploy_block:
        logger.debug('%s deploy block from cache: %s', address, deploy_block.number)
        return deploy_block.number
    logger.debug('%s deploy block not cached, fetching from chain', address)

async def _set_deploy_block(address: str, deploy_block: int) -> None:
    await ensure_block(deploy_block)
    return await __set_deploy_block(address, deploy_block)

set_deploy_block = a_sync.ProcessingQueue(_set_deploy_block, num_workers=10, return_data=False)

@a_sync_write_db_session
def __set_deploy_block(address: str, deploy_block: int) -> None:
    from y._db.utils._ep import _get_get_token
    get_token = _get_get_token()
    get_token(address, sync=True).deploy_block = (chain.id, deploy_block)
    logger.debug('deploy block cached for %s: %s', address, deploy_block)


# startup caches

@cached(TTLCache(maxsize=1, ttl=60*60), lock=threading.Lock())
@log_result_count("deploy blocks")
def known_deploy_blocks() -> Dict[Address, Block]:
    """cache and return all known contract deploy blocks for this chain to minimize db reads"""
    return dict(select((c.address, c.deploy_block.number) for c in Contract if c.chain.id == chain.id and c.deploy_block.number))
