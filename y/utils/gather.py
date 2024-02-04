
import asyncio
from typing import Any, Iterable, Optional, Tuple

from multicall import Call

async def gather_methods(
    address: str, 
    methods: Iterable[str], 
    *, 
    block: Optional[int] = None, 
    return_exceptions: bool = False,
) -> Tuple[Any]:
    methods = tuple(methods)
    gather_fn = _gather_methods_raw if "(" in methods[0] else _gather_methods_brownie
    return await gather_fn(address, methods, block=block, return_exceptions=return_exceptions)

async def _gather_methods_brownie(
    address: str, 
    methods: Iterable[str], 
    *, 
    block: Optional[int] = None, 
    return_exceptions: bool = False,
) -> Tuple[Any]:
    # skip circular import
    from y import Contract
    contract = await Contract.coroutine(address)
    return await asyncio.gather(*[getattr(contract, method).coroutine(block_identifier=block) for method in methods], return_exceptions=return_exceptions)

async def _gather_methods_raw(
    address: str, 
    methods: Iterable[str], 
    *, 
    block: Optional[int] = None, 
    return_exceptions: bool = False,
) -> Tuple[Any]:
    return await asyncio.gather(*[Call(address, [method], block_id=block) for method in methods], return_exceptions=return_exceptions)