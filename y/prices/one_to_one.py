
from typing import Optional

from brownie import chain
from brownie.convert.datatypes import EthAddress
from y.datatypes import UsdPrice
from y.networks import Network
from y.prices import magic
from y.typing import Block

MAPPING = {
    Network.Mainnet: {
        "0x4da27a545c0c5B758a6BA100e3a049001de870f5": "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9", # stkaave -> aave
    }
}.get(chain.id,{})

def is_one_to_one_token(token_address: EthAddress) -> bool:
    return token_address in MAPPING

def get_price(token_address: EthAddress, block: Optional[Block] = None) -> UsdPrice:
    return magic.get_price(MAPPING[token_address], block=block)
