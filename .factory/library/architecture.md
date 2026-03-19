# Architecture

**What belongs here:** Architectural decisions, pricing pipeline patterns, code organization.

---

## Pricing Pipeline

`get_price(token, block)` flow:
1. Zero address check -> None
2. ypriceAPI external lookup (if configured)
3. `check_bucket(token)` -> classify token into one of 36 bucket types
4. `_exit_early_for_known_tokens` -> dispatch to bucket-specific pricing function
5. DEX fallback: check liquidity on Uniswap + Curve, try deepest first, Balancer last resort
6. `sense_check` on result

## Key Modules

- `y/prices/magic.py` - main entry point, orchestrates pricing
- `y/prices/utils/buckets.py` - token classification (3 tiers: string match, calls-only, sequential)
- `y/datatypes.py` - core types (UsdPrice, AnyAddressType, Block, PriceResult, PriceStep)
- `y/classes/common.py` - ERC20 class with cached properties
- `y/contracts.py` - contract interaction utilities
- `y/utils/cache.py` - caching decorators (optional_async_diskcache)
- `y/utils/raw_calls.py` - raw contract call utilities

## Conventions

- `@stuck_coro_debugger` on all async RPC/pricing functions
- `@a_sync.a_sync(default="sync")` for dual sync/async support
- `@optional_async_diskcache` for detection functions
- Address normalization via `convert.to_address_async()`
- `has_methods()` for detecting contract interfaces without ABI — NOTE: calls each method via multicall with NO arguments; methods that require inputs (e.g., `previewRedeem(uint256)`) may silently fail. Use only no-input view methods for detection (e.g., `asset()`, `totalAssets()`).
