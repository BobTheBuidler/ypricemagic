
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Type, TypeVar

from hexbytes import HexBytes
from web3.datastructures import AttributeDict

T = TypeVar('T')

executor = ThreadPoolExecutor(16)

def enc_hook(obj: Any) -> bytes:
    if isinstance(obj, AttributeDict):
        return dict(obj)
    elif isinstance(obj, HexBytes):
        return obj.hex()
    raise NotImplementedError(obj)

def dec_hook(typ: Type[T], obj: bytes) -> T:
    if typ == HexBytes:
        return HexBytes(obj)
    raise ValueError(f"{typ} is not a valid type for decoding")
