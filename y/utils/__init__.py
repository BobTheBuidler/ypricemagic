"""
Provides utility functions for the ypricemagic library.

This module includes functions for caching, attribute checking, and gathering results from multiple contract method calls. These utilities are used throughout the library to enhance performance and ensure code reliability.

Imported Functions:
    - :func:`y.utils.cache.a_sync_ttl_cache`: Provides a caching mechanism with a time-to-live (TTL) feature.
    - :func:`y.utils.checks.hasall`: Checks if an object has all specified attributes.
    - :func:`y.utils.gather.gather_methods`: Asynchronously gathers results by calling multiple contract method signatures on a given contract address.

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

    Gathering contract method results:
        >>> from y.utils.gather import gather_methods
        >>> contract_address = "0x6B175474E89094C44Da98b954EedeAC495271d0F"  # Example contract address
        >>> methods = ["name()", "symbol()", "decimals()"]
        >>> results = await gather_methods(contract_address, methods)
        >>> print(results)
        ('Dai Stablecoin', 'DAI', 18)

See Also:
    - :mod:`y.utils.cache` for caching utilities.
    - :mod:`y.utils.checks` for attribute checking utilities.
    - :mod:`y.utils.gather` for gathering results from multiple contract method calls.
"""

from y.utils.cache import a_sync_ttl_cache
from y.utils.checks import hasall
from y.utils.gather import gather_methods
