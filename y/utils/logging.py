import logging
from typing import List, TypeVar, Union

from brownie import chain
from cachetools.func import ttl_cache
from lazy_logging import LazyLoggerFactory
from typing_extensions import ParamSpec

from y.datatypes import AnyAddressType, Block
from y.networks import Network

T = TypeVar('T')
P = ParamSpec('P')

yLazyLogger = LazyLoggerFactory("YPRICEMAGIC")

logger = logging.getLogger(__name__)

@ttl_cache(ttl=10*60)
def get_price_logger(token_address: AnyAddressType, block: Block, extra: str = '') -> logging.Logger:
    address = str(token_address)
    name = f"y.prices.{Network.label()}.{address}.{block}"
    if extra: 
        name += f".{extra}"
    logger = logging.getLogger(name)
    logger.setLevel(logger.parent.level)
    logger.address = address
    logger.block = block
    return logger

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
