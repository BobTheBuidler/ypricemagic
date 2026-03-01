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

## Async Pattern

- All pricing functions use `a_sync` decorator for dual sync/async support
- `igather` used for parallel RPC calls
- `stuck_coro_debugger` decorator for long-running calls (must be preserved)
