# Trade Path Return Feature — User-Visible Behaviors Enumeration

## 1. Public API Functions & Expected Return Types

### 1.1 `get_price(token_address, block, ...)` → currently `UsdPrice | None`
**Location:** `y/prices/magic.py` (lines 77–130), exported from `y/__init__.py`

- **Current return:** `UsdPrice` (float subclass, `str()` → `$1234.56780000`) or `None` (when `fail_to_None=True`)
- **New return:** `PriceResult` with `.price: UsdPrice` and `.path: list[PriceStep]`, or `None`
- **Parameters (unchanged):** `token_address`, `block`, `fail_to_None`, `skip_cache`, `ignore_pools`, `silent`, `amount`
- **Calling conventions:** sync (default) and async (`sync=False`)
- **Overloads:** 2 overloads for `fail_to_None=True` vs `bool` controlling None return

**Assertions needed:**
- `result.price` is `UsdPrice` (float subclass, `str()` starts with `$`)
- `result.path` is `list[PriceStep]`
- `len(result.path) >= 1` for any successful price
- When `fail_to_None=True` and token is un-priceable: returns `None`
- When `fail_to_None=False` and token is un-priceable: raises `yPriceMagicError`
- `float(result)` backward compat TBD — if `PriceResult` is NOT a float subclass, all callers doing `float(price)` or arithmetic break
- sync mode works, async mode works

### 1.2 `get_price_in(token_address, quote_token, block, ...)` → currently `Price | None`
**Location:** `y/prices/magic.py` (lines 170–285)

- **Current return:** `Price` (float subclass, no `$` prefix) or `None`
- **New return:** Should include path showing cross-rate resolution steps
- **Parameters:** `token_address`, `quote_token`, `block`, `fail_to_None`, `skip_cache`, `ignore_pools`, `silent`, `amount`

**Assertions needed:**
- Same-token case (`token == quote_token`): returns `Price(1.0)` with empty or identity path
- Stablecoin quote path: path shows `[token→USD, quote_token→USD]` (two `get_price` calls)
- On-chain routing path (V3/V2): path shows DEX hop(s) with pool addresses
- Cross-rate fallback path: path shows `[token→USD step(s), quote_token→USD step(s)]`
- When `fail_to_None=True`: returns `None` on failure
- When `fail_to_None=False`: raises exception on failure

### 1.3 `get_prices(token_addresses, block, ...)` → currently `list[UsdPrice | None]`
**Location:** `y/prices/magic.py` (lines 406–462)

- **Current return:** `list[UsdPrice | None]`
- **New return:** `list[PriceResult | None]`
- **Parameters:** `token_addresses`, `block`, `fail_to_None`, `skip_cache`, `silent`, `amounts`

**Assertions needed:**
- Length of returned list equals length of input list
- Each element is `PriceResult` or `None`
- Order matches input order
- Each element's `.path` is populated
- Delegates to `get_price()` per token (or `map_prices`)

### 1.4 `map_prices(token_addresses, block, ...)` → `a_sync.TaskMapping`
**Location:** `y/prices/magic.py` (lines 496–536)

- **Current return:** `a_sync.TaskMapping[_TAddress, UsdPrice | None]`
- **New return:** `a_sync.TaskMapping[_TAddress, PriceResult | None]`

**Assertions needed:**
- `.values(pop=True)` returns list of `PriceResult | None`
- Keys map correctly to addresses
- Async iteration works

### 1.5 `ERC20.price(block, ...)` → currently `UsdPrice | None`
**Location:** `y/classes/common.py` (lines 410–443)

- Delegates to `magic.get_price(self.address, ...)`
- **New return:** `PriceResult | None`

**Assertions needed:**
- `token.price()` returns same type as `get_price(token.address)`
- path[0] input_token matches `token.address`

### 1.6 `WeiBalance.price` property → currently `Decimal`
**Location:** `y/classes/common.py` (lines ~555–570)

- Calls `self.token.price(...)` then wraps in `Decimal(...)`
- **Impact:** `Decimal(PriceResult)` will fail if `PriceResult` is not numeric — MUST extract `.price` first

**Assertions needed:**
- `WeiBalance.price` returns `Decimal` (extracted from `PriceResult.price`)
- `WeiBalance.value_usd` still works (uses `price * readable`)

---

## 2. Resolution Strategies & Expected Path Shapes

### 2.1 API Source (`_get_price_from_api`)
- Checked first; if ypriceapi is enabled and token is not skipped
- **Path shape:** `[PriceStep(source="ypriceapi", input=token, output="USD")]` — single step, no pool

### 2.2 Known-Token Buckets (`_exit_early_for_known_tokens`)
All 35+ bucket types. Each bucket resolves differently:

| Bucket | Path Shape | Pool? |
|--------|-----------|-------|
| `stable usd` | `[PriceStep(source="stable_usd", input=token, output="USD", price=1)]` — hardcoded price=1 | No |
| `wrapped gas coin` | `[PriceStep(source="wrapped_gas_coin", input=token, output=WETH), ...WETH_path]` — recursive | No |
| `chainlink feed` | `[PriceStep(source="chainlink", input=token, output="USD")]` | No (oracle) |
| `chainlink and band` | `[PriceStep(source="chainlink", ...)]` or `[PriceStep(source="band", ...)]` | No |
| `atoken` | `[PriceStep(source="aave", input=aToken, output=underlying), ...underlying_path]` | No |
| `wrapped atoken v2` | `[PriceStep(source="aave_wrapped_v2", input=token, output=underlying), ...underlying_path]` | No |
| `wrapped atoken v3` | `[PriceStep(source="aave_wrapped_v3", input=token, output=underlying), ...underlying_path]` | No |
| `compound` | `[PriceStep(source="compound", input=cToken, output=underlying), ...underlying_path]` | No |
| `curve lp` | `[PriceStep(source="curve", input=token, output="USD", pool=curve_pool)]` | Yes |
| `balancer pool` | `[PriceStep(source="balancer", input=token, output="USD", pool=balancer_pool)]` | Yes |
| `uni or uni-like lp` | `[PriceStep(source="uniswap_v2_lp", input=token, output="USD", pool=pool_addr)]` | Yes |
| `yearn or yearn-like` | `[PriceStep(source="yearn", input=vault, output=underlying), ...underlying_path]` | No |
| `convex` | `[PriceStep(source="convex", input=token, output=mapped_token), ...mapped_token_path]` | No |
| `one to one` | `[PriceStep(source="one_to_one", input=token, output=mapped_token), ...mapped_token_path]` | No |
| `synthetix` | `[PriceStep(source="synthetix", input=synth, output="USD")]` | No (oracle) |
| `wsteth` | `[PriceStep(source="wsteth", input=wsteth, output=stETH), PriceStep(source=..., input=stETH→WETH→USD)]` | No |
| `creth` | `[PriceStep(source="creth", input=creth, output=WETH), ...WETH_path]` | No |
| `rkp3r` | `[PriceStep(source="rkp3r", input=rkp3r, output=KP3R, discount=...), ...KP3R_path]` | No |
| `popsicle` | `[PriceStep(source="popsicle", input=token, output="USD", pool=...)]` | Yes |
| `gelato` | `[PriceStep(source="gelato", input=token, output="USD", pool=...)]` | Yes |
| `gearbox` | `[PriceStep(source="gearbox", input=diesel_token, output=underlying), ...underlying_path]` | No |
| `pendle lp` | `[PriceStep(source="pendle", input=token, output="USD")]` | Yes |
| `ib token` | `[PriceStep(source="ib", input=ibToken, output=underlying), ...underlying_path]` | No |
| `solidex` | `[PriceStep(source="solidex", input=token, output=pool), ...pool_path]` | No → Yes |
| `token set` | `[PriceStep(source="tokensets", input=token, output="USD")]` | No |
| `basketdao` | `[PriceStep(source="basketdao", input=token, output="USD")]` | No |
| `piedao lp` | `[PriceStep(source="piedao", input=token, output="USD")]` | No |
| `reserve` | `[PriceStep(source="reserve", input=token, output="USD")]` | Yes |
| `belt lp` | `[PriceStep(source="belt", input=token, output="USD")]` | Yes |
| `ellipsis lp` | `[PriceStep(source="ellipsis", input=token, output="USD")]` | Yes |
| `froyo` | `[PriceStep(source="froyo", input=token, output="USD")]` | Yes |
| `saddle` | `[PriceStep(source="saddle", input=token, output="USD")]` | Yes |
| `stargate lp` | `[PriceStep(source="stargate", input=token, output="USD")]` | Yes |
| `mstable feeder pool` | `[PriceStep(source="mstable", input=token, output=masset), ...masset_path]` | No |
| `mooniswap lp` | `[PriceStep(source="mooniswap", input=token, output="USD", pool=...)]` | Yes |
| `generic amm` | `[PriceStep(source="generic_amm", input=token, output="USD", pool=...)]` | Yes |

### 2.3 DEX Fallback (`_get_price_from_dexes`)
- Tried after known tokens fail
- **Flow:** Check liquidity across `uniswap_multiplexer` and `curve`, sort by depth, try each
- **Path shape:** `[PriceStep(source="uniswap_v2"/"uniswap_v3"/"curve"/"balancer", input=token, output=intermediate?, output=USD, pool=pool_addr)]`
- Multi-hop possible (e.g., token→WETH→USDC via V3)
- Final fallback: `balancer_multiplexer.get_price()` tried as last resort

### 2.4 Recursive Resolution
Many buckets delegate back to `magic.get_price()`:
- `one_to_one.get_price()` → calls `magic.get_price(mapped_token)`
- `convex.get_price()` → calls `magic.get_price(MAPPING[token])`
- `ib.get_price()` → calls `magic.get_price(underlying_token)` and multiplies by exchange rate
- `creth.get_price_creth()` → calls `magic.get_price(weth)`
- `wsteth.get_price()` → calls `magic.get_price(weth)` and multiplies by stETH/ETH ratio
- `solidex.get_price()` → calls `magic.get_price(pool_address)`
- `mstablefeederpool.get_price()` → calls `magic.get_price(masset)`
- `mooniswap.get_pool_price()` → calls `magic.get_price(token0)`, `magic.get_price(token1)`
- `rkp3r.get_price()` → calls `magic.get_price(KP3R)` and applies discount
- `v2.UniswapV2Pool.get_price()` → calls `magic.get_price(paired_with)` in fallback path
- `balancer/v1.get_price()` → calls `magic.get_price(...)` for each pool token
- `gelato.get_price()` → calls `magic.get_price(token0)`, `magic.get_price(token1)`
- `saddle.get_price()` → calls `magic.get_prices(tokens, ...)`

**Path assertion:** Recursive calls should concatenate their inner path, producing a multi-step path.

---

## 3. Edge Cases

### 3.1 Zero Address (`ZERO_ADDRESS`)
- **Current:** `_get_price` returns `None` immediately (line 600–603 in magic.py)
- **New:** Should return `None`, no path
- **Assertion:** `get_price(ZERO_ADDRESS) is None` (with `fail_to_None=True`), raises without it

### 3.2 Unknown/Un-priceable Token
- **Current:** `_fail_appropriately()` called → raises `PriceError` or returns `None`
- **New:** Same, no path if None
- **Assertion:** `result is None` or exception raised

### 3.3 Stablecoin (in STABLECOINS set)
- **Current:** `bucket == "stable usd"` → `price = 1` (hardcoded integer, NOT `UsdPrice(1)`)
- **New:** Path = single step `[PriceStep(source="stable_usd", ...)]`, price = 1
- **CRITICAL NOTE:** Currently returns bare `int(1)`, not `UsdPrice(1)`. This means `isinstance(price, UsdPrice)` is `False` for stablecoins! This is a known bug/quirk. The PriceResult wrapper should normalize this.

### 3.4 Wrapped Gas Coin / EEE_ADDRESS
- **Current:** `bucket == "wrapped gas coin"` → recursively calls `get_price(WRAPPED_GAS_COIN)` (which goes through DEX/chainlink)
- **New:** Path = `[PriceStep(source="wrapped_gas_coin", ...), ...inner_path]`
- **Assertion:** Path has ≥2 steps (wrap + underlying resolution)

### 3.5 Non-Standard ERC20 (no symbol/name/decimals)
- **Current:** `NonStandardERC20` caught, symbol set to `None`, proceeds to price lookup
- **New:** Path should still be populated if price is found
- **Assertion:** Path is valid even when symbol is None

### 3.6 Amount Parameter (Price Impact)
- **Current:** `amount` only affects DEX sources; DB cache skipped when `amount is not None`
- **New:** Path should annotate when amount/price-impact was used
- **Assertion:** Same path structure, but DB not written/read when `amount` provided

### 3.7 DB Cache Hit
- **Current:** `__cache` decorator checks DB first; if hit, returns `UsdPrice(cached_decimal)`
- **New:** When cache hit, path = `[PriceStep(source="db_cache", ...)]` (or path not available from cache)
- **CRITICAL DECISION:** DB stores only the float price, not the path. Options:
  1. Return price without path on cache hit (path=None or empty)
  2. Store path in DB too (schema change)
  3. Always return path (skip_cache to get path, or re-resolve)
- **Assertion:** When `skip_cache=False` and price is in DB, behavior is defined

### 3.8 Memory Cache Hit (a_sync ram_cache)
- **Current:** `_get_price` has `@a_sync.a_sync(cache_type="memory", ...)` → returns cached result
- **New:** If memory cache stores `PriceResult`, subsequent calls return full path
- **Assertion:** Same `PriceResult` returned from memory cache as from fresh resolution

### 3.9 Sense Check
- **Current:** After price resolved, `utils.sense_check(token, block, price)` validates price magnitude
- **New:** sense_check receives `PriceResult.price` (just the float), no change needed
- **Assertion:** sense_check still works with extracted float

### 3.10 `price = 0` or falsy
- **Current:** Multiple `if price:` checks in `_get_price` that filter out 0 and falsy values
- **New:** Must check `result.price` truthiness, not `result` (PriceResult is always truthy as an object)
- **CRITICAL:** All `if price:` checks must become `if result and result.price:` or equivalent

---

## 4. Integration Points That Must Change

### 4.1 DB Cache Layer (`y/_db/utils/price.py`)
- `get_price()` returns `Decimal | None` — unchanged (just the price)
- `set_price()` takes `Decimal` — unchanged (just stores price)
- **Decision needed:** Store path in DB or not?
- If path stored: new DB entity needed, schema migration
- If not: cache hit has no path info

### 4.2 `__cache` Decorator (magic.py, lines 546–575)
- Currently reads/writes just the price float
- Must extract `.price` from `PriceResult` for DB storage
- Must reconstruct `PriceResult` (without path) on cache hit, or handle None path

### 4.3 `ERC20.price()` (common.py, line 434)
- `from y.prices.magic import get_price` → calls → returns result
- All callers of `ERC20.price()` must handle `PriceResult` instead of `UsdPrice`

### 4.4 `WeiBalance.price` property (common.py, line ~560)
- `Decimal(await self.token.price(...))` — will break if PriceResult not numeric
- Must become `Decimal(result.price)` or PriceResult must support `__float__`

### 4.5 `WeiBalance.value_usd` property
- Uses `balance * price` — same issue, must use `.price`

### 4.6 Internal Callers in Sub-Modules (~15 modules)
Every module that calls `magic.get_price()` and uses the result arithmetically must handle `PriceResult`:

| Module | Usage Pattern | Change Needed |
|--------|--------------|---------------|
| `one_to_one.py:70` | `return await magic.get_price(...)` | Return value wrapping |
| `convex.py:63` | `return await magic.get_price(...)` | Return value wrapping |
| `rkp3r.py:74` | `magic.get_price(KP3R) * discount` | Extract `.price` for arithmetic |
| `ib.py:89` | `token_price = await magic.get_price(...)` then arithmetic | Extract `.price` |
| `creth.py:65` | `magic.get_price(weth)` then arithmetic | Extract `.price` |
| `wsteth.py:90` | `magic.get_price(weth)` then arithmetic | Extract `.price` |
| `solidex.py:77` | `return await magic.get_price(pool)` | Return value wrapping |
| `mstablefeederpool.py:78` | `underlying_price = await magic.get_price(...)` then arithmetic | Extract `.price` |
| `mooniswap.py:109-116` | Two `magic.get_price()` calls, then arithmetic | Extract `.price` |
| `saddle.py:149` | `magic.get_prices(tokens, ...)` then arithmetic | Extract `.price` per element |
| `v2.py:594` | `magic.get_price(paired_with)` then arithmetic | Extract `.price` |
| `v1.py` (balancer) | `magic.get_price(...)` then arithmetic | Extract `.price` |
| `gelato.py:86-87` | Two `magic.get_price()` calls, then arithmetic | Extract `.price` |
| `ERC20.price()` | Returns result directly | Return type changes |
| `WeiBalance.price` | `Decimal(await self.token.price())` | Must extract `.price` |

### 4.7 `y/__init__.py` Exports
- Currently exports: `get_price`, `get_price_in`, `get_prices`, `map_prices`, `Price`
- Must also export: `PriceResult`, `PriceStep`
- `__all__` list must be updated

### 4.8 Test Files
All test files that assert on return types must update:
- `tests/prices/test_magic.py` — `checked_together[i] == checked_separately[i]` comparison
- `tests/prices/test_get_price_in.py` — `isinstance(result, UsdPrice)` checks
- `tests/prices/test_quote_token_routing.py` — if exists, type checks
- All bucket tests indirectly test price resolution

---

## 5. `PriceStep` Data Model Requirements

Based on the analysis, `PriceStep` should capture:

```python
@dataclass
class PriceStep:
    source: str        # e.g. "chainlink", "uniswap_v3", "aave", "stable_usd", "db_cache", "ypriceapi"
    input_token: str   # ChecksumAddress of input token
    output_token: str  # ChecksumAddress of output token, or "USD" for terminal steps
    pool: str | None   # Pool/contract address if applicable (DEX pools, curve, balancer)
    price: float       # The price/rate at this step

@dataclass
class PriceResult:
    price: UsdPrice    # The final USD price (or Price for get_price_in)
    path: list[PriceStep]  # The resolution path
```

### PriceResult Design Decisions:
1. **Should PriceResult be a float subclass?** If yes, backward compat is easier (arithmetic works). If no, all callers must change.
2. **Should path be optional?** For DB cache hits where path isn't stored.
3. **Should PriceResult support `__float__`?** For `Decimal(result)` calls.

---

## 6. Summary of All Behaviors to Assert

### API Contract Assertions:
1. `get_price(token, block)` returns `PriceResult` with `.price: UsdPrice` and `.path: list[PriceStep]`
2. `get_price(token, block, fail_to_None=True)` returns `PriceResult | None`
3. `get_price(ZERO_ADDRESS, fail_to_None=True)` returns `None`
4. `get_price(unknown_token, fail_to_None=False)` raises `yPriceMagicError`
5. `get_price_in(token, quote, block)` returns `PriceResult` with `.price: Price` and composite path
6. `get_price_in(token, token, block)` returns result with `Price(1.0)` and empty/identity path
7. `get_prices([...], block)` returns `list[PriceResult | None]` of same length
8. `map_prices([...], block)` TaskMapping yields `PriceResult | None` values
9. `ERC20(addr).price(block)` returns same as `get_price(addr, block)`
10. `WeiBalance.price` returns `Decimal` (extracts from PriceResult)
11. `WeiBalance.value_usd` returns `Decimal` (correct arithmetic)

### Path Structure Assertions:
12. Stablecoin → path has 1 step, source="stable_usd"
13. Chainlink token → path has 1 step, source="chainlink"
14. aToken → path has ≥2 steps: aave unwrap + underlying resolution
15. Compound cToken → path has ≥2 steps: compound unwrap + underlying resolution
16. Uniswap V2 LP → path has 1 step with pool address, source="uniswap_v2_lp"
17. Curve LP → path has 1 step with pool address, source="curve"
18. DEX fallback (non-LP token) → path shows DEX source with pool address
19. Wrapped gas coin → path has ≥2 steps: wrap + WETH resolution
20. Recursive buckets (convex, one_to_one, solidex, etc.) → path concatenates inner resolution
21. ypriceapi → path has 1 step, source="ypriceapi"
22. DB cache hit → path is empty/None or has 1 step source="db_cache"
23. Memory cache hit → path preserved from original resolution

### Arithmetic/Interop Assertions:
24. `float(result)` works (for backward compat)
25. `result * 2` works or callers extract `.price` first
26. `Decimal(result)` works (WeiBalance compat)
27. `result > 0` / `if result:` truthiness is correct
28. `result == other_result` comparison works
29. DB `set_price(token, block, result.price)` works (Decimal conversion)

### Edge Case Assertions:
30. `amount=1000` → price accounts for impact, path still populated, DB NOT written
31. `skip_cache=True` → DB bypassed, path from fresh resolution
32. `ignore_pools=(pool,)` → excluded pool not in path
33. Stablecoin returns `PriceResult` not bare `int(1)` (normalize the current quirk)
34. `silent=True` suppresses warnings but path still populated
35. Non-standard ERC20 (no symbol) → price and path still work
