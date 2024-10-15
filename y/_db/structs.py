
from functools import lru_cache
from typing import List, Optional

from dank_mids.structs import DictStruct
from dank_mids.structs.data import Address, uint
from hexbytes import HexBytes
from inflection import underscore

    
class _CamelDictStruct(DictStruct, rename="camel"):
    """
    A mixin class that allows camelCase key lookups for snake_case struct attrs
    Original use case was so Log structs can be used interchangably with LogReceipt instances
    """
    def __getitem__(self, attr: str):
        return super().__getitem__(_make_snake(attr))

class Log(_CamelDictStruct):
    removed: Optional[bool]
    block_number: Optional[uint]
    transaction_hash: HexBytes
    transaction_index: Optional[uint]
    log_index: Optional[uint]
    address: Optional[Address]
    topics: Optional[List[HexBytes]]
    data: Optional[HexBytes]

class Trace(_CamelDictStruct):
    # TODO so we can trace chain for eth_port on alt chains
    pass

@lru_cache(maxsize=None)
def _make_snake(camel: str) -> str:
    return underscore(camel)
