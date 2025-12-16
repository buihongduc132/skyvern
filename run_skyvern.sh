#!/bin/bash

set -euo pipefail

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Please add your api keys to the .env file."
fi

port="$(rg -N '^PORT=' .env | tail -n 1 | cut -d= -f2)"
if [ -z "${port:-}" ]; then
  port="28743"
fi

if [ -f .skyvern-server.pid ]; then
  old_pid="$(cat .skyvern-server.pid 2>/dev/null || true)"
  if [ -n "${old_pid:-}" ]; then
    kill "$old_pid" 2>/dev/null || true
  fi
fi

pkill -u "$(id -u)" -f "python -m skyvern\\.forge" 2>/dev/null || true

pid="$(lsof -t -iTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)"
if [ -n "${pid:-}" ]; then
  kill $pid || true
fi

uv sync
./run_alembic_check.sh

uv run bash scripts/ensure_playwright_chromium.sh

mkdir -p temp
nohup env PYTHONPATH="$(pwd)" bash -c "set -a; source .env; set +a; cd temp && uv run python -m skyvern.forge" >.skyvern-server.log 2>&1 &
echo $! >.skyvern-server.pid
