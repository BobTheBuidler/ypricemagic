
import threading
from typing import Any, Dict, Optional, Tuple, Type, TypeVar

T = TypeVar("T", bound=object)


class Singleton(type):
    def __init__(cls, name: str, bases: Tuple[type, ...], namespace: Dict[str, Any]) -> None:
        cls.__instance: Optional[T] = None
        cls.__lock = threading.Lock()
        super().__init__(name, bases, namespace)

    def __call__(cls, *args: Any, **kwargs: Any) -> T:
        if cls.__instance is None:
            with cls.__lock:
                # Check again in case `__instance` was set while we were waiting for the lock.
                if cls.__instance is None:
                    cls.__instance = super().__call__(*args, **kwargs)
        return cls.__instance
