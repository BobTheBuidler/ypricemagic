---
name: server-worker
description: Implements features in ypricemagic-server (FastAPI backend, Svelte frontend, Docker, caching, integration tests)
---

# Server Worker

NOTE: Startup and cleanup are handled by `worker-base`. This skill defines the WORK PROCEDURE.

## When to Use This Skill

Use for features that modify ypricemagic-server: FastAPI backend, Svelte frontend, Docker configuration, caching logic, integration test scripts, and PR merge/dependency updates.

## Important Context

- **Server repo:** `/Users/bryan/code/ypricemagic-server`
- **ypricemagic worktree:** `/Users/bryan/code/ypricemagic-pricing` (for reference, read-only during server work)
- **Docker stack:** Already running on ports 8000 (Traefik), 8001 (backend), 8080 (frontend)
- **NEVER** run `docker build --no-cache` or `docker compose build --no-cache`
- Server installs ypricemagic via `ypricemagic @ git+https://github.com/SatoshiAndKin/ypricemagic.git@master` in pyproject.toml
- Frontend: Svelte 5 + Vite + TypeScript in `frontend/` directory

## Work Procedure

### 1. Understand the Feature

- Read feature description, preconditions, expectedBehavior, verificationSteps
- Read relevant source files in `/Users/bryan/code/ypricemagic-server/`
- Key files:
  - `src/server.py` — FastAPI application (main backend)
  - `src/cache.py` — diskcache price cache
  - `frontend/src/` — Svelte frontend
  - `scripts/` — utility scripts (validate_prices.py, test_web_ui.py)
  - `docker-compose.yml` — Docker Compose configuration
  - `pyproject.toml` — Python dependencies (ypricemagic version here)

### 2. For PR Merge / Dependency Update Features

- Merge ypricemagic PRs: `gh pr merge <number> --merge`
- Update pyproject.toml ypricemagic dependency if needed
- Rebuild Docker: `cd /Users/bryan/code/ypricemagic-server && docker compose up --build -d`
- Wait for healthy: `docker compose ps` and check health status
- Verify updated code: `curl -sf http://localhost:8000/ethereum/price?token=0xdAC17F958D2ee523a2206206994597C13D831ec7` should now return source != "stable usd"

### 3. For Backend/Caching Features

- Write tests first in `src/tests/` following existing patterns (httpx TestClient)
- Implement changes in `src/server.py`, `src/cache.py`, or new files
- Run tests: `cd /Users/bryan/code/ypricemagic-server && uv run pytest src/tests/ -x -v`
- For script changes: create/modify files in `scripts/`

### 4. For Frontend Features

- Make changes in `frontend/src/`
- Frontend uses Svelte 5, TypeScript, Vite
- Test: `cd /Users/bryan/code/ypricemagic-server/frontend && npm run build`
- After changes, rebuild Docker to pick up frontend changes:
  `cd /Users/bryan/code/ypricemagic-server && docker compose up --build -d`
- Verify via browser or curl

### 5. For Integration Test Features

- Write integration tests as scripts in `scripts/` or as pytest files
- Tests should exercise the running Docker stack via curl:
  ```bash
  # Test stablecoin pricing
  curl -sf --max-time 120 "http://localhost:8000/ethereum/price?token=0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
  curl -sf --max-time 120 "http://localhost:8000/ethereum/price?token=0xdAC17F958D2ee523a2206206994597C13D831ec7"
  curl -sf --max-time 120 "http://localhost:8000/ethereum/price?token=0x6B175474E89094C44Da98b954EedeAC495271d0F"
  ```
- Verify: response includes `"price"` field, price is reasonable, no timeouts
- For Playwright tests: existing test at `scripts/test_web_ui.py` as reference
- Record all curl responses in handoff

### 6. Verify and Clean Up

- Run server tests: `cd /Users/bryan/code/ypricemagic-server && uv run pytest src/tests/ -x -v`
- Run linting: `cd /Users/bryan/code/ypricemagic-server && uv run ruff check src/`
- Ensure Docker stack is healthy after any rebuilds

## Example Handoff

```json
{
  "salientSummary": "Merged ypricemagic PRs #1-#4 into master, updated pyproject.toml dep, rebuilt Docker. Verified USDT now returns price=0.9998 with source='uniswap v2' (was 'stable usd'). USDC still returns 1.0. DAI returns 1.0003. MIC returns 0.00123 with trade_path showing USDT→USDC hop. No timeouts on any lookup.",
  "whatWasImplemented": "Merged 4 PRs, updated ypricemagic dependency in pyproject.toml, rebuilt Docker container. Ran integration tests verifying all stablecoin pricing changes work end-to-end.",
  "whatWasLeftUndone": "",
  "verification": {
    "commandsRun": [
      {"command": "gh pr merge 12 --merge", "exitCode": 0, "observation": "PR merged"},
      {"command": "docker compose up --build -d", "exitCode": 0, "observation": "Container rebuilt"},
      {"command": "curl .../price?token=USDT", "exitCode": 0, "observation": "price=0.9998, source=uniswap v2"}
    ],
    "interactiveChecks": [
      {"action": "Waited for container health", "observed": "healthy after 30s"},
      {"action": "Tested MIC via curl", "observed": "price=0.00123, trade_path shows [MIC→USDT→USDC]"}
    ]
  },
  "tests": {"added": []},
  "discoveredIssues": []
}
```

## When to Return to Orchestrator

- ypricemagic PRs have merge conflicts that need resolution
- Docker build fails (not a cache issue — do NOT use --no-cache)
- Server health check fails after rebuild and cannot be diagnosed
- Feature requires changes to ypricemagic library code (wrong worker type)
- External service (RPC node, Etherscan) is unreachable
