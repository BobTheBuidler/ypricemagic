import logging
import threading
from typing import Dict, Optional

from a_sync import ProcessingQueue, a_sync
from cachetools import TTLCache, cached
from pony.orm import select

from y._db.decorators import db_session_retry_locked, log_result_count
from y._db.entities import Contract
from y._db.utils._ep import _get_get_token
from y._db.utils.utils import ensure_block, make_executor
from y.constants import CHAINID
from y.datatypes import Address, Block


logger = logging.getLogger(__name__)
_logger_debug = logger.debug

_get_get_token()

_deploy_block_read_executor = make_executor(
    2, 4, "ypricemagic db executor [deploy block]"
)
_deploy_block_write_executor = make_executor(
    1, 4, "ypricemagic db executor [deploy block]"
)


@a_sync(
    default="async",
    executor=_deploy_block_read_executor,
)
@db_session_retry_locked
def get_deploy_block(address: str) -> Optional[int]:
    """Retrieve the deployment block number for a given contract address.

    This function first checks a cache for the deployment block number. If not found,
    it fetches the information from the blockchain.

    Args:
        address: The contract address as a string.

    Examples:
        >>> deploy_block = get_deploy_block("0x1234567890abcdef1234567890abcdef12345678")
        >>> print(deploy_block)

    See Also:
        - :func:`_set_deploy_block`
    """
    if deploy_block := known_deploy_blocks().pop(address, None):
        _logger_debug("%s deploy block from cache: %s", address, deploy_block)
        return deploy_block
    get_token = _get_get_token()
    token = get_token(address, sync=True)
    if token is None:
        raise ValueError(f"get_token('{address}', sync=True) returned 'None'")
    if deploy_block := token.deploy_block:
        _logger_debug("%s deploy block from cache: %s", address, deploy_block.number)
        return deploy_block.number
    _logger_debug("%s deploy block not cached, fetching from chain", address)


@a_sync(default="async", executor=_deploy_block_write_executor)
@db_session_retry_locked
def _set_deploy_block(address: str, deploy_block: int) -> None:
    """Set the deployment block number for a contract address in the database.

    Args:
        address: The contract address as a string.
        deploy_block: The block number where the contract was deployed.

    See Also:
        - :func:`set_deploy_block`
    """
    from y._db.utils._ep import _get_get_token

    ensure_block(deploy_block, sync=True)
    get_token = _get_get_token()
    get_token(address, sync=True).deploy_block = (CHAINID, deploy_block)
    _logger_debug("deploy block cached for %s: %s", address, deploy_block)


def set_deploy_block(address: str, deploy_block: int) -> None:
    """Set the deployment block number for a contract address in the database.

    Args:
        address: The contract address as a string.
        deploy_block: The block number where the contract was deployed.

    See Also:
        - :func:`_set_deploy_block`
    """


set_deploy_block = ProcessingQueue(_set_deploy_block, num_workers=10, return_data=False)

# startup caches


@cached(TTLCache(maxsize=1, ttl=60 * 60), lock=threading.Lock())
@log_result_count("deploy blocks")
def known_deploy_blocks() -> Dict[Address, Block]:
    """Cache and return all known contract deploy blocks for this chain.

    This function minimizes database reads by caching the result for one hour.

    Examples:
        >>> deploy_blocks = known_deploy_blocks()
        >>> print(deploy_blocks)

    See Also:
        - :func:`get_deploy_block`
    """
    return dict(
        select(
            (c.address, c.deploy_block.number)
            for c in Contract
            if c.chain.id == CHAINID and c.deploy_block.number
        )
    )
