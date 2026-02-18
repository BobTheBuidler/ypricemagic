import logging
from dataclasses import dataclass
from decimal import Decimal

import a_sync
from brownie import ZERO_ADDRESS, chain

from y import convert
from y._decorators import stuck_coro_debugger
from y.contracts import Contract
from y.datatypes import Address, AnyAddressType, Block, UsdPrice
from y.exceptions import PriceError
from y.prices import magic
from y.utils.raw_calls import raw_call

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class VbTokenConfig:
    vbtoken: Address
    underlying: Address


VBTOKEN_ALLOWLIST: dict[int, dict[Address, VbTokenConfig]] = {
    1: {
        # Agglayer vault bridge registry: L1 Mainnet vbTokens and underlyings.
        # Katana vbTokens are bridged assets (ERC-20) and are not supported without
        # a dedicated allowlist entry and config.
        "0x31A5684983EeE865d943A696AAC155363bA024f9": VbTokenConfig(
            vbtoken="0x31A5684983EeE865d943A696AAC155363bA024f9",
            underlying="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        ),
        "0x4aE82D8CDbDeF9aE3C62f3fD8c3631fF57C12e9A": VbTokenConfig(
            vbtoken="0x4aE82D8CDbDeF9aE3C62f3fD8c3631fF57C12e9A",
            underlying="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        ),
        "0x2F71340c2682E12d7be5cEBf3bDd0074f1B406f3": VbTokenConfig(
            vbtoken="0x2F71340c2682E12d7be5cEBf3bDd0074f1B406f3",
            underlying="0xdAC17F958D2ee523a2206206994597C13D831ec7",
        ),
        "0x540794E5a77A735EF64c8b0d1E1ee8fefc29cE08": VbTokenConfig(
            vbtoken="0x540794E5a77A735EF64c8b0d1E1ee8fefc29cE08",
            underlying="0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
        ),
        "0xC76b15F20932BFE39F5EaB1d806c39208D9fCfA6": VbTokenConfig(
            vbtoken="0xC76b15F20932BFE39F5EaB1d806c39208D9fCfA6",
            underlying="0xC0d6b3A65b0dC57351bA93A5016Bef8A749dC104",
        ),
    }
}

VBTOKEN_SOLVENCY_MIN = Decimal("0.9995")
VBTOKEN_SOLVENCY_MAX = Decimal("1.01")


def _allowlist_for_chain(chain_id: int | None = None) -> dict[Address, VbTokenConfig]:
    return VBTOKEN_ALLOWLIST.get(chain_id or chain.id, {})


@a_sync.a_sync(default="sync", cache_type="memory")
async def is_vbtoken(token_address: AnyAddressType) -> bool:
    token_address = await convert.to_address_async(token_address)
    return token_address in _allowlist_for_chain()


async def _resolve_config(token_address: AnyAddressType) -> VbTokenConfig | None:
    token_address = await convert.to_address_async(token_address)
    return _allowlist_for_chain().get(token_address)


@a_sync.a_sync(default="sync", cache_type="memory")
async def get_underlying_address(token_address: AnyAddressType) -> Address | None:
    config = await _resolve_config(token_address)
    return config.underlying if config else None


@stuck_coro_debugger
async def _assets_per_share(token_address: Address, block: Block | None = None) -> Decimal | None:
    contract = await Contract.coroutine(token_address)

    try:
        assets = await contract.convertToAssets.coroutine(1, block_identifier=block)
    except Exception as exc:
        logger.debug("vbToken %s convertToAssets failed: %s", token_address, exc)
        assets = None

    if assets is None:
        total_assets = await raw_call(
            token_address,
            "totalAssets()",
            output="int",
            block=block,
            return_None_on_failure=True,
            sync=False,
        )
        total_supply = await raw_call(
            token_address,
            "totalSupply()",
            output="int",
            block=block,
            return_None_on_failure=True,
            sync=False,
        )
        if not total_assets or not total_supply:
            return None
        assets = Decimal(total_assets) / Decimal(total_supply)
    else:
        assets = Decimal(assets)

    return assets


async def _check_solvency(
    token_address: Address,
    underlying_address: Address,
    block: Block | None,
    assets_per_share: Decimal,
    skip_cache: bool,
) -> None:
    # Use vault accounting (assets_per_share * underlying_price) as a sanity check.
    # This fails closed to avoid silently accepting non-1:1 bridged or depegged assets.
    underlying_price = await magic.get_price(
        underlying_address, block=block, skip_cache=skip_cache, sync=False
    )
    if underlying_price is None:
        raise PriceError(f"No underlying price for vbToken {token_address}")

    ratio = (assets_per_share * Decimal(underlying_price)) / Decimal(underlying_price)
    if ratio < VBTOKEN_SOLVENCY_MIN or ratio > VBTOKEN_SOLVENCY_MAX:
        raise PriceError(
            f"vbToken {token_address} solvency guard failed: ratio {ratio}"
        )


@a_sync.a_sync(default="sync")
async def get_price(
    token_address: AnyAddressType,
    block: Block | None = None,
    skip_cache: bool = False,
) -> UsdPrice | None:
    config = await _resolve_config(token_address)
    if config is None:
        return None

    token_address = config.vbtoken
    underlying_address = config.underlying

    assets_per_share = await _assets_per_share(token_address, block)
    if assets_per_share is None:
        raise PriceError(f"vbToken {token_address} missing assets_per_share")

    await _check_solvency(
        token_address,
        underlying_address,
        block,
        assets_per_share,
        skip_cache,
    )

    underlying_price = await magic.get_price(
        underlying_address, block=block, skip_cache=skip_cache, sync=False
    )
    if underlying_price is None:
        raise PriceError(f"No underlying price for vbToken {token_address}")

    return UsdPrice(assets_per_share * Decimal(underlying_price))
