
import threading
from collections import defaultdict
from typing import Any, DefaultDict, Dict, Generic, Optional, Tuple, TypeVar

import a_sync
from a_sync import _kwargs
from checksum_dict import ChecksumAddressDict
from checksum_dict.base import AnyAddressOrContract

T = TypeVar("T", bound=object)


class ChecksumASyncSingletonMeta(a_sync._meta.ASyncMeta, Generic[T]):
    def __init__(cls, name, bases, namespace):
        super().__init__(name, bases, namespace)
        cls.__instances: DefaultDict[bool, ChecksumAddressDict[T]] = defaultdict(ChecksumAddressDict)
        cls.__locks = defaultdict(lambda: defaultdict(threading.Lock))
        cls.__locks_lock: threading.Lock = threading.Lock()
    
    def __call__(cls, address: AnyAddressOrContract, *args, **kwargs) -> T:  # type: ignore
        # NOTE This will only work if you init your objects using a kwarg not a positional arg
        # TODO Make it work with posiional args
        address = str(address)
        is_sync = cls.__a_sync_instance_will_be_sync__(args, kwargs)
        try:
            instance = cls.__instances[is_sync][address]
        except KeyError:
            with cls.__get_address_lock(address, is_sync):
                # Try to get the instance again, in case it was added while waiting for the lock
                try:
                    instance =  cls.__instances[is_sync][address]
                except KeyError:
                    instance = super().__call__(address, *args, **kwargs)
                    cls.__instances[is_sync][address] = instance
            cls.__delete_address_lock(address, is_sync)
        assert instance.asynchronous is not is_sync, f"You must initialize your objects with 'asynchronous' specified as a kwarg, not a positional arg. {instance} {kwargs} {is_sync} {instance.asynchronous} {args} {kwargs}"
        return instance

    def __get_address_lock(cls, address: AnyAddressOrContract, is_sync: bool) -> threading.Lock:
        """ Makes sure the singleton is actually a singleton. """
        with cls.__locks_lock:
            return cls.__locks[is_sync][address]
    
    def __delete_address_lock(cls, address: AnyAddressOrContract, is_sync: bool) -> None:
        """ No need to maintain locks for initialized addresses. """
        with cls.__locks_lock:
            try:
                del cls.__locks[is_sync][address]
            except KeyError:
                pass