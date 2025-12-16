#!/bin/bash

set -euo pipefail

if [ "${SKYVERN_SKIP_PLAYWRIGHT_INSTALL:-}" = "true" ]; then
  exit 0
fi

if python -c "from pathlib import Path; from playwright.sync_api import sync_playwright; p=sync_playwright().start(); exe=Path(p.chromium.executable_path); p.stop(); raise SystemExit(0 if exe.exists() else 1)"; then
  exit 0
fi

echo "Playwright Chromium missing; installing..."
python -m playwright install chromium

