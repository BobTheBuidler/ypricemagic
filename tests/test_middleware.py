from types import SimpleNamespace

import pytest

from y.networks import Network
from y.utils import middleware


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
