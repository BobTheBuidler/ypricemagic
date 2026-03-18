# Abandoned TODOs

These deferred features exist on `abandoned-master` and are intentionally not being ported into `clean-rebuild` during the rebuild mission.

## Pool index V2

- Description: Inverted Uniswap V2 pool index for O(1) token-to-pool lookup.
- Git refs on `abandoned-master`: `b3fcee30`, `0b6439c2`, `c63aff3a`

## Pool index V3

- Description: Inverted Uniswap V3 pool index for O(1) token-to-pool lookup.
- Git refs on `abandoned-master`: `c3d1230d`

## Multi-hop routing

- Description: Multi-hop DEX routing through intermediate tokens.
- Git refs on `abandoned-master`: `16b6996c`, `ec6f5b0b`, `a7654f22`, `ac29dee8`

## Quote-token support

- Description: Pricing in arbitrary quote tokens, then reverted.
- Git refs on `abandoned-master`: `d283b85d`, `ff03e713`, `4ec0579c`; reverted in `d1dfd456`

## Stablecoin pricing overhaul

- Description: Real market prices for stablecoins, then partially reverted.
- Git refs on `abandoned-master`: `1cae065c`, `d2ab29b8`, `7715db84`, `452149e6`

## V3 fee-tier explosion fix

- Description: Reduce N² fee-tier path combinations to linear growth.
- Git refs on `abandoned-master`: `5e083784`

## V2 factory.getPair() O(1) lookup

- Description: Query V2 factory directly instead of scanning 330k+ pairs.
- Git refs on `abandoned-master`: `54e10f94`

## Amount parameter for price impact

- Description: Optional amount parameter for slippage-aware pricing.
- Git refs on `abandoned-master`: `587a4349`

## VTTLCache per-key TTL

- Description: Variable-TTL caching, only needed for amount-parameter pricing.
- Git refs on `abandoned-master`: `3eec7800`
