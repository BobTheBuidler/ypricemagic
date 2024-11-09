from typing import final

import evmspec


@final
class Log(evmspec.log.Log, frozen=True, kw_only=True, array_like=True):
    """
    It works just like a :class:`~evmspec.log.Log` but it encodes to a tuple instead of a dict to save space since keys are known.
    """
