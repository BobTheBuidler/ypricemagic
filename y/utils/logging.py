import asyncio
import weakref
from logging import DEBUG, Logger, StreamHandler, getLogger, _lock
from types import MethodType
from typing import List, NoReturn, Optional, Tuple, TypeVar, Union

import a_sync
from brownie import chain
from lazy_logging import LazyLoggerFactory
from typing_extensions import ParamSpec

from y.datatypes import AnyAddressType, Block
from y.networks import Network

T = TypeVar("T")
P = ParamSpec("P")

yLazyLogger = LazyLoggerFactory("YPRICEMAGIC")

logger = getLogger(__name__)


def enable_debug_logging(logger: str = "y") -> None:
    """
    Enables ypricemagic's debugging mode. Very verbose.
    """
    logger = getLogger(logger)
    logger.setLevel(DEBUG)
    if not logger.handlers:
        logger.addHandler(StreamHandler())


class PriceLogger(Logger):
    enabled: bool
    address: str
    block: int
    key: Tuple[AnyAddressType, Block, Optional[str], str]
    debug_task: Optional["asyncio.Task[None]"]

    def close(self) -> None:
        # since we make a lot of these we don't want logging module to cache them
        self.debug("closing %s", logger)
        with _lock:
            Logger.manager.loggerDict.pop(self.name, None)


def get_price_logger(
    token_address: AnyAddressType,
    block: Block,
    *,
    symbol: str = None,
    extra: str = "",
    start_task: bool = False,
) -> PriceLogger:
    address = str(token_address)
    name = f"y.prices.{Network.label()}.{address}.{block}"
    if extra:
        name += f".{extra}"

    # the built-in logging module caches loggers but we need to make sure they have the proper members for ypm
    if cached_logger := _all_price_loggers.get(name, None):
        return cached_logger

    logger = getLogger(name)
    logger.address = address
    logger.block = block
    logger.enabled = logger.isEnabledFor(DEBUG)

    if logger.enabled:
        logger.debug = lambda msg, *args, **kwargs: logger._log(
            DEBUG, msg, args, **kwargs
        )

        if start_task:
            # will kill itself when this logger is garbage collected
            logger.debug_task = a_sync.create_task(
                coro=_debug_tsk(symbol, weakref.ref(logger)),
                name=f"_debug_tsk({symbol}, {logger})",
                log_destroy_pending=False,
            )

    else:
        logger.debug = _noop

    logger.close = MethodType(PriceLogger.close, logger)

    _all_price_loggers[name] = logger
    return logger


def _noop(*_a, **_k): ...


async def _debug_tsk(
    symbol: Optional[str], logger_ref: "weakref.ref[Logger]"
) -> NoReturn:
    """Prints a log every 1 minute until the creating coro returns"""
    if symbol:
        args = "price still fetching for %s", symbol
    else:
        args = ("still fetching...",)
    while True:
        await asyncio.sleep(60)
        logger = logger_ref()
        if logger is None:
            return
        logger.debug(*args)


_all_price_loggers: "weakref.WeakValueDictionary[str, PriceLogger]" = (
    weakref.WeakValueDictionary()
)


NETWORK_DESCRIPTOR_FOR_ISSUE_REQ = (
    f"name ({Network.name()})" if Network.name() else f"chainid ({chain.id})"
)


def _gh_issue_request(
    issue_request_details: Union[str, List[str]], _logger=None
) -> None:

    _logger = _logger or logger

    if type(issue_request_details) == str:
        _logger.warning(issue_request_details)

    elif type(issue_request_details) == list:
        for message in issue_request_details:
            _logger.warning(message)

    _logger.warning(
        "Please create an issue and/or create a PR at https://github.com/BobTheBuidler/ypricemagic"
    )
    _logger.warning(
        f"In your issue, please include the network {NETWORK_DESCRIPTOR_FOR_ISSUE_REQ} and the detail shown above."
    )
    _logger.warning(
        "and I will add it soon :). This will not prevent ypricemagic from fetching price for this asset."
    )
