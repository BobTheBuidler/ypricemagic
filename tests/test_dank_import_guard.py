import importlib.util
import sys
import types
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).resolve().parents[1] / "y" / "_dank_import_guard.py"


def _load_guard_module(name: str):
    spec = importlib.util.spec_from_file_location(name, MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    loader = spec.loader
    assert loader is not None
    loader.exec_module(module)
    return module


def test_import_dank_w3_returns_underlying_object(monkeypatch):
    guard = _load_guard_module("y_dank_import_guard_success")

    sentinel = object()
    fake_dank_mids = types.ModuleType("dank_mids")
    fake_dank_mids.dank_web3 = sentinel
    monkeypatch.setitem(sys.modules, "dank_mids", fake_dank_mids)

    assert guard.import_dank_w3() is sentinel


def test_import_dank_w3_raises_actionable_error_with_cause(monkeypatch):
    guard = _load_guard_module("y_dank_import_guard_failure")

    fake_dank_mids = types.ModuleType("dank_mids")

    def _missing_attr(name: str):
        if name == "dank_web3":
            raise guard.BrowniePatchNotInitializedError("dank_web3")
        raise AttributeError(name)

    setattr(fake_dank_mids, "__getattr__", _missing_attr)
    monkeypatch.setitem(sys.modules, "dank_mids", fake_dank_mids)

    with pytest.raises(guard.DankMidsImportOrderError) as exc_info:
        guard.import_dank_w3()

    message = str(exc_info.value)
    assert "Invalid startup import/init order detected for ypricemagic" in message
    assert "Process restart is required." in message
    assert "Brownie connects before importing `y` or `dank_mids`" in message
    assert isinstance(exc_info.value.__cause__, guard.BrowniePatchNotInitializedError)
