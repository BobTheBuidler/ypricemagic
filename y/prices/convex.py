
from typing import Optional

import a_sync
from brownie.convert.datatypes import EthAddress

from y import ENVIRONMENT_VARIABLES as ENVS
from y.datatypes import Block, UsdPrice
from y.prices import magic

MAPPING = {
    "0x30D9410ED1D5DA1F6C8391af5338C93ab8d4035C": "0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490", # cvx3crv -> 3crv
    "0xbE0F6478E0E4894CFb14f32855603A083A57c7dA": "0xd632f22692FaC7611d2AA1C0D552930D43CAEd3B", # cvxFRAX3CRV-f -> FRAX3CRV
    "0xabB54222c2b77158CC975a2b715a3d703c256F05": "0x5a6A4D54456819380173272A5E8E9B9904BdF41B", # cvxMIM-3LP3CRV-f -> crvMIM
    "0xCA3D9F45FfA69ED454E66539298709cb2dB8cA61": "0x43b4FdFD4Ff969587185cDB6f0BD875c5Fc83f8c", # cvxalUSD3CRV-f -> crvalusd
    "0xDeFd8FdD20e0f34115C7018CCfb655796F6B2168": "0xc4AD29ba4B3c580e6D59105FFf484999997675Ff", # cvx3crypto -> 3crypto
}

def is_convex_lp(token_address: EthAddress) -> bool:
    return token_address in MAPPING

@a_sync.a_sync(default='sync')
async def get_price(token_address: EthAddress, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE) -> UsdPrice:
    return await magic.get_price(MAPPING[token_address], block, skip_cache=skip_cache, sync=False)
