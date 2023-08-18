
from typing import TYPE_CHECKING, Union

from brownie import Contract
from brownie.convert.datatypes import EthAddress, HexBytes
from eth_typing import AnyAddress, BlockNumber

if TYPE_CHECKING:
    from y.prices.dex.uniswap.v2 import UniswapV2Pool
    from y.prices.stable_swap.curve import CurvePool

Pool = Union["UniswapV2Pool", "CurvePool"]

Address = Union[str,HexBytes,AnyAddress,EthAddress]
Block = Union[int,BlockNumber]
AddressOrContract = Union[Address,Contract]
AnyAddressType = Union[Address,Contract,int]

class UsdValue(float):
    def __init__(self, v) -> None:
        super().__init__()
    
    def __str__(self) -> str:
        return f'${self:.8f}'

class UsdPrice(UsdValue):
    def __init__(self, v) -> None:
        super().__init__(v)
