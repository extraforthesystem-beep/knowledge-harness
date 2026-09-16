#!/usr/bin/env bash
# Fresh deep research: Loop Engineering + agent memory (run in Mac Terminal).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [[ -x "$ROOT/.venv/bin/notebooklm" ]]; then
  export PATH="$ROOT/.venv/bin:$PATH"
fi
export NOTEBOOKLM_TRANSPORT="${NOTEBOOKLM_TRANSPORT:-curl_cffi}"

unset NOTEBOOKLM_HOME PLAYWRIGHT_BROWSERS_PATH || true

echo "== auth =="
notebooklm auth check --test --json | tee /tmp/nlm-auth.json
python3 - <<'PY'
import json, sys
d = json.load(open("/tmp/nlm-auth.json"))
ok = d.get("status") == "ok" and (d.get("checks") or {}).get("token_fetch") is True
if not ok:
    print("Auth not ready. Run: bash scripts/notebooklm-auth-refresh-mac.sh", file=sys.stderr)
    sys.exit(1)
print("auth ok")
PY

STAMP=$(date +%Y-%m-%d-%H%M)
TITLE="Research: Loop Engineering + Agent Memory (${STAMP})"
QUERY=$(cat <<'EOF'
Loop Engineering and AI agent memory systems (2025-2026). Fresh pass — prefer newest primary sources.

Cover:
1) Loop Engineering: definition, origins (Peter Steinberger, Boris Cherny, Addy Osmani / X posts), vs prompt engineering and harness engineering; primitives (/goal, /loop, routines, skills, subagents, hooks, worktrees, verification, budgets, stop conditions).
2) Agent memory systems: short-term vs long-term, session memory, RAG / semantic recall, structured project memory (OKF, CLAUDE.md, AGENTS.md, .memory bundles); tools like claude-mem, agentmemory, Mem0, Zep, Letta/MemGPT; how memory feeds agent loops.
3) How loop engineering and memory compose: state outside chat, failure logs, convergence criteria, cost/token risks.
4) Practical patterns for Claude Code, Codex, Cursor, OpenCode.

Exclude unrelated civil/mechanical "loop engineering" companies.
EOF
)

OUT_DIR="${HOME}/Desktop/notebooklm-loop-memory-${STAMP}"
mkdir -p "$OUT_DIR"

echo "== create notebook: $TITLE =="
CREATE_JSON=$(notebooklm create "$TITLE" --json)
echo "$CREATE_JSON" | tee "$OUT_DIR/create.json"
NB_ID=$(python3 -c 'import json,sys; print(json.load(sys.stdin)["notebook"]["id"])' <<<"$CREATE_JSON")
echo "$NB_ID" | tee "$OUT_DIR/notebook_id.txt"
echo "Open: https://notebooklm.google.com/notebook/$NB_ID"

echo "== deep research =="
notebooklm source add-research "$QUERY" --mode deep --no-wait -n "$NB_ID"
echo "Waiting/importing (up to ~30 min)..."
notebooklm research wait -n "$NB_ID" --import-all --timeout 1800

echo "== sources =="
notebooklm source list -n "$NB_ID" | tee "$OUT_DIR/sources.txt"

echo "== summary ask =="
notebooklm ask -n "$NB_ID" --json "$(cat <<'EOF'
Synthesize: What is Loop Engineering, how does it relate to agent harnesses, and what memory architectures make agent loops reliable? Give a structured brief with definitions, key people/posts, primitives, memory layers, and concrete recommendations for a Knowledge Harness + deep-recall plugin setup. Prefer newest sources from this notebook.
EOF
)" | tee "$OUT_DIR/summary.json" /tmp/nlm-loop-memory-summary.json

python3 - <<PY
import json
from pathlib import Path
d = json.load(open("/tmp/nlm-loop-memory-summary.json"))
ans = d.get("answer") or ""
Path("$OUT_DIR/summary.md").write_text(ans + "\n", encoding="utf-8")
print("Wrote summary.md (", len(ans), "chars)")
PY

echo
echo "Done."
echo "Notebook: https://notebooklm.google.com/notebook/$NB_ID"
echo "Files: $OUT_DIR"
