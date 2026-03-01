#!/bin/bash
set -euo pipefail

cd /Users/bryan/code/ypricemagic

# Ensure pip is available in venv
if ! .venv/bin/python -m pip --version &>/dev/null; then
    echo "Installing pip in venv..."
    .venv/bin/python -m ensurepip --default-pip
fi

# Install project + dev dependencies
echo "Installing dependencies..."
.venv/bin/python -m pip install -e . -r requirements-dev.txt -q
.venv/bin/python -m pip install "setuptools<82" click -q

# Configure Brownie network to use the archive node
echo "Configuring Brownie network..."
.venv/bin/brownie networks modify mainnet host=http://10.11.12.43:8545 2>/dev/null || true

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env from .env.sample..."
    cp .env.sample .env
    echo "WARNING: .env created but ETHERSCAN_TOKEN may need to be set"
fi

# Ensure .env is gitignored
if ! grep -q '^\.env$' .gitignore 2>/dev/null; then
    echo ".env" >> .gitignore
    echo "Added .env to .gitignore"
fi

# Clean build artifacts if present
rm -rf build/ *.egg-info/

echo "Environment ready."
