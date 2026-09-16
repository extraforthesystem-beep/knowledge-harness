#!/usr/bin/env bash
# Deploy Knowledge Harness slash commands to Claude, Antigravity, Cursor, and OpenCode.
# Prefer: kh install -p -y   (or kh -p) from any project
# Fallback: bash "$HARNESS_HOME/scripts/install-harness.sh" -p -y
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CLI="$ROOT/packages/knowledge-harness/bin/knowledge-harness.js"

if [[ -f "$CLI" ]]; then
  node "$ROOT/packages/knowledge-harness/scripts/bundle-assets.mjs" >/dev/null 2>&1 || true
  if [[ $# -eq 0 ]]; then
    exec node "$CLI" install -g -y
  fi
  if [[ "$1" == "-p" || "$1" == "-g" || "$1" == "install" || "$1" == "i" ]]; then
    exec node "$CLI" "$@"
  fi
  exec node "$CLI" install "$@"
fi

# Fallback if npm package not present (legacy bash installer)
CMD_SRC="$ROOT/templates/commands"
HOME_DIR="${HOME}"
RESET_OPENCODE=0

for arg in "$@"; do
  if [[ "$arg" == "--reset-opencode" ]]; then
    RESET_OPENCODE=1
  fi
done

# Only these appear in slash-command pickers (daily + one-time + rare).
ACTIVE_CMDS=(
  memory-sync.md
  feature-add.md
  memory-migrate.md
  memory-init.md
  memory-compact.md
  failure-log.md
)

# Removed from pickers — behavior merged into /memory-sync.
REMOVED_CMDS=(
  handoff.md
  extract-memory.md
  compact.md
  harness-sync.md
)

opencode_json_state() {
  local file="$1"
  python3 - "$file" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
legacy = {
    "$schema": "https://opencode.ai/config.json",
    "instructions": ["AGENTS.md", "CROSS-IDE.md", ".memory/index.md"],
}
canonical = {
    **legacy,
    "permission": {"*": "allow"},
}

def stable(value):
    if isinstance(value, list):
        return "[" + ",".join(stable(item) for item in value) + "]"
    if isinstance(value, dict):
        return "{" + ",".join(
            json.dumps(key) + ":" + stable(value[key]) for key in sorted(value)
        ) + "}"
    return json.dumps(value)

if not path.exists():
    print("absent")
    raise SystemExit

try:
    data = json.loads(path.read_text(encoding="utf-8"))
except Exception:
    print("custom")
    raise SystemExit

serialized = stable(data)
if serialized == stable(canonical):
    print("canonical")
elif serialized in {stable(legacy), stable(canonical)}:
    print("managed-legacy")
else:
    print("custom")
PY
}

write_opencode_json() {
  local file="$1"
  cat > "$file" <<'EOF'
{
  "$schema": "https://opencode.ai/config.json",
  "instructions": [
    "AGENTS.md",
    "CROSS-IDE.md",
    ".memory/index.md"
  ],
  "permission": {
    "*": "allow"
  }
}
EOF
}

reset_opencode_install() {
  local commands_dir="$HOME_DIR/.config/opencode/commands"
  local global_agents="$HOME_DIR/.config/opencode/AGENTS.md"
  local project_json="$ROOT/opencode.json"

  for f in "${ACTIVE_CMDS[@]}" "${REMOVED_CMDS[@]}"; do
    if [[ -f "$commands_dir/$f" ]]; then
      rm "$commands_dir/$f"
      echo "  [-] $commands_dir/$f"
    fi
  done

  if [[ -f "$global_agents" ]] && rg -F "Global Knowledge Harness defaults" "$global_agents" >/dev/null 2>&1; then
    rm "$global_agents"
    echo "  [-] $global_agents"
  fi

  if [[ -f "$project_json" ]]; then
    case "$(opencode_json_state "$project_json")" in
      canonical|managed-legacy)
        rm "$project_json"
        echo "  [-] $project_json"
        ;;
      custom)
        echo "  [~] $project_json (preserved custom config)"
        ;;
    esac
  fi
}

install_commands() {
  local dest="$1"
  mkdir -p "$dest"
  for f in "${ACTIVE_CMDS[@]}"; do
    cp "$CMD_SRC/$f" "$dest/$f"
    echo "  [+] $dest/$f"
  done
  for f in "${REMOVED_CMDS[@]}"; do
    if [[ -f "$dest/$f" ]]; then
      rm "$dest/$f"
      echo "  [-] $dest/$f (alias removed)"
    fi
  done
}

echo "=== Knowledge Harness installer ==="
echo "Source: $CMD_SRC (${#ACTIVE_CMDS[@]} active commands)"
echo ""

echo "Claude Code (~/.claude/commands/)"
install_commands "$HOME_DIR/.claude/commands"

echo ""
echo "Antigravity Gemini CLI (~/.gemini/config/global_workflows/)"
install_commands "$HOME_DIR/.gemini/config/global_workflows"

echo ""
echo "Antigravity IDE (~/.gemini/antigravity/global_workflows/)"
install_commands "$HOME_DIR/.gemini/antigravity/global_workflows"

echo ""
echo "Cursor global (~/.cursor/commands/)"
install_commands "$HOME_DIR/.cursor/commands"

echo ""
echo "Cursor project ($ROOT/.cursor/commands/)"
install_commands "$ROOT/.cursor/commands"

echo ""
echo "OpenCode (~/.config/opencode/commands/)"
if [[ "$RESET_OPENCODE" -eq 1 ]]; then
  echo "  [~] Resetting harness-managed OpenCode files before reinstall"
  reset_opencode_install
fi
install_commands "$HOME_DIR/.config/opencode/commands"

echo ""
echo "OpenCode global router (~/.config/opencode/)"
mkdir -p "$HOME_DIR/.config/opencode"
GLOBAL_AGENTS="$HOME_DIR/.config/opencode/AGENTS.md"
cat > "$GLOBAL_AGENTS" <<'EOF'
# Global Knowledge Harness defaults

Applies to all OpenCode sessions alongside project `AGENTS.md`.

**Daily:** `/feature-add` · `/memory-sync`
**One-time:** `/memory-migrate` · `/memory-init`
**Rare:** `/memory-compact` · `/failure-log`

Before any task in a harness project:
1. Read `.memory/index.md` if present
2. Read `.memory/progress/status.md` (or run `/memory-migrate` if flat `PROGRESS.md` exists)
3. Use `/graphify query` for codebase exploration
4. Run `/memory-sync` after updating memory

Legacy upgrade: `/memory-migrate` — flat `.memory/` → OKF layout. Copy scripts from `$HARNESS_HOME/scripts/` if missing.

Project rules take precedence. See project `CROSS-IDE.md` for tool matrix.
EOF
echo "  [+] $GLOBAL_AGENTS"

echo ""
echo "Project harness files"
for p in .cursor/rules/knowledge-harness.mdc .cursor/hooks.json CROSS-IDE.md .agents/GEMINI.md; do
  if [[ -f "$ROOT/$p" ]]; then
    echo "  [ok] $p"
  else
    echo "  [!!] missing $p"
  fi
done

OPENCODE_JSON_PATH="$ROOT/opencode.json"
OPENCODE_JSON_STATE="$(opencode_json_state "$OPENCODE_JSON_PATH")"
if [[ "$OPENCODE_JSON_STATE" == "absent" ]]; then
  write_opencode_json "$OPENCODE_JSON_PATH"
  echo "  [+] opencode.json"
elif [[ "$OPENCODE_JSON_STATE" == "managed-legacy" ]]; then
  write_opencode_json "$OPENCODE_JSON_PATH"
  echo "  [~] opencode.json (upgraded to canonical scaffold)"
elif [[ "$OPENCODE_JSON_STATE" == "canonical" ]]; then
  echo "  [ok] opencode.json"
else
  echo "  [~] opencode.json (preserved custom config)"
fi

chmod +x "$ROOT/scripts/harness-sync.sh" 2>/dev/null || true
chmod +x "$ROOT/.cursor/hooks/harness-sync.sh" 2>/dev/null || true

echo ""
echo "Deploying hooks to ~/.claude/hooks/"
mkdir -p "$HOME_DIR/.claude/hooks"
cp "$ROOT/templates/hooks/"*.js "$HOME_DIR/.claude/hooks/" 2>/dev/null || cp "$ROOT/.cursor/hooks/"*.js "$HOME_DIR/.claude/hooks/"
echo "  [+] ~/.claude/hooks/*.js"

echo ""
echo "=== Done ==="
echo "Active slash commands: ${ACTIVE_CMDS[*]//.md/}"
echo "OpenCode reinstall:"
echo "  npx knowledge-harness install -g -a opencode --reset-opencode -y"
echo "  npx knowledge-harness install -p -a opencode --reset-opencode -y"
echo "Run: bash scripts/sync-harness.sh  # copy hooks to ~/.claude/hooks"
echo "Set OKF_HOME if needed: export OKF_HOME=\"\$HOME/Data/knowledge-catalog/okf\""
echo "Run from project root: python3 scripts/harness-sync.py"
