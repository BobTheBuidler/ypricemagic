# Agent Requirements

All agents must follow these rules:

1) Fully test your changes before submitting a PR (run the full suite or all relevant tests).
2) PR titles must be descriptive and follow Conventional Commits-style prefixes:
   - Common: `feat:`, `fix:`, `chore:`, `refactor:`, `docs:`, `test:`, `perf:`
   - Support titles: `fix(docs):`, `fix(benchmarks):`, `fix(cicd):`
3) When adding or refactoring async RPC/price-fetching code, keep or add `y._decorators.stuck_coro_debugger` so the `y.stuck?` DEBUG logger continues emitting "still executing" messages at the default 5-minute interval (via `a_sync.debugging.stuck_coro_debugger`).

Reference: https://www.conventionalcommits.org/en/v1.0.0/
