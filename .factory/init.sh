#!/bin/bash
# Minimal init - deps are pre-installed in .venv
echo "init.sh: checking environment..."
cd /Users/bryan/code/ypricemagic
test -f .venv/bin/python && echo "venv OK" || echo "WARNING: no .venv"
git fetch upstream --quiet 2>/dev/null || true
echo "init.sh: done"
