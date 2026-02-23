from typing import Any, Final

from dank_mids.exceptions import BrowniePatchNotInitializedError

_INVALID_IMPORT_ORDER_MESSAGE: Final = (
    "Invalid startup import/init order detected for ypricemagic: "
    "`dank_mids` brownie patch is not initialized. "
    "Process restart is required. "
    "Fix your entrypoint startup order so Brownie connects before importing `y` or `dank_mids`."
)


class DankMidsImportOrderError(RuntimeError):
    """Raised when ypricemagic detects an invalid dank_mids/Brownie init order."""

    def __init__(self) -> None:
        super().__init__(_INVALID_IMPORT_ORDER_MESSAGE)


def import_dank_w3() -> Any:
    """Import dank_mids.dank_web3 and wrap init-order failures with actionable guidance."""
    try:
        from dank_mids import dank_web3 as dank_w3
    except BrowniePatchNotInitializedError as exc:
        raise DankMidsImportOrderError() from exc
    return dank_w3
