"""Tests for the y._db.utils.purge module.

Unit tests that exercise validation logic (ValueError for inverted ranges,
function signatures, docstrings) run without a live database.  Tests that
require Pony ORM entity access are marked as integration tests and may be
skipped in environments where the full ypricemagic import chain is
unavailable (e.g. missing brownie / dank_mids / RPC connection).
"""

from __future__ import annotations

import importlib
import inspect
import sys
from datetime import datetime

import pytest

# ---------------------------------------------------------------------------
# Helpers – conditionally import the purge module
# ---------------------------------------------------------------------------

_PURGE_MODULE_PATH = "y._db.utils.purge"

_import_error: str | None = None
try:
    from y._db.utils.purge import (
        purge_prices_by_block_range,
        purge_prices_by_date_range,
        purge_prices_by_token,
    )
except Exception as exc:  # noqa: BLE001
    _import_error = f"{type(exc).__name__}: {exc}"
    # Provide stubs so the test file itself is importable even when the
    # real module cannot be loaded (missing brownie, dank_mids, etc.).
    purge_prices_by_token = None  # type: ignore[assignment]
    purge_prices_by_block_range = None  # type: ignore[assignment]
    purge_prices_by_date_range = None  # type: ignore[assignment]

_skip_if_no_import = pytest.mark.skipif(
    _import_error is not None,
    reason=f"Cannot import purge module: {_import_error}",
)


# ===================================================================
# 1. Validation tests – ValueError for inverted ranges
# ===================================================================


@_skip_if_no_import
class TestBlockRangeValidation:
    """purge_prices_by_block_range must raise ValueError when start > end."""

    def test_inverted_block_range_raises(self):
        with pytest.raises(ValueError, match="start_block.*must be <= end_block"):
            purge_prices_by_block_range(200, 100)

    def test_inverted_block_range_message_contains_values(self):
        with pytest.raises(ValueError) as exc_info:
            purge_prices_by_block_range(500, 100)
        assert "500" in str(exc_info.value)
        assert "100" in str(exc_info.value)


@_skip_if_no_import
class TestDateRangeValidation:
    """purge_prices_by_date_range must raise ValueError when start > end."""

    def test_inverted_date_range_raises(self):
        later = datetime(2024, 6, 1)
        earlier = datetime(2024, 1, 1)
        with pytest.raises(ValueError, match="start_date.*must be <= end_date"):
            purge_prices_by_date_range(later, earlier)

    def test_inverted_date_range_message_contains_values(self):
        later = datetime(2024, 12, 31)
        earlier = datetime(2024, 1, 1)
        with pytest.raises(ValueError) as exc_info:
            purge_prices_by_date_range(later, earlier)
        assert "2024-12-31" in str(exc_info.value)
        assert "2024-01-01" in str(exc_info.value)


# ===================================================================
# 2. Function signatures and docstrings
# ===================================================================


@_skip_if_no_import
class TestFunctionSignatures:
    """Verify the public API surface (argument names, return annotations, docs)."""

    def test_purge_by_token_signature(self):
        sig = inspect.signature(purge_prices_by_token)
        assert "address" in sig.parameters

    def test_purge_by_block_range_signature(self):
        sig = inspect.signature(purge_prices_by_block_range)
        params = list(sig.parameters)
        assert "start_block" in params
        assert "end_block" in params

    def test_purge_by_date_range_signature(self):
        sig = inspect.signature(purge_prices_by_date_range)
        params = list(sig.parameters)
        assert "start_date" in params
        assert "end_date" in params

    def test_purge_by_token_has_docstring(self):
        assert purge_prices_by_token.__doc__
        assert "ProcessingQueue" in purge_prices_by_token.__doc__

    def test_purge_by_block_range_has_docstring(self):
        assert purge_prices_by_block_range.__doc__
        assert "ProcessingQueue" in purge_prices_by_block_range.__doc__

    def test_purge_by_date_range_has_docstring(self):
        assert purge_prices_by_date_range.__doc__
        assert "ProcessingQueue" in purge_prices_by_date_range.__doc__


# ===================================================================
# 3. EEE_ADDRESS mapping logic
# ===================================================================


@_skip_if_no_import
class TestEEEAddressMapping:
    """Verify that purge_prices_by_token maps EEE_ADDRESS → WRAPPED_GAS_COIN."""

    def test_eee_address_is_mapped(self):
        """The function body should reference the EEE_ADDRESS mapping.

        We verify the source code contains the mapping rather than calling the
        function (which would require a live database session).
        """
        source = inspect.getsource(purge_prices_by_token)
        assert "EEE_ADDRESS" in source
        assert "WRAPPED_GAS_COIN" in source


# ===================================================================
# 4. Integration tests (require live database)
# ===================================================================


@pytest.mark.skipif(
    _import_error is not None,
    reason=f"Cannot import purge module: {_import_error}",
)
@pytest.mark.integration
class TestIntegrationPurge:
    """Integration tests that interact with the real Pony ORM database.

    These are only expected to pass when a Brownie + RPC environment is
    fully configured.  Mark them with ``-m integration`` to run explicitly.
    """

    def test_purge_nonexistent_token_returns_zero(self):
        """Purging a token that has no Price rows should return 0, not raise."""
        # Use a made-up address that is extremely unlikely to exist
        result = purge_prices_by_token(
            "0x0000000000000000000000000000000000000001"  # type: ignore[arg-type]
        )
        assert result == 0

    def test_purge_empty_block_range_returns_zero(self):
        """Purging a single block with no prices should return 0."""
        result = purge_prices_by_block_range(0, 0)
        assert result == 0

    def test_purge_equal_block_range(self):
        """start_block == end_block should not raise (single-block purge)."""
        result = purge_prices_by_block_range(1, 1)
        assert isinstance(result, int)

    def test_purge_empty_date_range_returns_zero(self):
        """Purging a date range with no data should return 0."""
        result = purge_prices_by_date_range(datetime(1970, 1, 1), datetime(1970, 1, 2))
        assert result == 0

    def test_purge_equal_date_range(self):
        """start_date == end_date should not raise."""
        ts = datetime(2020, 1, 1)
        result = purge_prices_by_date_range(ts, ts)
        assert isinstance(result, int)
