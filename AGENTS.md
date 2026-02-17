# Agent Requirements

All agents must follow these rules:

1) Fully test your changes before submitting a PR (run the full suite or all relevant tests).
2) PR titles must be descriptive and follow Conventional Commits-style prefixes:
   - Common: `feat:`, `fix:`, `chore:`, `refactor:`, `docs:`, `test:`, `perf:`
   - Support titles: `fix(docs):`, `fix(benchmarks):`, `fix(cicd):`
3) Commit messages must follow the same Conventional Commits-style prefixes and include a short functional description plus a user-facing value proposition.
4) PR descriptions must include Summary, Rationale, and Details sections.
5) Run relevant Python tests for changes (pytest/unittest or the repo's configured runner).
6) Follow formatting/linting configured in pyproject.toml, setup.cfg, tox.ini, or ruff.toml.
7) Update dependency lockfiles when adding or removing Python dependencies.
8) When adding or refactoring async RPC/price-fetching code, keep or add `y._decorators.stuck_coro_debugger` so the `y.stuck?` DEBUG logger continues emitting "still executing" messages at the default 5-minute interval (via `a_sync.debugging.stuck_coro_debugger`).
9) If you touch ypricemagic-driven price lookups or related docs, keep the `y.stuck?` logger guidance accurate (DEBUG-only, 5-minute interval) so long-running calls can be diagnosed.
10) If the repo uses mypyc, verify tests run against compiled extensions (not interpreted Python) and note how you confirmed.
11) Maximize the use of caching in GitHub workflow files to minimize run duration.
12) Use one of `paths` or `paths-ignore` in every workflow file to make sure workflows only run when required.
13) All mypy configuration (flags, overrides, per-module ignores, and file targets) should go in pyproject.toml. Do not split config across CLI args, mypy.ini, setup.cfg, or workflow steps.
14) Centralize pytest settings (flags, markers, ignore patterns, and targets) in pyproject.toml, pytest.ini, setup.cfg, or tox.ini; workflows/hooks should call pytest without inline args.
15) If the branch you're assigned to work on is from a remote (ie origin/master or upstream/awesome-feature) you must ensure you fetch and pull from the remote before you begin your work.
16) For testing: use Python 3.12 and run `PYTEST_ADDOPTS="-p no:pytest_ethereum" BROWNIE_NETWORK=mainnet make test`.
    Note: in a clean env this currently fails (ContractLogicError / aggregator assertions) even with `setuptools<81` and `click` installed. As long as the tests run, and no new failures pop up, we're good. If working on a section of the codebase with existing test failures, try to fix those particular tests.
17) Local pip install . generates build/; clean up before closing a worktree to avoid dirty state.
Reference: https://www.conventionalcommits.org/en/v1.0.0/
