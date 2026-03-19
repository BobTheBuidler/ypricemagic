#!/bin/bash
# Minimal init - deps are pre-installed in .venv
echo "init.sh: checking environment..."
cd /Users/bryan/code/ypricemagic
test -f .venv/bin/python && echo "venv OK" || echo "WARNING: no .venv"
git fetch upstream --quiet 2>/dev/null || true
# Clean mypyc build artifacts that cause brownie INTERNALERROR
# (brownie's test runner tries to hash .o files as Python AST)
rm -rf build/temp.* build/bdist.* build/lib.* 2>/dev/null || true
# Source .env for ETHERSCAN_TOKEN and other env vars
if [ -f .env ]; then
  set -a && source .env && set +a
  echo "Loaded .env"
fi
echo "init.sh: done"
