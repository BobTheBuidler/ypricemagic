from decimal import Decimal
from logging import getLogger

import dank_mids
from a_sync import a_sync, cgather
from async_lru import alru_cache
from web3.exceptions import ContractLogicError

from y import ENVIRONMENT_VARIABLES as ENVS
from y._decorators import stuck_coro_debugger
from y.classes.common import ERC20
from y.contracts import Contract, has_method, is_contract
from y.datatypes import Address, Block
from y.exceptions import ContractNotVerified
from y.utils.cache import a_sync_ttl_cache

logger = getLogger(__name__)

# Docs + deployments references:
# - Oracle integration: https://docs.pendle.finance/pendle-v2/Developers/Oracles/HowToIntegratePtAndLpOracle
# - Mainnet deployments: https://raw.githubusercontent.com/pendle-finance/pendle-core-v2-public/main/deployments/1-core.json
PENDLE_ORACLE_DOCS = (
    "https://docs.pendle.finance/pendle-v2/Developers/Oracles/HowToIntegratePtAndLpOracle"
)
PENDLE_DEPLOYMENTS = (
    "https://raw.githubusercontent.com/pendle-finance/pendle-core-v2-public/main/deployments/1-core.json"
)

# Canonical oracle address comes from Pendle docs. Deployments list pyYtLpOracle;
# keep it for optional probing, but do not use it as the default oracle.
PENDLE_ORACLE_ADDRESS = "0x9a9Fa8338dd5E5B2188006f1Cd2Ef26d921650C2"
PENDLE_PY_YT_LP_ORACLE_ADDRESS = "0x5542be50420E88dd7D5B4a3D488FA6ED82F6DAc2"

# Mainnet factory addresses sourced from Pendle deployments.
PENDLE_MARKET_FACTORY_ADDRESSES = (
    "0x27b1dAcd74688aF24a64BD3C9C1B143118740784",
    "0x1A6fCc85557BC4fB7B534ed835a03EF056552D52",
    "0x3d75Bd20C983edb5fD218A1b7e0024F1056c7A2F",
    "0x6fcf753f2C67b83f7B09746Bbc4FA0047b35D050",
    "0x6d247b1c044fA1E22e6B04fA9F71Baf99EB29A9f",
)
PENDLE_YIELD_CONTRACT_FACTORY_ADDRESSES = (
    "0x70ee0A6DB4F5a2Dc4d9c0b57bE97B9987e75BAFD",
    "0xdF3601014686674e53d1Fa52F7602525483F9122",
    "0x273b4bFA3Bb30fe8F32c467b5f0046834557F072",
    "0x35A338522a435D46f77Be32C70E215B813D0e3aC",
    "0x3E6EBa46AbC5ab18ED95F6667d8B2fd4020E4637",
)
PENDLE_SY_FACTORY_ADDRESSES = ("0x466CeD3b33045Ea986B2f306C8D0aA8067961CF8",)

PENDLE_MARKET_EVENT_NAMES = ("CreateNewMarket", "MarketCreated")

try:
    PENDLE_ORACLE = (
        Contract(PENDLE_ORACLE_ADDRESS) if is_contract(PENDLE_ORACLE_ADDRESS) else None
    )
except ContractNotVerified:
    PENDLE_ORACLE = None

# Pendle docs recommend a 900s TWAP duration.
TWAP_DURATION_SECONDS = 900


def _event_value(event, *keys: str) -> Address | None:
    for key in keys:
        try:
            return event[key]
        except Exception:
            continue
    return None


def _market_event_name(factory: Contract) -> str | None:
    for name in PENDLE_MARKET_EVENT_NAMES:
        if name in factory.topics:
            return name
    return None


@a_sync_ttl_cache
async def _pendle_markets_by_address() -> dict[str, str]:
    return await _load_pendle_markets_by_address()


@stuck_coro_debugger
async def _load_pendle_markets_by_address() -> dict[str, str]:
    markets: dict[str, str] = {}
    to_block = await dank_mids.eth.block_number
    for factory_address in PENDLE_MARKET_FACTORY_ADDRESSES:
        try:
            factory = await Contract.coroutine(factory_address)
        except ContractNotVerified:
            logger.debug(
                "Pendle market factory %s is not verified; skipping event scan",
                factory_address,
            )
            continue

        event_name = _market_event_name(factory)
        if not event_name:
            logger.debug(
                "Pendle market factory %s missing expected market event; skipping",
                factory_address,
            )
            continue

        events = getattr(factory.events, event_name)
        async for event in events.events(to_block=to_block):
            market = _event_value(event, "market", "Market")
            pt = _event_value(event, "PT", "pt", "principalToken")
            if market and pt:
                markets[str(market)] = str(pt)

    return markets


async def _pendle_market_pt(market: Address) -> Address | None:
    markets = await _pendle_markets_by_address()
    return markets.get(str(market))


async def _call_address_method(contract: Contract, *names: str) -> Address | None:
    for name in names:
        method = getattr(contract, name, None)
        if method is None:
            continue
        try:
            return await method.coroutine()
        except ContractLogicError:
            continue
    return None


@stuck_coro_debugger
async def _tokens_from_registry(lp_token: Address) -> tuple[Address, Address, Address] | None:
    pt = await _pendle_market_pt(lp_token)
    if not pt:
        return None

    try:
        pt_contract = await Contract.coroutine(pt)
    except ContractNotVerified:
        return None

    sy, yt = await cgather(
        _call_address_method(pt_contract, "SY", "sy"),
        _call_address_method(pt_contract, "YT", "yt"),
    )
    if sy and yt:
        return sy, pt, yt
    return None


@stuck_coro_debugger
async def _is_pendle_market(token: Address) -> bool:
    markets = await _pendle_markets_by_address()
    return str(token) in markets


@a_sync("sync")
async def is_pendle_lp(token: Address) -> bool:
    return await _is_pendle_lp(token)


@stuck_coro_debugger
async def _is_pendle_lp(token: Address) -> bool:
    # idk why this token is giving a false positive, but it is, at least sometimes
    if token == "0x00e8Eb340f8AF587EEA6200D2081E31dC87285ac":
        return False
    if await _is_pendle_market(token):
        return True
    return await has_method(token, "readTokens()(address,address,address)", sync=False)


@alru_cache(maxsize=None)
async def get_tokens(lp_token: Address) -> tuple[str, str, str]:
    return await _get_tokens(lp_token)


@stuck_coro_debugger
async def _get_tokens(lp_token: Address) -> tuple[str, str, str]:
    """
    Retrieves the addresses of the tokens in a Pendle LP token.

    This function is cached to improve performance for repeated calls.

    Args:
        lp_token: The address of the Pendle LP token.

    Returns:
        A tuple containing the addresses of the SY token, PT token, and YT token.

    Example:
        >>> tokens = await get_tokens("0x1b92b5242301ce4a8c73cc3ef0d6dee33a3a5b23")
        >>> print(tokens)
        ('0x...', '0x...', '0x...')  # Addresses of SY, PT, and YT tokens

    Note:
        The function returns the result of the `readTokens` method from the Pendle LP
        contract, with a registry-based fallback using factory events.

    See Also:
        - :func:`is_pendle_lp` for checking if a token is a Pendle LP token.
    """
    try:
        lp_contract = await Contract.coroutine(lp_token)
    except ContractNotVerified as exc:
        fallback = await _tokens_from_registry(str(lp_token))
        if fallback:
            return fallback
        raise exc
    try:
        return await lp_contract.readTokens
    except ContractLogicError as exc:
        fallback = await _tokens_from_registry(lp_contract.address)
        if fallback:
            return fallback
        raise exc


@stuck_coro_debugger
async def _oracle_lp_rate(
    token: Address, block: Block | None
) -> tuple[str, int] | None:
    if PENDLE_ORACLE is None:
        return None

    oracle = PENDLE_ORACLE
    for method_name, kind in (
        ("getLpToSyRate", "sy"),
        ("getLpToAssetRate", "asset"),
    ):
        method = getattr(oracle, method_name, None)
        if method is None:
            continue
        try:
            rate = await method.coroutine(
                token, TWAP_DURATION_SECONDS, block_identifier=block
            )
        except ContractLogicError:
            continue
        return kind, rate
    return None


@a_sync("sync")
async def get_lp_price(
    token: Address, block: Block = None, skip_cache: bool = ENVS.SKIP_CACHE
) -> Decimal | None:
    return await _get_lp_price(token, block=block, skip_cache=skip_cache)


@stuck_coro_debugger
async def _get_lp_price(
    token: Address, block: Block = None, skip_cache: bool = ENVS.SKIP_CACHE
) -> Decimal | None:
    """
    Calculates the price of a Pendle LP token.

    Args:
        token: The address of the Pendle LP token.
        block (optional): The block number to query. Defaults to the latest block.
        skip_cache (optional): Whether to skip the cache when fetching prices. Defaults to
            :obj:`ENVS.SKIP_CACHE`.

    Returns:
        The price of the LP token in USD.

    Example:
        >>> price = get_lp_price("0x1b92b5242301ce4a8c73cc3ef0d6dee33a3a5b23", block=14_000_000)
        >>> print(f"{price:.6f}")
        1.234567  # The price of the Pendle LP token in USD

    Note:
        This function retrieves the LP to SY rate using the Pendle oracle and multiplies
        it by the underlying asset price. If SY-rate calls are unavailable or revert, it
        falls back to the asset-rate variant.

    See Also:
        - :func:`get_tokens` for retrieving the tokens in a Pendle LP token.
    """
    if PENDLE_ORACLE is None:
        return None

    try:
        sy_token, _, _ = await get_tokens(str(token))  # force to string for cache key
    except ContractLogicError:
        return None

    try:
        sy = await Contract.coroutine(sy_token)
    except ContractNotVerified:
        return None
    try:
        _asset_type, asset, decimals = await sy.assetInfo
    except ContractLogicError:
        return None

    oracle_rate = await _oracle_lp_rate(token, block)
    if oracle_rate is None:
        return None

    kind, rate = oracle_rate
    rate_decimal = Decimal(rate)
    if kind == "asset":
        rate_decimal /= Decimal(10**decimals)
    else:
        rate_decimal /= Decimal(10**18)

    asset_price = await ERC20(asset, asynchronous=True).price(
        block=block,
        skip_cache=skip_cache,
        return_None_on_failure=True,
    )
    if asset_price is None:
        return None
    return rate_decimal * Decimal(asset_price)
