#!/bin/bash
set -e

cd /Users/bryan/code/ypricemagic

# Only install if deps seem missing (check for brownie as canary)
if ! .venv/bin/python -c "import brownie" 2>/dev/null; then
  .venv/bin/pip install -e . --quiet 2>/dev/null || true
fi

# Install dev deps if pytest-asyncio-cooperative missing
if ! .venv/bin/python -c "import pytest_asyncio_cooperative" 2>/dev/null; then
  .venv/bin/pip install -r requirements-dev.txt --quiet 2>/dev/null || true
fi

# Fetch upstream if not already available
git fetch upstream --quiet 2>/dev/null || true
