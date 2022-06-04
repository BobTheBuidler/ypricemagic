
from typing import Union

from brownie import Contract
from brownie.convert.datatypes import EthAddress, HexBytes
from eth_typing import AnyAddress, BlockNumber

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
