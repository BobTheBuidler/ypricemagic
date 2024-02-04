
from typing import Any, Iterable

def hasall(obj: Any, attrs: Iterable[str]) -> bool:
    """returns True if each attr in `attrs` is an attribute of `obj`, False otherwise"""
    return all(hasattr(obj, attr) for attr in attrs)