"""Tests for Uniswap price fetching functions.

This module contains asynchronous tests for verifying price retrieval via the Uniswap multiplexer
across different Uniswap versions (V1, V2, and V3). In particular, note that for Uniswap V2 the test now uses
the primary router determined via liquidity depth via :meth:`~y.prices.dex.uniswap.uniswap.UniswapMultiplexer.routers_by_depth`.

See Also:
    :class:`~y.prices.dex.uniswap.uniswap.UniswapMultiplexer`
"""

import pytest
from a_sync import cgather
from brownie import chain

from tests.fixtures import async_uni_v1, mutate_addresses
from y.networks import Network
from y.prices import magic
from y.prices.dex.uniswap import v3
from y.prices.dex.uniswap.uniswap import uniswap_multiplexer

V1_TOKENS = {
    Network.Mainnet: [
        "0x6B175474E89094C44Da98b954EedeAC495271d0F",
        "0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2",
        "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
    ],
}.get(chain.id, [])

V2_TOKENS = {
    Network.Mainnet: [
        "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9",
        "0xBA11D00c5f74255f56a5E366F4F77f5A186d7f55",
        "0xc00e94Cb662C3520282E6f5717214004A7f26888",
        "0xD533a949740bb3306d119CC777fa900bA034cd52",
        "0x6B175474E89094C44Da98b954EedeAC495271d0F",
        "0x6810e776880C02933D47DB1b9fc05908e5386b96",
        "0xc944E90C64B2c07662A292be6244BDf05Cda44a7",
        "0x514910771AF9Ca656af840dff83E8264EcF986CA",
        "0x0F5D2fB29fb7d3CFeE444a200298f468908cC942",
        "0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2",
        "0xec67005c4E498Ec7f55E092bd1d35cbC47C91892",
        "0x4fE83213D56308330EC302a8BD641f1d0113A4Cc",
        "0xC011a73ee8576Fb46F5E1c5751cA3B9Fe0af2a6F",
        "0x04Fa0d235C4abf4BcF4787aF4CF447DE572eF828",
        "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
        "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        "0xdAC17F958D2ee523a2206206994597C13D831ec7",
        "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
        "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        "0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e",
        "0xE41d2489571d322189246DaFA5ebDe1F4699F498",
    ],
}.get(chain.id, [])

V2_TOKENS = mutate_addresses(V2_TOKENS)


@pytest.mark.parametrize("token", V1_TOKENS)
@pytest.mark.asyncio_cooperative
async def test_uniswap_v1(token, async_uni_v1):
    """Test Uniswap V1 price fetching.

    This test concurrently retrieves the price using an asynchronous Uniswap V1 caller and the generic
    :func:`~y.prices.magic.get_price` function. It verifies that the prices obtained from both methods are
    consistent within a 5% relative tolerance.

    Args:
        token: The token address to query.
        async_uni_v1: Fixture providing an asynchronous Uniswap V1 instance.

    See Also:
        :meth:`~y.prices.dex.uniswap.uniswap.UniswapMultiplexer.get_price`
    """
    price, alt_price = await cgather(
        async_uni_v1.get_price(token, None),
        magic.get_price(token, skip_cache=True, sync=False),
    )
    print(token, price, alt_price)
    # check if price is within 5% range
    assert price == pytest.approx(alt_price, rel=5e-2)


@pytest.mark.parametrize("token", V2_TOKENS)
@pytest.mark.asyncio_cooperative
async def test_uniswap_v2(token):
    """Test Uniswap V2 price fetching.

    This test retrieves the list of routers sorted by liquidity depth for the provided token by calling
    :meth:`~y.prices.dex.uniswap.uniswap.UniswapMultiplexer.routers_by_depth`, and then concurrently fetches
    price data from the selected router and from the generic :func:`~y.prices.magic.get_price` function.
    The test verifies that the prices obtained are consistent within a 5% relative tolerance.

    Args:
        token: The token address to query.

    See Also:
        :meth:`~y.prices.dex.uniswap.uniswap.UniswapMultiplexer.routers_by_depth`
    """
    deepest_router = await uniswap_multiplexer.deepest_router(token, sync=False)
    price, alt_price = await cgather(
        deepest_router.get_price(token, skip_cache=True, sync=False),
        magic.get_price(token, skip_cache=True, sync=False),
    )
    print(token, price, alt_price)
    assert price == pytest.approx(alt_price, rel=5e-2)


@pytest.mark.parametrize("token", V2_TOKENS)
@pytest.mark.asyncio_cooperative
async def test_uniswap_v3(token):
    """Test Uniswap V3 price fetching.

    This test concurrently retrieves pricing data using the Uniswap V3 router and the generic
    :func:`~y.prices.magic.get_price` function. It ensures that the price returned by the Uniswap V3 router
    is within a 5% relative tolerance of the price obtained from the magic fetch.

    Args:
        token: The token address to query.

    See Also:
        :meth:`~y.prices.dex.uniswap.v3.uniswap_v3.get_price`
    """
    price, alt_price = await cgather(
        v3.uniswap_v3.get_price(token, skip_cache=True, sync=False),
        magic.get_price(token, skip_cache=True, sync=False),
    )
    print(token, price, alt_price)
    assert price == pytest.approx(alt_price, rel=5e-2)
