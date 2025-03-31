"""
This module provides utility functions for the ypricemagic library.

The utilities include caching, attribute checking, and method gathering functionalities
that are used throughout the library to enhance performance and ensure code reliability.

Imported Functions:
    - :func:`y.utils.cache.a_sync_ttl_cache`: Provides a caching mechanism with a time-to-live (TTL) feature.
    - :func:`y.utils.checks.hasall`: Checks if an object has all specified attributes.
    - :func:`y.utils.gather.gather_methods`: Gathers methods from a class or module.

Examples:
    Using the caching utility:
    >>> from y.utils.cache import a_sync_ttl_cache
    >>> @a_sync_ttl_cache
    ... def expensive_function(x):
    ...     return x * x
    >>> result = expensive_function(4)

    Checking for attributes:
    >>> from y.utils.checks import hasall
    >>> class MyClass:
    ...     attr1 = 1
    ...     attr2 = 2
    >>> obj = MyClass()
    >>> hasall(obj, ['attr1', 'attr2'])
    True

    Gathering methods:
    >>> from y.utils.gather import gather_methods
    >>> methods = gather_methods(MyClass)
    >>> print(methods)

See Also:
    - :mod:`y.utils.cache`: For caching utilities.
    - :mod:`y.utils.checks`: For attribute checking utilities.
    - :mod:`y.utils.gather`: For method gathering utilities.
"""

from y.utils.cache import a_sync_ttl_cache
from y.utils.checks import hasall
from y.utils.gather import gather_methods
