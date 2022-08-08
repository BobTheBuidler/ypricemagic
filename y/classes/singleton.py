
from typing import Any, Optional, TypeVar

T = TypeVar("T", bound=type)


class Singleton(type):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.__instance: Optional[T] = None
        super().__init__(*args, **kwargs)

    def __call__(self, *args: Any, **kwargs: Any) -> T:
        if self.__instance is None:
            self.__instance = super().__call__(*args, **kwargs)
        return self.__instance
