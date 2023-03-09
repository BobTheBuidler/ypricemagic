
import threading
from typing import Any, Dict, Optional, Tuple, TypeVar


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


'''
class NoFlagsFound(BaseException):
    pass

class TooManyFlags(BaseException):
    pass

def get_flag_name(kwargs: dict) -> str:
    return _get_flag_name(kwargs)

def get_flag_name_from_signature(signature: inspect.Signature) -> str:
    print(signature)
    print(signature.parameters)
    return _get_flag_name(signature.parameters)

def _get_flag_name(_in: dict) -> str:
    present_flags = [flag for flag in a_sync._flags.VIABLE_FLAGS if flag in _in]
    if len(present_flags) == 0:
        err = "There are no viable a_sync flags present in 'kwargs':\n"
        err += f"Viable flags: {a_sync._flags.VIABLE_FLAGS}\n"
        err += f"kwargs keys: {_in.keys()}\n"
        err += "This is likely an issue with a custom subclass definition."
        raise NoFlagsFound(err)
    if len(present_flags) != 1:
        err = "There are multiple a_sync flags present in 'kwargs' and there should only be one.\n"
        err += f"Present flags: {present_flags}\n"
        err += "This is likely an issue with a custom subclass definition."
        raise TooManyFlags(err)
    return present_flags[0]

def get_flag_value(flag: str, kwargs: dict) -> bool:
    flag_value = kwargs[flag]
    if not isinstance(flag_value, bool):
        raise TypeError(f"'{flag}' should be boolean. You passed {flag_value}.")
    return flag_value

def negate_if_necessary(flag: str, flag_value: bool):
    if flag in a_sync._flags.AFFIRMATIVE_FLAGS:
        return bool(flag_value)
    elif flag in a_sync._flags.NEGATIVE_FLAGS:
        return bool(not flag_value)
    raise ValueError(f'This code should not be reached. This is likely an issue with a custom subclass definition.')

def is_sync_from_kwargs(kwargs: dict) -> bool:
    flag = get_flag_name(kwargs)
    flag_value = get_flag_value(flag, kwargs)
    return negate_if_necessary(flag, flag_value)


def get_cls_default_mode(cls: type) -> bool:
    signature = inspect.signature(cls.__init__)
    print(cls)
    flag = get_flag_name_from_signature(signature)
    flag_value = signature.parameters[flag].default
    if flag_value is inspect._empty:
        raise Exception("The implementation for 'cls' uses an arg to specify sync mode, instead of a kwarg. We are unable to proceed. I suppose we can extend the code to accept positional arg flags if necessary")
    #validate_flag_value()
    return negate_if_necessary(flag, flag_value)

def is_sync(cls: type, kwargs: dict) -> bool:
    try:
        return is_sync_from_kwargs(kwargs)
    except NoFlagsFound:
        return get_cls_default_mode(cls)

class ASyncSingletonMeta(ASyncMeta):
    def __init__(cls, name: str, bases: Tuple[type, ...], namespace: Dict[str, Any]) -> None:
        cls.__instances: Dict[bool, T] = {}
        cls.__lock = threading.Lock()
        super().__init__(name, bases, namespace)

    def __call__(cls, *args: Any, **kwargs: Any) -> T:
        instance_is_sync = is_sync(cls, kwargs)
        if instance_is_sync not in cls.__instances:
            with cls.__lock:
                # Check again in case `__instance` was set while we were waiting for the lock.
                if instance_is_sync not in cls.__instances:
                    cls.__instances[instance_is_sync] = super().__call__(*args, **kwargs)
        return cls.__instances[instance_is_sync]

class ASyncSingleton(a_sync.ASyncGenericBase, metaclass=ASyncSingletonMeta):
    #def __getattribute__(self, __name: str) -> Any:
    #    return getattr(self, __name)
    pass

'''