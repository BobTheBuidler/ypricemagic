#!/bin/bash
set -e

cd /Users/bryan/code/ypricemagic-pool-index

# Install ypricemagic as editable into the server venv
uv pip install -e . --python /Users/bryan/code/ypricemagic-server/.venv/bin/python 2>&1 | tail -3

echo "init.sh complete"
