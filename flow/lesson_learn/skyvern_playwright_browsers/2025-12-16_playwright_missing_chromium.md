# Playwright chromium missing (Skyvern local run)

- Symptom: workflow runs fail when starting browser context; error says Chromium executable missing in `~/.cache/ms-playwright`.
- Root cause: Playwright python package installed/updated but browser binaries not installed for the current user.
- Fix: install browsers once (`python -m playwright install chromium`), and add a startup check in `run_skyvern.sh` to auto-install if missing.
- Verification: remote Tailscale run completes after install; local Playwright smoke launch passes.

