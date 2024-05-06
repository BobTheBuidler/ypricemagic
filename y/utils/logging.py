import asyncio
import logging
import weakref
from typing import List, NoReturn, Optional, Tuple, TypeVar, Union

import a_sync
from brownie import chain
from lazy_logging import LazyLoggerFactory
from typing_extensions import ParamSpec

from y.datatypes import AnyAddressType, Block
from y.networks import Network

T = TypeVar('T')
P = ParamSpec('P')

yLazyLogger = LazyLoggerFactory("YPRICEMAGIC")

logger = logging.getLogger(__name__)

class PriceLogger(logging.Logger):
    address: str
    block: int

def get_price_logger(token_address: AnyAddressType, block: Block, symbol: str = None, extra: str = '') -> PriceLogger:
    address = str(token_address)
    key = (address, block, extra)
    if logger := _all_price_loggers.get(key, None):
        return logger
    name = f"y.prices.{Network.label()}.{address}.{block}"
    if extra: 
        name += f".{extra}"
    logger = logging.getLogger(name)
    logger.address = address
    logger.block = block
    if logger.level != logger.parent.level:
        logger.setLevel(logger.parent.level)
    if logger.isEnabledFor(logging.DEBUG):
        # will kill itself when this logger is garbage collected
        logger.debugger_task = a_sync.create_task(
            coro=_debug_tsk(symbol, logger), 
            name=f"_debug_tsk({symbol}, {logger})", 
            log_destroy_pending=False,
        )
    _all_price_loggers[key] = logger
    return logger

async def _debug_tsk(symbol: Optional[str], logger: logging.Logger) -> NoReturn:
    """Prints a log every 1 minute until the creating coro returns"""
    if symbol:
        args = "price still fetching for %s", symbol
    else:
        args = "still fetching...",
    while True:
        await asyncio.sleep(60)
        logger.debug(*args)

_all_price_loggers: "weakref.WeakValueDictionary[Tuple[AnyAddressType, Block, str], PriceLogger]" = weakref.WeakValueDictionary()

def enable_debug_logging(logger: str = 'y') -> None:
    logger = logging.getLogger(logger)
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        logger.addHandler(logging.StreamHandler())

NETWORK_DESCRIPTOR_FOR_ISSUE_REQ =f'name ({Network.name()})' if Network.name() else f'chainid ({chain.id})'

def _gh_issue_request(issue_request_details: Union[str, List[str]], _logger = None) -> None:

    if _logger is None: _logger = logger

    if type(issue_request_details) == str:
        _logger.warning(issue_request_details)

    elif type(issue_request_details) == list:
        for message in issue_request_details:
            _logger.warning(message)

    _logger.warning('Please create an issue and/or create a PR at https://github.com/BobTheBuidler/ypricemagic')
    _logger.warning(f'In your issue, please include the network {NETWORK_DESCRIPTOR_FOR_ISSUE_REQ} and the detail shown above.')
    _logger.warning('and I will add it soon :). This will not prevent ypricemagic from fetching price for this asset.')
