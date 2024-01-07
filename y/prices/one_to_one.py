
from typing import Optional

import a_sync
from brownie import chain
from brownie.convert.datatypes import EthAddress

from y import ENVIRONMENT_VARIABLES as ENVS
from y.datatypes import Block, UsdPrice
from y.networks import Network
from y.prices import magic

MAPPING = {
    Network.Mainnet: {
        "0x4da27a545c0c5B758a6BA100e3a049001de870f5": "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9", # stkaave -> aave
        "0x27D22A7648e955E510a40bDb058333E9190d12D4": "0x0cec1a9154ff802e7934fc916ed7ca50bde6844e", # ppool -> pool
    }
}.get(chain.id,{})

def is_one_to_one_token(token_address: EthAddress) -> bool:
    return token_address in MAPPING

@a_sync.a_sync(default='sync')
async def get_price(token_address: EthAddress, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE) -> UsdPrice:
    return await magic.get_price(MAPPING[token_address], block=block, skip_cache=skip_cache, sync=False)
