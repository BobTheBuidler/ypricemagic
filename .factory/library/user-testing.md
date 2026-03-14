# User Testing

Testing surface, resource cost classification, and validation notes.

---

## Validation Surface

**Primary surface:** curl against ypricemagic-server API at `http://localhost:8000`
- Endpoint: `GET /{chain}/price?token={address}&block={block}&amount={amount}`
- Response: `{"token": "...", "price": float, "block": int, "trade_path": [...]}`
- Timeout: 120s per request is conservative; most respond in <30s

**Secondary surface:** agent-browser for Svelte frontend at `http://localhost:8000/`
- Token dropdown/autocomplete
- "Get Price" button
- Price result display

**Test tokens (Ethereum mainnet):**
- USDC: `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48`
- USDT: `0xdAC17F958D2ee523a2206206994597C13D831ec7`
- DAI: `0x6B175474E89094C44Da98b954EedeAC495271d0F`
- MIC: `0x368B3a58B5f49392e5C9E4C998cb0bB966752E51` (use block 12500000)
- Native ETH: `0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE`

## Validation Concurrency

**curl surface:** Lightweight, no resource concerns. Max concurrent: **5**.
- Each curl is a single HTTP request, no local compute
- The server handles concurrency internally

**agent-browser surface:** Each instance ~300MB RAM for browser + page.
- Machine has adequate resources for 3 concurrent instances
- Max concurrent: **3**

## Flow Validator Guidance: curl-api

Testing surface: curl against `http://localhost:8000` API.

**Isolation rules:**
- All requests are read-only GET queries — no shared mutable state
- Multiple validators can run fully concurrently without conflict
- Each request is stateless; no session, no cookies needed

**Boundaries:**
- Only test on `http://localhost:8000/{chain}/price?token={address}&block={block}&amount={amount}`
- Default chain is `ethereum` (prefix: `/ethereum/price`)
- Use `--max-time 120` for all curl calls to prevent indefinite hangs
- Use actual block numbers for historical queries (e.g., block 12500000 for MIC)
- Do NOT modify server code or cache

**Response format:**
```json
{"token": "0x...", "price": 1.0, "block": 12345, "chain": "ethereum", "block_timestamp": 123, "cached": false, "trade_path": [{"source": "stable usd", "input_token": "0x...", "output_token": "USD", "pool": null, "price": 1.0}]}
```

**Important:** The server may need time to warm up for first requests on a newly rebuilt container. If a request times out on first try, retry once before marking as fail.

## Cache Invalidation Notes

When the stablecoin pricing fix is deployed (switching from hardcoded $1 to real pricing), two caches hold stale data that must be cleared:

1. **ypricemagic bucket cache** (`/root/.ypricemagic/ypricemagic.sqlite`, `Address` table, `bucket` column):
   - USDT, DAI and other non-USDC stablecoins get `bucket = 'stable usd'` from the old code
   - Must clear: `UPDATE Address SET bucket = NULL WHERE bucket = 'stable usd' AND address != '<USDC_ADDRESS>'`
   - The Docker named volume `ypricemagic-ethereum` persists this across rebuilds

2. **ypricemagic price cache** (`/root/.ypricemagic/ypricemagic.sqlite`, `Price` table):
   - Old prices for USDT/DAI cached as 1.0
   - Must clear: `DELETE FROM Price WHERE token_address = '<USDT_OR_DAI>'`

3. **Server diskcache** (`/data/cache` volume):
   - Server-level cache also stores stale $1.00 values
   - Clear with diskcache Python API

After clearing all three, restart the container to flush in-memory caches.

**Script to clear stale stablecoin caches:**
```python
import sqlite3, diskcache

# Clear bucket cache
conn = sqlite3.connect('/root/.ypricemagic/ypricemagic.sqlite')
USDC = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'
conn.execute("UPDATE Address SET bucket = NULL WHERE bucket = 'stable usd' AND address != ?", (USDC,))
conn.execute("DELETE FROM Price WHERE token_address IN ('0xdAC17F958D2ee523a2206206994597C13D831ec7', '0x6B175474E89094C44Da98b954EedeAC495271d0F')")
conn.commit()

# Clear server diskcache
cache = diskcache.Cache('/data/cache')
for stablecoin in ['0xdac17f958d2ee523a2206206994597c13d831ec7', '0x6b175474e89094c44da98b954eedeac495271d0f']:
    for k in [k for k in cache.iterkeys() if stablecoin in str(k).lower()]:
        del cache[k]
```

## Exotic Token Addresses (Confirmed Working)

- **stkAAVE**: `0x4da27a545c0c5B758a6BA100e3a049001de870f5` → maps 1:1 to AAVE ($110)
- **plDAI V3**: `0x49d716DFe60b37379010A75329ae09428f17118d` → maps 1:1 to DAI (~$1)
- **plUSDC V3**: `0xBD87447F48ad729C5c4b8bcb503e1395F62e8B98` → maps 1:1 to USDC (~$1)
- **sDAI (ERC4626)**: `0x83F20F44975D03b1b09e64809B757c47f942BEeA` → priced at ~$1.17
- **weETH (ERC4626)**: `0xCd5fE23C85820F7B72D0926FC9b05b43E359b7ee` → priced at ~$2264
- **aDAI V1**: `0xfC1E690f61EFd961294b3e1Ce3313fBD8aa4f85d` → priced at ~$1 (V1 underlyingAssetAddress())

## Exotic Token Addresses (Problems Found)

- **pSLP-WBTC-ETH**: `0x55282dA27a3a02eFe599f9bD85E2e0C78f9cD2b2` → NonStandardERC20 (symbol() fails)
- **ptUSDC V4**: `0xdd4d117723C257CEe402285D3aCF218E9A8236E1` → consistently times out (600+ seconds cold start)
- **vxPREMIA**: `0xF1bB87563A122211d40d393eBf1c633c330377F9` → symbol='vxPREMIA' (different from xPREMIA)
- **xPREMIA staking**: `0x16f9D564Df80376C61AC914205D3fDfB8a32f98b` → NonStandardERC20 (symbol() fails)
- **xTAROT**: `0x74D1D2A851e339B8cB953716445Be7E8aBdf92F4` → Fantom only

## Server Docker Rebuild Note (exotic-tokens milestone)

The server `pyproject.toml` was updated from `feat/stablecoin-pricing` to `feat/exotic-tokens` branch to deploy exotic token code. Run:
```bash
cd /Users/bryan/code/ypricemagic-server
# Edit pyproject.toml: ypricemagic @ git+...@feat/exotic-tokens
uv lock --upgrade-package ypricemagic
docker compose up --build -d ypm-ethereum
```

## Known Limitations

- ypricemagic pytest suite does not run reliably on macOS
- All behavioral validation goes through the server Docker stack
- Exotic token addresses may need discovery at test time (not all known upfront)
- Fantom chain (for Geist gTokens, xTAROT) requires a Fantom-specific Docker service which is not running
- Many exotic/novel tokens cause 600+ second cold-start timeouts due to Etherscan ABI fetching
- Tokens with NonStandardERC20 (no symbol() method) cannot be detected by detection functions that rely on symbol
- The ptUSDC V4 ticket and novel tokens consistently timeout on first request in this environment
