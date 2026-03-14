# Architecture

Architectural decisions and patterns discovered during the mission.

**What belongs here:** Design decisions, code patterns, module responsibilities, type system notes.

---

## Price Resolution Flow

```
y.get_price(token, block)
  → y.prices.magic._get_price(token, block)
    → _get_price_from_api()        # external API (if configured)
    → _exit_early_for_known_tokens()  # protocol-specific (atoken, curve LP, yearn, etc.)
    → _get_price_from_dexes()      # DEX price resolution
      → UniswapMultiplexer.get_price()  # aggregates V1, V2 forks, V3
      → CurvePool pricing
      → BalancerMultiplexer (fallback)
```

## DEX Routing Architecture

### V3 (y/prices/dex/uniswap/v3.py)
- `UniswapV3.get_price()` generates encoded paths for the V3 Quoter contract
- Paths are tried in parallel via `igather`
- Returns `max(outputs)` across all paths
- **Key change area**: Path generation currently hardcodes USDC as terminal + WETH as only intermediary

### V2 (y/prices/dex/uniswap/v2.py)
- `UniswapRouterV2.get_price()` uses `getAmountsOut()` with multi-hop address paths
- `get_path_to_stables()` recursively builds paths by following the deepest pool
- Fallback: prices the paired token recursively via `magic.get_price()`
- **Key change area**: Only follows single deepest pool; needs to try multiple candidates

## Type System

- `UsdPrice(UsdValue(float))` — USD-denominated price
- `UsdValue(float)` — USD-denominated value with `$` string formatting
- New `Price(float)` type needed for non-USD denominated prices

## V2 Fee Correction for Spot Prices

When `get_price()` calls `getAmountsOut`, the router applies the Uniswap V2 fee (0.3%) per hop. The result is the net-of-fee execution price, not the spot price. To recover the spot price, the code divides out the fees:

```python
fees = Decimal(0.997) ** (len(path) - 1)
return UsdPrice(amount_out / fees / _amount)
```

This pattern is used in multiple places in `v2.py` for consistency. Future workers touching `get_price()` should NOT remove this division — the goal is to report spot/market prices, not net-of-fee execution prices.

## Deferred Imports for Circular Import Avoidance

`PriceResult` from `y.datatypes` is imported inside function bodies (deferred import) rather than at the top of files like `v2.py`. This is an established project pattern to avoid circular imports caused by `y.datatypes` → `y.prices.magic` → `y.prices.dex.uniswap.v2` import chain. Do not move these to the module-level imports.

## Token Detection Patterns

### `has_methods` — no-input methods only

`has_methods` (in `y/contracts.py`) only works correctly for public view methods with **no inputs**. When called with `all` as the aggregator and any input-bearing method, it always returns `False` (see `contracts.py:839`).

```python
# CORRECT — no-input view methods
has_methods(token, ('asset()(address)', 'previewRedeem(uint256)(uint256)'), all)

# BROKEN — getTwab requires inputs (address, uint32), has_methods always returns False
has_methods(token, ('getTwab(address,uint32)(uint224,uint32)', 'controller()(address)'), all)
```

**Alternative for input-bearing methods:** Use a companion no-input method from the same interface, or use `raw_call` with `return_None_on_failure=True` with representative arguments.

### Bucket evaluation order: string_matchers before calls_only

`check_bucket()` in `y/prices/utils/buckets.py` evaluates `string_matchers` (which includes `'one to one'` → `is_one_to_one_token`) **before** `calls_only`. Any address in `y/prices/one_to_one.py`'s `MAPPING` will always be returned as `'one to one'` — never as a `calls_only` bucket like `'curve gauge'` or `'erc4626 vault'`.

**Implication for tests:** Test addresses for `calls_only` bucket detection must NOT be hardcoded in `one_to_one.py`. Choose algorithmically-detectable-only addresses.

### ZERO_ADDRESS guard for raw_call address returns

When `raw_call` with `output='address'` returns a zero address, the return value is the string `'0x0000000000000000000000000000000000000000'` which is truthy. A simple `if not address` check does NOT catch it. Use:

```python
from y.constants import ZERO_ADDRESS
if not lp_token or lp_token == ZERO_ADDRESS:
    return None
```

This pattern is established in `curve_gauge.py:109` and should be followed consistently.

## Async Pattern

- All pricing functions use `a_sync` decorator for dual sync/async support
- `igather` used for parallel RPC calls
- `stuck_coro_debugger` decorator for long-running calls (must be preserved)
- **Both** `get_price_*` and `is_*` detection functions must use `@stuck_coro_debugger`, since detection functions also make multiple RPC calls that can stall. Pattern: `@a_sync.a_sync(...)` → `@stuck_coro_debugger` → `@optional_async_diskcache` (see `yearn.py:72-79`).

## a_sync: Methods vs Async Generators

**Critical distinction:** `@a_sync.a_sync`-decorated methods accept `sync=True`/`sync=False` keyword arguments. Plain async generator methods on `ASyncGenericBase` subclasses are wrapped by `ASyncGeneratorFunction` via the `ASyncMeta` metaclass — this wrapper does **NOT** support the `sync` keyword argument.

```python
# This works — @a_sync.a_sync method, supports sync kwarg
price = await self.get_price(token, block, sync=False)

# This raises TypeError — async generator, ASyncGeneratorFunction does NOT support sync kwarg
async for pool in self.top_pools(token, block, sync=False):  # WRONG
    ...
async for pool in self.top_pools(token, block):  # CORRECT
    ...
```

Always check whether a method is decorated with `@a_sync.a_sync` or is a plain `async def` generator before passing `sync=False`.
