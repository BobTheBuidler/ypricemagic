# User Testing

## Validation Surface

- **Surface:** Python smoke test scripts run locally against live RPC
- **Tool:** Execute tool (run script, check stdout output)
- **No browser/CLI/API surface** — this is a pure library refactor

## Validation Concurrency

**Max concurrent validators: 1**

Rationale: Each smoke test instance requires brownie connected to mainnet, loads 330k+ pool objects into memory (~500MB+), and makes RPC calls. Running multiple instances would exceed reasonable memory (36GB machine, ~6GB baseline usage) and conflict on brownie's global state.

## Smoke Test Pattern

Scripts should:
1. Apply macOS SemLock monkey-patch (MUST be first)
2. Connect brownie to mainnet
3. Import ypricemagic
4. Call get_price() for various tokens at specific blocks
5. Report prices and wall-clock timing
6. Expected total runtime: 2-5 minutes (60s+ for init + pool loading)

## Known Constraints

- Module import triggers dank_mids initialization (~30s)
- First pool access triggers event loading from SQLite (~30-120s on warm restart)
- Cold start (no SQLite cache) takes 10-30 minutes — avoid if possible
- Python 3.12 on macOS requires SemLock monkey-patch
