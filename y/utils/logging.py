
import inspect
import logging
from functools import lru_cache
from typing import Any, List, Union
from lazy_logging import LazyLoggerFactory

from brownie import chain
from y.networks import Network

yLazyLogger = LazyLoggerFactory("YPRICEMAGIC")

logger = logging.getLogger(__name__)

NETWORK_DESCRIPTOR_FOR_ISSUE_REQ =f'name ({Network.name()})' if Network.name() else f'chainid ({chain.id})'

def gh_issue_request(issue_request_details: Union[str, List[str]], _logger = None) -> None:

    if _logger is None: _logger = logger

    if type(issue_request_details) == str:
        _logger.warning(issue_request_details)

    elif type(issue_request_details) == list:
        for message in issue_request_details:
            _logger.warning(message)

    _logger.warning('Please create an issue and/or create a PR at https://github.com/BobTheBuidler/ypricemagic')
    _logger.warning(f'In your issue, please include the network {NETWORK_DESCRIPTOR_FOR_ISSUE_REQ} and the detail shown above.')
    _logger.warning('and I will add it soon :). This will not prevent ypricemagic from fetching price for this asset.')


def getLineInfo():
    print(inspect.stack()[2][1],":",inspect.stack()[2][2],":",
          inspect.stack()[2][3])


@lru_cache(maxsize=None)
def previous_line(): # TODO
    '''
    getLineInfo()
    cf = inspect.currentframe()
    pprint(inspect.stack())
    '''


def log_previous_line_with_output(logger, output: Any) -> None:
    '''
    Logs previous line of code to both:
    - `logger.debug('code: I am a line of code that produced an output')`
    - `logger.debug('output: 12345)`
    '''
    logger.debug()
