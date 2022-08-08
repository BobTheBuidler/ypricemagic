
import threading
from typing import Any, Optional, TypeVar

T = TypeVar("T", bound=type)


class Singleton(type):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.__instance: Optional[T] = None
        self.__lock = threading.Lock()
        super().__init__(*args, **kwargs)

    def __call__(self, *args: Any, **kwargs: Any) -> T:
        if self.__instance is None:
            with self.__lock:
                # Check again in case `__instance` was set while we were waiting for the lock.
                if self.__instance is None:
                    self.__instance = super().__call__(*args, **kwargs)
                return self.__instance
