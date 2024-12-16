import threading
from collections import defaultdict
from typing import DefaultDict, Generic, TypeVar

from a_sync.a_sync._meta import ASyncMeta
from checksum_dict import ChecksumAddressDict
from checksum_dict.base import AnyAddressOrContract

T = TypeVar("T", bound=object)


class ChecksumASyncSingletonMeta(ASyncMeta, Generic[T]):
    """
    A metaclass for creating singleton instances with checksummed addresses and asynchronous capabilities.

    This metaclass extends :class:`~a_sync.a_sync._meta.ASyncMeta` to ensure that only one instance of a class
    is created for each synchronous or asynchronous context, with the added functionality of checksumming
    Ethereum addresses using :class:`~checksum_dict.ChecksumAddressDict`.

    The differentiation between synchronous and asynchronous contexts is achieved by using the
    `__a_sync_instance_will_be_sync__` method to determine the context during instance creation.
    Instances are stored in `cls.__instances`, which is a `DefaultDict` of `ChecksumAddressDict` keyed by the context
    (synchronous or asynchronous). This ensures that separate instances are created for each context.

    Examples:
        >>> class MySingleton(metaclass=ChecksumASyncSingletonMeta):
        ...     def __init__(self, address, asynchronous=False):
        ...         self.address = address
        ...         self.asynchronous = asynchronous
        ...
        >>> instance1 = MySingleton('0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb', asynchronous=True)
        >>> instance2 = MySingleton('0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb', asynchronous=True)
        >>> assert instance1 is instance2

    See Also:
        - :class:`~a_sync.a_sync._meta.ASyncMeta`
        - :class:`~checksum_dict.ChecksumAddressDict`
    """

    def __init__(cls, name, bases, namespace):
        """
        Initialize the metaclass with a name, bases, and namespace.

        Args:
            name: The name of the class being created.
            bases: A tuple of base classes.
            namespace: A dictionary representing the class namespace.
        """

        super().__init__(name, bases, namespace)

        cls.__instances: DefaultDict[bool, ChecksumAddressDict[T]] = defaultdict(
            ChecksumAddressDict
        )
        """A dictionary to store singleton instances, keyed by their synchronous or asynchronous context."""

        cls.__locks = defaultdict(lambda: defaultdict(threading.Lock))
        """A dictionary to store locks for each address to ensure thread-safe instance creation."""

        cls.__locks_lock: threading.Lock = threading.Lock()
        """A lock to ensure thread-safe access to the locks dictionary."""

    def __call__(cls, address: AnyAddressOrContract, *args, **kwargs) -> T:  # type: ignore
        """
        Create or retrieve a singleton instance for the given address.

        This method ensures that only one instance of a class is created for each address
        in a synchronous or asynchronous context. The address is checksummed to ensure consistency.

        Note:
            This will only work if you init your objects using a kwarg not a positional arg.
            TODO: Make it work with positional args.

        Args:
            address: The address for which to create or retrieve the singleton instance.
            *args: Additional positional arguments for instance creation.
            **kwargs: Additional keyword arguments for instance creation.

        Raises:
            AssertionError: If the instance's asynchronous state does not match the expected state.

        Examples:
            >>> class MySingleton(metaclass=ChecksumASyncSingletonMeta):
            ...     def __init__(self, address, asynchronous=False):
            ...         self.address = address
            ...         self.asynchronous = asynchronous
            ...
            >>> instance1 = MySingleton('0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb', asynchronous=True)
            >>> instance2 = MySingleton('0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb', asynchronous=True)
            >>> assert instance1 is instance2

        See Also:
            - :class:`~checksum_dict.ChecksumAddressDict`
        """
        address = str(address)
        is_sync = cls.__a_sync_instance_will_be_sync__(args, kwargs)
        try:
            instance = cls.__instances[is_sync][address]
        except KeyError:
            with cls.__get_address_lock(address, is_sync):
                # Try to get the instance again, in case it was added while waiting for the lock
                try:
                    instance = cls.__instances[is_sync][address]
                except KeyError:
                    instance = super().__call__(address, *args, **kwargs)
                    cls.__instances[is_sync][address] = instance
            cls.__delete_address_lock(address, is_sync)
        if instance.asynchronous is is_sync:
            raise RuntimeError(
                "You must initialize your objects with 'asynchronous' specified as a kwarg, not a positional arg. "
                + f"{instance} {kwargs} {is_sync} {instance.asynchronous} {args} {kwargs}"
            )
        return instance

    def __get_address_lock(
        self, address: AnyAddressOrContract, is_sync: bool
    ) -> threading.Lock:
        """
        Acquire a lock for the given address to ensure thread safety.

        This method ensures that the singleton instance creation is thread-safe by
        acquiring a lock for the specific address and context.

        Args:
            address: The address for which to acquire the lock.
            is_sync: The context (synchronous or asynchronous) for which to acquire the lock.

        Returns:
            A threading.Lock object for the given address and context.

        Examples:
            >>> meta = ChecksumASyncSingletonMeta('MySingleton', (), {})
            >>> lock = meta._ChecksumASyncSingletonMeta__get_address_lock('0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb', True)
        """
        with self.__locks_lock:
            return self.__locks[is_sync][address]

    def __delete_address_lock(
        self, address: AnyAddressOrContract, is_sync: bool
    ) -> None:  # sourcery skip: use-contextlib-suppress
        """
        Delete the lock for an address once the instance is created.

        This method removes the lock for an address after the singleton instance
        has been successfully created, freeing up resources.

        Args:
            address: The address for which to delete the lock.
            is_sync: The context (synchronous or asynchronous) for which to delete the lock.

        Examples:
            >>> meta = ChecksumASyncSingletonMeta('MySingleton', (), {})
            >>> meta._ChecksumASyncSingletonMeta__delete_address_lock('0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb', True)
        """
        with self.__locks_lock:
            try:
                del self.__locks[is_sync][address]
            except KeyError:
                pass
