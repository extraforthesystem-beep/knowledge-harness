---
description: Migrate flat legacy .memory/ (PROGRESS.md, CONTEXT.md) to OKF concept layout.
---

Upgrade an **old harness** `.memory/` bundle to the OKF-native layout.

## Detect legacy layout

Legacy (flat) if any of these exist at `.memory/` root **and** `.memory/context/project.md` is missing:

- `PROGRESS.md`
- `CONTEXT.md`
- `DECISIONS.md`
- `DECISIONS-archive.md`
- `INDEX.md`

OKF-native if `.memory/context/project.md` exists with YAML frontmatter (`type: Project Context`).

## Run migration

1. **Dry run first:** `python scripts/migrate-memory-to-okf.py --dry-run`
2. **Apply:** `python scripts/migrate-memory-to-okf.py`
3. **Re-sync:** `python scripts/harness-sync.py`

Options: `--force` re-migrates from flat sources; leftover flat files move to `.memory/_legacy/`.

## If migration script is missing from this repo

Copy harness scripts from a Knowledge Harness checkout, then migrate:

```bash
# Set HARNESS_HOME to your harness template checkout (adjust path)
export HARNESS_HOME="${HARNESS_HOME:-$HOME/Data/harness}"
mkdir -p scripts
cp "$HARNESS_HOME/scripts/migrate-memory-to-okf.py" scripts/
cp "$HARNESS_HOME/scripts/harness-sync.py" scripts/
cp "$HARNESS_HOME/scripts/harness-sync.sh" scripts/ 2>/dev/null || true
chmod +x scripts/harness-sync.sh 2>/dev/null || true
python scripts/migrate-memory-to-okf.py
python scripts/harness-sync.py
```

Also deploy global slash commands once per machine:

```bash
bash "$HARNESS_HOME/scripts/install-harness.sh"
```

Confirm: list migrated paths under `.memory/context/`, `.memory/progress/`, `.memory/decisions/`, and that flat files are in `.memory/_legacy/`.
