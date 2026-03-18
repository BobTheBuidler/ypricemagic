#!/bin/bash
set -e

cd /Users/bryan/code/ypricemagic

# Ensure venv exists and has deps
if [ -d ".venv" ]; then
  .venv/bin/pip install -e . --quiet 2>/dev/null || true
  .venv/bin/pip install -r requirements-dev.txt --quiet 2>/dev/null || true
fi

# Fetch upstream if not already available
git fetch upstream --quiet 2>/dev/null || true
