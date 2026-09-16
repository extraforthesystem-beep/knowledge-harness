---
description: Main end-of-session command — sync all .memory/ concepts, handoff, and index.
---

## 0. Legacy `.memory/` upgrade (if needed)

If flat files exist at `.memory/` root (`PROGRESS.md`, `CONTEXT.md`, `DECISIONS.md`) and `.memory/context/project.md` is missing, run `/memory-migrate` before syncing.

## 0b. Memory Authority (hard truth gate)

Read [.memory/meta/memory-authority.md](../../.memory/meta/memory-authority.md) if present.

- **Soft (no challenge):** `progress/status.md`, handoff, feature frontmatter-only `status`/`priority`
- **Hard:** new/changed ADRs, feature body/contract, architecture fields in `context/project.md`
- If a hard write **conflicts, overrides, removes, or bends** existing truth → stop; challenge (`keep / update / remove / add`) and wait for confirm. Do **not** edit old ADR files — append new.
- Non-conflicting new ADR (already decided this session) → write, then summarize.

## 1. Update from this session

If `.memory/progress/unsummarized.md` exists, fold those paths into Done (one short line), then delete the file. Do not copy basename dumps into inject.

1. `.memory/progress/status.md` — Done / In progress / Next (keep the injected body under 500 tokens)
2. New ADRs → `.memory/decisions/YYYY-MM-DD-slug.md` (one file per decision, do not edit old ADRs)
3. `.memory/context/project.md` — stack, phase, branch, key paths if changed
4. Feature files under `.memory/features/` — update frontmatter `status`, `priority`

## 1b. Handoff (if switching tools or IDE)

If the user is switching tools (Claude, Cursor, Antigravity, OpenCode), append to `.memory/progress/status.md` under `## Handoff`:

- What was done this session
- What is in progress
- Exact next steps
- Blockers or open decisions
- Key files touched

## 1c. Summarize (if session was long or verbose)

Summarize current session goals into `.memory/progress/status.md`. Archive verbose notes into feature or decision concepts if needed.

## 2. Sync

Run: `python scripts/harness-sync.py` (copy from `$HARNESS_HOME/scripts/` if missing — see `/memory-migrate`). Sync regenerates `.memory/meta/debt.md`; review `no-trigger` rows.

## 3. Token budget check

Read `.memory/index.md`. If estimated injection exceeds 500 tokens, suggest `/memory-compact`.

Confirm what was updated. If handoff was written: "Safe to switch tools."
