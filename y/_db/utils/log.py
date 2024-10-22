
from typing import final

from dank_mids.structs import Log


@final
class Log(Log, frozen=True, kw_only=True, array_like=True):
    """
    It works just like a :class:`~structs.Log` but it encodes to a tuple instead of a dict to save space since keys are known.
    """