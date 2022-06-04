
import logging
from typing import Optional

from y import magic
from y.datatypes import AnyAddressType, Block, UsdPrice

logger = logging.getLogger(__name__)

def get_price(token: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
    logger.warning('ypricemagic is in the process of being migrated to y.'
                'y can do all of the same old stuff you expect, plus some new stuff you may or may not need.'
                'This method still works for now, but will be removed soon.'
                'Please update your scripts to use `y.get_price(token, block)`.')
    return magic.get_price(token, block)
