"""
Utility functions for gathering method results asynchronously.
"""

from asyncio import ensure_future
from typing import Any, Awaitable, Iterable, Optional, Tuple, TypeVar

from a_sync import igather
from multicall import Call

from y._decorators import stuck_coro_debugger


__T0 = TypeVar("__T0")
__T1 = TypeVar("__T1")


async def gather2(
    first_awaitable: Awaitable[__T0], second_awaitable: Awaitable[__T1]
) -> Tuple[__T0, __T1]:
    second_awaitable = ensure_future(second_awaitable)
    return await first_awaitable, await second_awaitable


async def gather_methods(
    address: str,
    methods: Iterable[str],
    *,
    block: Optional[int] = None,
    return_exceptions: bool = False,
) -> Tuple[Any]:
    """
    Asynchronously gather results from multiple contract methods.

    Args:
        address: The contract address.
        methods: An iterable of method names or encoded method calls.
        block: The block number to query. Defaults to None.
        return_exceptions: Whether to return exceptions or raise them. Defaults to False.

    Returns:
        A tuple containing the results of the method calls.

    Example:
        >>> from y.utils import gather_methods
        >>> address = "0x6B175474E89094C44Da98b954EedeAC495271d0F"  # DAI
        >>> methods = ["name()", "symbol()", "decimals()"]
        >>> results = await gather_methods(address, methods)
        >>> print(results)
        ('Dai Stablecoin', 'DAI', 18)

        >>> # Using raw method calls
        >>> methods = ["name()(string)", "symbol()(string)", "decimals()(uint8)"]
        >>> results = await gather_methods(address, methods)
        >>> print(results)
        ('Dai Stablecoin', 'DAI', 18)
    """
    methods = tuple(methods)
    gather_fn = _gather_methods_raw if "(" in methods[0] else _gather_methods_brownie
    return await gather_fn(
        address, methods, block=block, return_exceptions=return_exceptions
    )


@stuck_coro_debugger
async def _gather_methods_brownie(
    address: str,
    methods: Iterable[str],
    *,
    block: Optional[int] = None,
    return_exceptions: bool = False,
) -> Tuple[Any]:
    """
    Internal function to gather results using Brownie.

    This function uses the Contract.coroutine method to make asynchronous calls.

    Args:
        address: The contract address.
        methods: An iterable of method names.
        block: The block number to query. Defaults to the latest block.
        return_exceptions: Whether to return exceptions or raise them. Defaults to False.

    Returns:
        A tuple containing the results of the method calls.

    Example:
        >>> address = "0x6B175474E89094C44Da98b954EedeAC495271d0F"  # DAI
        >>> methods = ["name", "symbol", "decimals"]
        >>> results = await _gather_methods_brownie(address, methods)
        >>> print(results)
        ('Dai Stablecoin', 'DAI', 18)
    """
    # skip circular import
    from y import Contract

    contract = await Contract.coroutine(address)
    return await igather(
        (
            getattr(contract, method).coroutine(block_identifier=block)
            for method in methods
        ),
        return_exceptions=return_exceptions,
    )


@stuck_coro_debugger
async def _gather_methods_raw(
    address: str,
    methods: Iterable[str],
    *,
    block: Optional[int] = None,
    return_exceptions: bool = False,
) -> Tuple[Any]:
    """
    Internal function to gather results using raw calls.

    This function uses multicall.Call from the multicall library to make asynchronous calls.

    Args:
        address: The contract address.
        methods: An iterable of encoded method calls.
        block: The block number to query. Defaults to the latest block.
        return_exceptions: Whether to return exceptions or raise them. Defaults to False.

    Returns:
        A tuple containing the results of the method calls.

    Example:
        >>> address = "0x6B175474E89094C44Da98b954EedeAC495271d0F"  # DAI
        >>> methods = ["name()(string)", "symbol()(string)", "decimals()(uint8)"]
        >>> results = await _gather_methods_raw(address, methods)
        >>> print(results)
        ('Dai Stablecoin', 'DAI', 18)
    """
    return await igather(
        (Call(address, [method], block_id=block) for method in methods),
        return_exceptions=return_exceptions,
    )
