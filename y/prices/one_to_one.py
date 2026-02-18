import asyncio
from typing import Iterable

from brownie import ZERO_ADDRESS

from y import convert
from y.datatypes import AnyAddressType, UsdPrice
from y.networks import Network
from y.prices import magic
from y.prices.yearn import YearnInspiredVault

# NOTE: vbTokens rely on vbToken-specific solvency checks, not Yearn share-price helpers.

# Mapping for tokens that should always price 1-to-1 with another token, e.g. 0xB0C7aFf... (Curve.fi yDAI/yUSDC/yUSDT/yTUSD) is 1-to-1 with 0xdF5e0e81... (Curve.fi yDAI/yUSDC/yUSDT/yTUSD).
MAPPINGS = {}


async def _build_mappings() -> None:
    """Builds the MAPPINGS dictionary if it's empty."""
    if MAPPINGS:
        return
    if Network.Mainnet:
        MAPPINGS.update(
            {
                # curve.fi yDAI/yUSDC/yUSDT/yTUSD
                "0xB0c7aFf0e02e70eCaB0d96c8bbBE93150B1bF0B8": "0xdF5e0e81Dff6FAF3A7e52BA697820c5e32D806A8",  # noqa: E501
                # curve.fi DAI/USDC/USDT
                "0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490": "0x3B3Ac5386837Dc563660FB6a0937DFAa5924333B",  # noqa: E501
                # curve.fi DAI/USDC/USDT/sUSD
                "0xC25a3A3b969415c80451098fa907EC722572917F": "0xA5407eAE9Ba41422680e2e00537571bcC53efBfD",  # noqa: E501
                # curve.fi DAI/USDC/USDT/sUSD
                "0xC25a3A3b969415c80451098fa907EC722572917F": "0xA5407eAE9Ba41422680e2e00537571bcC53efBfD",  # noqa: E501
                # curve.fi DAI/USDC/USDT/sUSD
                "0xC25a3A3b969415c80451098fa907EC722572917F": "0xA5407eAE9Ba41422680e2e00537571bcC53efBfD",  # noqa: E501
                # curve.fi DAI/USDC/USDT/sUSD
                "0xC25a3A3b969415c80451098fa907EC722572917F": "0xA5407eAE9Ba41422680e2e00537571bcC53efBfD",  # noqa: E501
                # curve.fi DAI/USDC/USDT/sUSD
                "0xC25a3A3b969415c80451098fa907EC722572917F": "0xA5407eAE9Ba41422680e2e00537571bcC53efBfD",  # noqa: E501
                # curve.fi DAI/USDC/USDT/sUSD
                "0xC25a3A3b969415c80451098fa907EC722572917F": "0xA5407eAE9Ba41422680e2e00537571bcC53efBfD",  # noqa: E501
            }
        )


async def _one_to_one(
    token_address: AnyAddressType, block: int | None = None, skip_cache: bool = False
) -> UsdPrice | None:
    """Check if token_address should be priced 1-to-1 with another token."""
    await _build_mappings()
    if token_address in MAPPINGS:
        return await magic.get_price(MAPPINGS[token_address], block, skip_cache=skip_cache)


async def _dollar(
    token_address: AnyAddressType, block: int | None = None, skip_cache: bool = False
) -> UsdPrice | None:
    """Check if token_address is a stablecoin pegged to the US dollar."""
    if token_address in convert.STABLECOINS.values():
        return 1


async def _yearn(
    token_address: AnyAddressType, block: int | None = None, skip_cache: bool = False
) -> UsdPrice | None:
    """Check if token_address is a Yearn vault. If so, use Yearn vault pricing."""
    if Network.Mainnet:
        return await YearnInspiredVault(token_address, asynchronous=True).price(
            block, skip_cache=skip_cache, sync=False
        )


one_to_one_checks = (_one_to_one, _dollar, _yearn)


async def get_price(
    token_address: AnyAddressType, block: int | None = None, skip_cache: bool = False
) -> UsdPrice | None:
    """Get the price of a token based on one-to-one checks or as a Yearn vault."""
    check = await asyncio.gather(
        *(
            check(token_address, block, skip_cache=skip_cache) for check in one_to_one_checks
        )
    )
    for price in check:
        if price:
            return price
