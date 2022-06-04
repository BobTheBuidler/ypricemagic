
from typing import Any, Dict

from y import convert
from y.datatypes import AnyAddressType


class Singleton(type):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.__instance = None
        super().__init__(*args, **kwargs)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if self.__instance is None:
            self.__instance = super().__call__(*args, **kwargs)
        return self.__instance

class ContractSingleton(type):
    def __init__(self, address: AnyAddressType, *args: Any, **kwargs: Any) -> None:
        self.__instances: Dict[str,Any] = {}
        super().__init__(address, *args, **kwargs)

    def __call__(self, address: AnyAddressType, *args: Any, **kwargs: Any) -> Any:
        address = convert.to_address(address)
        if address not in self.__instances:
            self.__instances[address] = super().__call__(address, *args, **kwargs)
        return self.__instances[address]
