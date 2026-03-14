#!/bin/bash
set -euo pipefail

WORKTREE="/Users/bryan/code/ypricemagic-pricing"
MAIN_REPO="/Users/bryan/code/ypricemagic"

cd "$WORKTREE"

# Use the venv from the main repo (shared)
VENV="$MAIN_REPO/.venv"

if [ ! -d "$VENV" ]; then
    echo "ERROR: .venv not found at $VENV"
    exit 1
fi

# Quick check: if brownie and y are importable, skip full install
if "$VENV/bin/python" -c "import brownie; import click" 2>/dev/null; then
    echo "Dependencies already installed, skipping install."
else
    echo "Installing dependencies..."
    "$VENV/bin/python" -m pip install -e "$WORKTREE" -r "$WORKTREE/requirements-dev.txt" -q
    "$VENV/bin/python" -m pip install "setuptools<82" click -q
fi

# Ensure .env exists (copy from main repo if missing)
if [ ! -f "$WORKTREE/.env" ]; then
    if [ -f "$MAIN_REPO/.env" ]; then
        cp "$MAIN_REPO/.env" "$WORKTREE/.env"
    else
        cp "$WORKTREE/.env.sample" "$WORKTREE/.env"
        echo "WARNING: .env created from sample — ETHERSCAN_TOKEN may need to be set"
    fi
fi

# Ensure .env is gitignored
if ! grep -q '^\.env$' "$WORKTREE/.gitignore" 2>/dev/null; then
    echo ".env" >> "$WORKTREE/.gitignore"
fi

echo "Environment ready (worktree: $WORKTREE, venv: $VENV)."
