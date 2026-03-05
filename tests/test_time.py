from types import SimpleNamespace

import pytest

import y._db.utils.utils as db
import y.time as ytime
from y.networks import Network


@pytest.fixture(autouse=True)
def clear_get_block_timestamp_cache():
    if hasattr(ytime.get_block_timestamp, "clear"):
        ytime.get_block_timestamp.clear(warn=False)


def test_get_block_timestamp_erigon_supports_int_like_header_timestamp(monkeypatch):
    height = 987_654_301
    expected_timestamp = 1_700_000_001
    observed = {}

    class UnixTimestampLike:
        def __int__(self):
            return expected_timestamp

    def fake_get_block_timestamp(_height, sync=False):  # noqa: ARG001
        return None

    def fake_set_block_timestamp(block, timestamp, sync=False):  # noqa: ARG001
        observed["set"] = (block, timestamp, sync)

    def fake_request_blocking(method, params):
        observed["request"] = (method, params)
        return SimpleNamespace(timestamp=UnixTimestampLike())

    monkeypatch.setattr(ytime, "CHAINID", Network.Mainnet)
    monkeypatch.setattr(ytime, "get_ethereum_client", lambda: "erigon")
    monkeypatch.setattr(db, "get_block_timestamp", fake_get_block_timestamp)
    monkeypatch.setattr(db, "set_block_timestamp", fake_set_block_timestamp)
    monkeypatch.setattr(ytime.web3.manager, "request_blocking", fake_request_blocking)

    assert ytime.get_block_timestamp(height) == expected_timestamp
    assert observed["request"] == ("erigon_getHeaderByNumber", [height])
    assert observed["set"] == (height, expected_timestamp, True)


def test_get_block_timestamp_erigon_supports_hex_timestamp_string(monkeypatch):
    height = 987_654_302
    expected_timestamp = 1_700_000_002
    observed = {}

    def fake_get_block_timestamp(_height, sync=False):  # noqa: ARG001
        return None

    def fake_set_block_timestamp(block, timestamp, sync=False):  # noqa: ARG001
        observed["set"] = (block, timestamp, sync)

    def fake_request_blocking(_method, _params):
        return SimpleNamespace(timestamp=hex(expected_timestamp))

    monkeypatch.setattr(ytime, "CHAINID", Network.Mainnet)
    monkeypatch.setattr(ytime, "get_ethereum_client", lambda: "erigon")
    monkeypatch.setattr(db, "get_block_timestamp", fake_get_block_timestamp)
    monkeypatch.setattr(db, "set_block_timestamp", fake_set_block_timestamp)
    monkeypatch.setattr(ytime.web3.manager, "request_blocking", fake_request_blocking)

    assert ytime.get_block_timestamp(height) == expected_timestamp
    assert observed["set"] == (height, expected_timestamp, True)


@pytest.mark.asyncio_cooperative
async def test_get_block_timestamp_async_erigon_supports_int_like_header_timestamp(monkeypatch):
    height = 987_654_303
    expected_timestamp = 1_700_000_003
    observed = {}

    class UnixTimestampLike:
        def __int__(self):
            return expected_timestamp

    async def fake_get_block_timestamp(_height, sync=False):  # noqa: ARG001
        return None

    def fake_set_block_timestamp(block, timestamp):
        observed["set"] = (block, timestamp)

    async def fake_get_client():
        return "erigon"

    async def fake_coro_request(method, params):
        observed["request"] = (method, params)
        return SimpleNamespace(timestamp=UnixTimestampLike())

    async def fake_fallback(_height):  # pragma: no cover
        raise AssertionError("fallback path should not run for erigon header timestamps")

    monkeypatch.setattr(ytime, "CHAINID", Network.Mainnet)
    monkeypatch.setattr(ytime, "get_ethereum_client_async", fake_get_client)
    monkeypatch.setattr(db, "get_block_timestamp", fake_get_block_timestamp)
    monkeypatch.setattr(db, "set_block_timestamp", fake_set_block_timestamp)
    monkeypatch.setattr(ytime.dank_mids.web3.manager, "coro_request", fake_coro_request)
    monkeypatch.setattr(ytime.dank_mids.eth, "get_block_timestamp", fake_fallback)

    undecorated = ytime.get_block_timestamp_async.__wrapped__.__wrapped__
    assert await undecorated(height) == expected_timestamp
    assert observed["request"] == ("erigon_getHeaderByNumber", [height])
    assert observed["set"] == (height, expected_timestamp)


@pytest.mark.asyncio_cooperative
async def test_get_block_timestamp_async_erigon_supports_hex_timestamp_string(monkeypatch):
    height = 987_654_304
    expected_timestamp = 1_700_000_004
    observed = {}

    async def fake_get_block_timestamp(_height, sync=False):  # noqa: ARG001
        return None

    def fake_set_block_timestamp(block, timestamp):
        observed["set"] = (block, timestamp)

    async def fake_get_client():
        return "erigon"

    async def fake_coro_request(_method, _params):
        return SimpleNamespace(timestamp=hex(expected_timestamp))

    monkeypatch.setattr(ytime, "CHAINID", Network.Mainnet)
    monkeypatch.setattr(ytime, "get_ethereum_client_async", fake_get_client)
    monkeypatch.setattr(db, "get_block_timestamp", fake_get_block_timestamp)
    monkeypatch.setattr(db, "set_block_timestamp", fake_set_block_timestamp)
    monkeypatch.setattr(ytime.dank_mids.web3.manager, "coro_request", fake_coro_request)

    undecorated = ytime.get_block_timestamp_async.__wrapped__.__wrapped__
    assert await undecorated(height) == expected_timestamp
    assert observed["set"] == (height, expected_timestamp)
