
from typing import Any, Optional, TypeVar

from checksum_dict import ChecksumAddressDict
from y.datatypes import AnyAddressType

T = TypeVar("T", bound=type)


class Singleton(type):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.__instance: Optional[T] = None
        super().__init__(*args, **kwargs)

    def __call__(self, *args: Any, **kwargs: Any) -> T:
        if self.__instance is None:
            self.__instance = super().__call__(*args, **kwargs)
        return self.__instance

class ContractSingleton(type):
    def __init__(self, address: AnyAddressType, *args: Any, **kwargs: Any) -> None:
        self.__instances: ChecksumAddressDict[T] = ChecksumAddressDict()
        super().__init__(address, *args, **kwargs)

    def __call__(self, address: AnyAddressType, *args: Any, **kwargs: Any) -> T:
        try:
            return self.__instances[address]
        except KeyError:
            new = super().__call__(address, *args, **kwargs)
            self.__instances[address] = new
            return new
