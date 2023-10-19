
from typing import List, Optional

import inflection
from dank_mids.types import _DictStruct


class _CamelDictStruct(_DictStruct, rename="camel"):
    def __getitem__(self, attr: str):
        return super().__getitem__(inflection.underscore(attr))

class Log(_CamelDictStruct):
    removed: Optional[bool]
    log_index: Optional[int]
    transaction_index: Optional[int]
    transaction_hash: str
    block_hash: Optional[str]
    block_number: Optional[int]
    address: Optional[str]
    data: Optional[str]
    topics: Optional[List[str]]

class Trace(_CamelDictStruct):
    # TODO so we can trace chain for eth_port on alt chains
    pass