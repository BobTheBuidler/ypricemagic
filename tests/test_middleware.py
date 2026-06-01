from types import SimpleNamespace
from uuid import uuid4

import pytest
from web3 import Web3

from y.networks import Network
from y.utils import middleware


def _unique_address():
    return f"0x{uuid4().hex}{uuid4().hex[:8]}"


def _make_wrapped_request():
    calls = []

    def make_request(method, params):
        calls.append((method, params))
        return {"jsonrpc": "2.0", "id": len(calls), "result": f"result-{len(calls)}"}

    wrapped = middleware.GetCodeCacheMiddleware(None).wrap_make_request(make_request)
    return wrapped, calls


def test_getcode_latest_is_cached():
    wrapped, calls = _make_wrapped_request()
    params = [_unique_address(), "latest"]

    first = wrapped("eth_getCode", params)
    second = wrapped("eth_getCode", params)

    assert first == second
    assert len(calls) == 1


def test_non_getcode_calls_pass_through():
    wrapped, calls = _make_wrapped_request()
    params = [_unique_address(), "latest"]

    first = wrapped("eth_getBalance", params)
    second = wrapped("eth_getBalance", params)

    assert first != second
    assert len(calls) == 2


def test_getcode_non_latest_calls_pass_through():
    wrapped, calls = _make_wrapped_request()
    params = [_unique_address(), "0x1"]

    first = wrapped("eth_getCode", params)
    second = wrapped("eth_getCode", params)

    assert first != second
    assert len(calls) == 2


def test_getcode_cache_middleware_class_can_be_added_to_web3_v7_onion():
    web3 = Web3()

    web3.middleware_onion.add(middleware.GetCodeCacheMiddleware)

    assert middleware.GetCodeCacheMiddleware in tuple(web3.middleware_onion)


class _FakeMiddlewareOnion:
    def __init__(self, exc=None):
        self.exc = exc
        self.inject_calls = []

    def inject(self, middleware_obj, layer):
        self.inject_calls.append((middleware_obj, layer))
        if self.exc is not None:
            raise self.exc


def test_setup_geth_poa_middleware_injects_v7_middleware(monkeypatch):
    onion = _FakeMiddlewareOnion()
    monkeypatch.setattr(middleware, "web3", SimpleNamespace(middleware_onion=onion))

    middleware.setup_geth_poa_middleware()

    assert onion.inject_calls == [(middleware._poa_middleware, 0)]


def test_setup_geth_poa_middleware_ignores_duplicate_unnamed_middleware(monkeypatch):
    onion = _FakeMiddlewareOnion(ValueError("You can't add the same un-named instance twice"))
    monkeypatch.setattr(middleware, "web3", SimpleNamespace(middleware_onion=onion))

    middleware.setup_geth_poa_middleware()

    assert onion.inject_calls == [(middleware._poa_middleware, 0)]


def test_setup_geth_poa_middleware_reraises_other_value_errors(monkeypatch):
    onion = _FakeMiddlewareOnion(ValueError("boom"))
    monkeypatch.setattr(middleware, "web3", SimpleNamespace(middleware_onion=onion))

    with pytest.raises(ValueError, match="boom"):
        middleware.setup_geth_poa_middleware()


@pytest.mark.parametrize(
    "chain_id",
    (Network.BinanceSmartChain, Network.Polygon, Network.Avalanche),
)
def test_remove_legacy_poa_middleware_target_chains(chain_id, monkeypatch):
    onion = ["cache", "poa-first", "poa-second", "other"]
    monkeypatch.setattr(middleware, "chain", SimpleNamespace(id=chain_id))
    monkeypatch.setattr(middleware, "web3", SimpleNamespace(middleware_onion=onion))

    middleware.remove_legacy_poa_middleware()

    assert onion == ["cache", "poa-second", "other"]


@pytest.mark.parametrize("chain_id", (Network.Mainnet, Network.Optimism))
def test_remove_legacy_poa_middleware_non_target_chains_unchanged(chain_id, monkeypatch):
    onion = ["cache", "poa-first", "other"]
    monkeypatch.setattr(middleware, "chain", SimpleNamespace(id=chain_id))
    monkeypatch.setattr(middleware, "web3", SimpleNamespace(middleware_onion=onion))

    middleware.remove_legacy_poa_middleware()

    assert onion == ["cache", "poa-first", "other"]


def test_remove_legacy_poa_middleware_is_idempotent(monkeypatch):
    onion = ["cache", "poa-first", "other"]
    monkeypatch.setattr(middleware, "chain", SimpleNamespace(id=Network.Polygon))
    monkeypatch.setattr(middleware, "web3", SimpleNamespace(middleware_onion=onion))

    middleware.remove_legacy_poa_middleware()
    middleware.remove_legacy_poa_middleware()

    assert onion == ["cache", "other"]
