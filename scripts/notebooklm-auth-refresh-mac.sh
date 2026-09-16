#!/usr/bin/env bash
# Mac: refresh NotebookLM auth in a real Terminal (not Cursor agent sandbox).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [[ -x "$ROOT/.venv/bin/notebooklm" ]]; then
  export PATH="$ROOT/.venv/bin:$PATH"
fi
export NOTEBOOKLM_TRANSPORT="${NOTEBOOKLM_TRANSPORT:-curl_cffi}"

unset NOTEBOOKLM_HOME PLAYWRIGHT_BROWSERS_PATH || true

echo "== 1) auth refresh =="
if ! notebooklm auth refresh; then
  echo "Server refresh failed — falling back to Chrome login..."
  rm -rf "${HOME}/.notebooklm/profiles/default/browser_profile"
  notebooklm login --browser chrome --fresh
fi

echo
echo "== 2) auth check --test =="
notebooklm auth check --test --json | tee /tmp/nlm-auth-refresh.json

python3 - <<'PY'
import json, sys
d = json.load(open("/tmp/nlm-auth-refresh.json"))
ok = d.get("status") == "ok" and (d.get("checks") or {}).get("token_fetch") is True
print("RESULT:", "OK" if ok else "FAILED")
sys.exit(0 if ok else 1)
PY

echo
echo "== 3) list notebooks =="
notebooklm list

echo
echo "Auth refresh complete."
