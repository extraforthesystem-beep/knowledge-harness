#!/usr/bin/env bash
# Cursor sessionEnd hook — regenerate OKF index and viz.html
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
if [[ -f "$ROOT/scripts/harness-sync.py" ]]; then
  python3 "$ROOT/scripts/harness-sync.py" --skip-graphify >/dev/null 2>&1 || true
fi
exit 0
