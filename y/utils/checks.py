"""
Utility functions for performing various checks.
"""

from typing import Any, Iterable


def hasall(obj: Any, attrs: Iterable[str]) -> bool:
    """
    Check if an object has all the specified attributes.

    Args:
        obj: The object to check.
        attrs: An iterable of attribute names to check for.

    Returns:
        True if the object has all the specified attributes, False otherwise.

    Example:
        >>> class TestClass:
        ...     attr1 = 1
        ...     attr2 = 2
        >>> test_obj = TestClass()
        >>> hasall(test_obj, ['attr1', 'attr2'])
        True
        >>> hasall(test_obj, ['attr1', 'attr3'])
        False
    """
    return all(hasattr(obj, attr) for attr in attrs)