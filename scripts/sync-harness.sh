#!/usr/bin/env bash
# Copy project hooks to global Claude path and sync Antigravity workflows.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOME_DIR="${HOME:?HOME not set}"
HOOKS_SRC="$ROOT/.cursor/hooks"

echo "=== sync-harness ==="
echo "Copying hooks: $HOOKS_SRC -> $HOME_DIR/.claude/hooks/"
mkdir -p "$HOME_DIR/.claude/hooks"
cp "$HOOKS_SRC/"*.js "$HOME_DIR/.claude/hooks/"
chmod +x "$HOOKS_SRC/"*.js 2>/dev/null || true

SRC_WF="$HOME_DIR/.gemini/config/global_workflows"
DST_WF="$HOME_DIR/.gemini/antigravity/global_workflows"
if [[ -d "$SRC_WF" && -d "$DST_WF" ]]; then
  echo "Syncing workflows: $SRC_WF -> $DST_WF"
  cp "$SRC_WF/"*.md "$DST_WF/" 2>/dev/null || true
fi

HOOKS_JSON="$HOME_DIR/.gemini/config/hooks.json"
if [[ -f "$HOOKS_JSON" ]]; then
  echo "Antigravity hooks config: $HOOKS_JSON"
else
  echo "Note: create $HOOKS_JSON pointing to $HOME_DIR/.claude/hooks/"
fi

echo "Smoke test: node \"$HOME_DIR/.claude/hooks/inject-context.js\""
echo "Done."
