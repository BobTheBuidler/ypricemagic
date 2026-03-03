#!/bin/bash
set -euo pipefail

cd /Users/bryan/code/ypricemagic

# Quick check: if brownie and y are importable, skip full install
if .venv/bin/python -c "import brownie; import click" 2>/dev/null; then
    echo "Dependencies already installed, skipping install."
else
    # Ensure pip is available in venv
    if ! .venv/bin/python -m pip --version &>/dev/null; then
        echo "Installing pip in venv..."
        .venv/bin/python -m ensurepip --default-pip
    fi

    echo "Installing dependencies..."
    .venv/bin/python -m pip install -e . -r requirements-dev.txt -q
    .venv/bin/python -m pip install "setuptools<82" click -q
fi

# Ensure cachebox is installed
if ! .venv/bin/python -c "import cachebox" 2>/dev/null; then
    echo "Installing cachebox..."
    .venv/bin/python -m pip install cachebox -q
fi

# Configure Brownie network (fast, idempotent)
.venv/bin/brownie networks modify mainnet host=http://10.11.12.43:8545 2>/dev/null || true

# Ensure .env exists with ETHERSCAN_TOKEN
if [ ! -f .env ]; then
    cp .env.sample .env
    echo "WARNING: .env created but ETHERSCAN_TOKEN may need to be set"
fi

# Ensure .env is gitignored
if ! grep -q '^\.env$' .gitignore 2>/dev/null; then
    echo ".env" >> .gitignore
fi

echo "Environment ready."
