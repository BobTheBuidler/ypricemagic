
import logging
from typing import Dict, Optional

import a_sync
from brownie import chain
from cachetools.func import ttl_cache
from pony.orm import select
from y._db.decorators import a_sync_read_db_session, a_sync_write_db_session
from y._db.entities import Contract
from y._db.utils._ep import _get_get_token
from y._db.utils.utils import ensure_block
from y.datatypes import Address, Block


logger = logging.getLogger(__name__)

@a_sync_read_db_session
def get_deploy_block(address: str) -> Optional[int]:
    if deploy_block := known_deploy_blocks().get(address):
        logger.debug('%s deploy block from cache: %s', address, deploy_block)
        return deploy_block
    get_token = _get_get_token()
    if deploy_block := get_token(address, sync=True).deploy_block:
        logger.debug('%s deploy block from cache: %s', address, deploy_block.number)
        return deploy_block.number
    logger.debug('%s deploy block not cached, fetching from chain', address)

def set_deploy_block(address: str, deploy_block: int) -> None:
    a_sync.create_task(
        coro=_set_deploy_block(address, deploy_block),
        name=f"set_deploy_block {address}: {deploy_block}",
        skip_gc_until_done=True,
    )

@a_sync_write_db_session
def _set_deploy_block(address: str, deploy_block: int) -> None:
    from y._db.utils._ep import _get_get_token
    get_token = _get_get_token()
    ensure_block(deploy_block, sync=True)
    get_token(address, sync=True).deploy_block = (chain.id, deploy_block)
    logger.debug('deploy block cached for %s: %s', address, deploy_block)


# startup caches
    
@ttl_cache(maxsize=1, ttl=60*60)
def known_deploy_blocks() -> Dict[Address, Block]:
    """cache and return all known contract deploy blocks for this chain to minimize db reads"""
    return dict(select((c.address, c.deploy_block.number) for c in Contract if c.chain.id == chain.id and c.deploy_block.number))
