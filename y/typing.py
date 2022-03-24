
from typing import Union

from brownie import Contract
from brownie.convert.datatypes import EthAddress, HexBytes
from eth_typing import AnyAddress, BlockNumber

Address = Union[str,HexBytes,AnyAddress,EthAddress]
Block = Union[int,BlockNumber]
AddressOrContract = Union[Address,Contract]
AnyAddressType = Union[Address,Contract,int]
