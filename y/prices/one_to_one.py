
from typing import Optional

from brownie import chain
from brownie.convert.datatypes import EthAddress
from multicall.utils import await_awaitable
from y.datatypes import Block, UsdPrice
from y.networks import Network
from y.prices import magic

MAPPING = {
    Network.Mainnet: {
        "0x4da27a545c0c5B758a6BA100e3a049001de870f5": "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9", # stkaave -> aave
    }
}.get(chain.id,{})

def is_one_to_one_token(token_address: EthAddress) -> bool:
    return token_address in MAPPING

def get_price(token_address: EthAddress, block: Optional[Block] = None) -> UsdPrice:
    return await_awaitable(get_price_async(token_address, block=block))

async def get_price_async(token_address: EthAddress, block: Optional[Block] = None) -> UsdPrice:
    return await magic.get_price_async(MAPPING[token_address], block=block)