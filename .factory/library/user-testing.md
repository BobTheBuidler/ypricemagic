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

## Known Limitations

- ypricemagic pytest suite does not run reliably on macOS
- All behavioral validation goes through the server Docker stack
- Exotic token addresses may need discovery at test time (not all known upfront)
- Fantom chain (for Geist gTokens) requires a Fantom-specific Docker service which may not be running
