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

_deploy_block_read_executor = make_executor(2, 4, "ypricemagic db executor [deploy block]")
_deploy_block_write_executor = make_executor(1, 4, "ypricemagic db executor [deploy block]")


@a_sync(
    default="async",
    executor=_deploy_block_read_executor,
)
@db_session_retry_locked
def get_deploy_block(address: str) -> Optional[int]:
    """Retrieve the cached deployment block number for a given contract address.

    This function first examines the cached deploy block numbers via
    :func:`known_deploy_blocks`. If a deploy block is found there, it returns it.
    Otherwise, it retrieves the token instance using :func:`_get_get_token` in
    synchronous mode and checks its stored deploy block. If a deploy block is present
    on the token, its block number is returned. If no deploy block is found, the function
    logs that the deploy block is not cached and returns None without attempting to fetch
    it from the blockchain.

    Args:
        address: The contract address as a string.

    Examples:
        >>> deploy_block = get_deploy_block("0x1234567890abcdef1234567890abcdef12345678")
        >>> if deploy_block is not None:
        ...     print("Deployment occurred at block", deploy_block)
        ... else:
        ...     print("Deployment block not available in cache.")

    See Also:
        - :func:`_set_deploy_block`
        - :func:`known_deploy_blocks`
        - :func:`_get_get_token`
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

    Examples:
        >>> _set_deploy_block("0x1234567890abcdef1234567890abcdef12345678", 12345678)

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

    Examples:
        >>> set_deploy_block("0x1234567890abcdef1234567890abcdef12345678", 12345678)

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
    The cache is built by selecting all contract entities on the current chain
    where a deploy block is recorded.

    Examples:
        >>> deploy_blocks = known_deploy_blocks()
        >>> for addr, block in deploy_blocks.items():
        ...     print(f"Contract at {addr} was deployed at block {block}")

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
