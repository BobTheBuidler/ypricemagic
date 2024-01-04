
import logging
from typing import Optional

from a_sync import a_sync
from pony.orm import db_session
from y._db.common import token_attr_threads
from y._db.entities import retry_locked
from y._db.utils._ep import _get_get_token


logger = logging.getLogger(__name__)

@a_sync(default='async', executor=token_attr_threads)
@db_session
@retry_locked
def get_deploy_block(address: str) -> Optional[int]:
    get_token = _get_get_token()
    deploy_block = get_token(address, sync=True).deploy_block
    logger.debug('%s deploy block from cache: %s', address, deploy_block)
    return deploy_block

@a_sync(default='async', executor=token_attr_threads)
@db_session
@retry_locked
def set_deploy_block(address: str, deploy_block: int) -> None:
    get_token = _get_get_token()
    get_token(address, sync=True).deploy_block = deploy_block
    logger.debug('deploy block cached for %s: %s', address, deploy_block)
