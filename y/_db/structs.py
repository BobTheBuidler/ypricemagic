from functools import lru_cache

from dank_mids.types import _DictStruct
from inflection import underscore


class _CamelDictStruct(_DictStruct, rename="camel"):
    """
    A mixin class that allows camelCase key lookups for snake_case struct attrs
    Original use case was so Log structs can be used interchangably with LogReceipt instances
    """

    def __getitem__(self, attr: str):
        return getattr(self, _make_snake(attr))


class Log(_CamelDictStruct):
    removed: bool | None
    log_index: int | None
    transaction_index: int | None
    transaction_hash: str
    block_hash: str | None
    block_number: int | None
    address: str | None
    data: str | None
    topics: list[str] | None


class Trace(_CamelDictStruct):
    # TODO so we can trace chain for eth_port on alt chains
    pass


@lru_cache(maxsize=None)
def _make_snake(camel: str) -> str:
    return underscore(camel)
