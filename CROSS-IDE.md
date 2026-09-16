# Cross-IDE Knowledge Harness

One `.memory/` OKF bundle, four agent surfaces. Same workflow everywhere.

| Tool | Project router | Global config | Slash commands |
|------|----------------|---------------|----------------|
| **Claude Code** | [`CLAUDE.md`](CLAUDE.md) | `~/.claude/CLAUDE.md` | `~/.claude/commands/` — 6 cmds |
| **Antigravity** | [`AGENTS.md`](AGENTS.md) + [`.agents/GEMINI.md`](.agents/GEMINI.md) | `GEMINI.md` (workspace) | `~/.gemini/antigravity/global_workflows/` — 6 cmds |
| **Cursor** | [`AGENTS.md`](AGENTS.md) | `~/.cursor/commands/` (global) | [`.cursor/commands/`](.cursor/commands/) (project) — 6 cmds |
| **OpenCode** | [`AGENTS.md`](AGENTS.md) | `~/.config/opencode/AGENTS.md` | `~/.config/opencode/commands/` — 6 cmds |

Installed commands: `memory-sync`, `feature-add`, `memory-migrate`, `memory-init`, `memory-compact`, `failure-log`. Alias cmds (`handoff`, `extract-memory`, `compact`, `harness-sync`) are removed from pickers — use `/memory-sync`.

## Install (once per machine)

**Recommended — works in any terminal, any IDE (like `npx skills`):**

```bash
npx knowledge-harness install -g -y
```

OpenCode reset/reinstall:

```bash
npx knowledge-harness install -g -a opencode --reset-opencode -y
npx knowledge-harness install -p -a opencode --reset-opencode -y
```

From this repo (dev):

```bash
bash scripts/install-harness.sh
# or
node packages/knowledge-harness/bin/knowledge-harness.js install -g -y
```

**skills.sh ecosystem:**

```bash
npx skills add extraforthesystem-beep/knowledge-harness --skill knowledge-harness -g -y
```

Windows:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/install-harness.ps1
```

## Daily workflow

| Situation | Commands |
|-----------|----------|
| Normal session end | `/memory-sync` (1 cmd) |
| Added/changed a feature | `/feature-add` then `/memory-sync` (2 cmds) |
| Upgrading old flat `.memory/` | `/memory-migrate` once, then daily workflow |
| Token budget over 500 | `/memory-compact` |
| Switching IDE mid-task | `/memory-sync` (handoff included) |

In Cursor, session-end hooks often run `harness-sync.py` automatically — use `/memory-sync` when you want the agent to write progress, ADRs, and features from the session.

## Every session (all tools)

1. Read [`.memory/index.md`](.memory/index.md)
2. Read [`.memory/progress/status.md`](.memory/progress/status.md)
3. Code exploration → `/graphify query` or `graphify-out/GRAPH_REPORT.md`
4. Writing code → `.memory/meta/lazy-code.md` (reuse via graphify first)
5. After work → `/memory-sync`

## Upgrading legacy `.memory/`

If the project still has flat files (`.memory/PROGRESS.md`, `CONTEXT.md`, `DECISIONS.md`) and no `.memory/context/project.md`:

1. Run `/memory-migrate` (or `python scripts/migrate-memory-to-okf.py`)
2. If scripts are missing, copy from a harness checkout (`$HARNESS_HOME/scripts/`) — see [`templates/commands/memory-migrate.md`](templates/commands/memory-migrate.md)
3. Run `python scripts/harness-sync.py`

## Hooks (all platforms)

Project hooks live in [`.cursor/hooks/`](.cursor/hooks/) and deploy globally via:

```bash
bash scripts/sync-harness.sh   # .cursor/hooks → ~/.claude/hooks + workflow sync
```

| Hook | Event | Behavior |
|------|-------|----------|
| `inject-context.js` | Session start | Injects `progress/status.md`; token budget warning at 500 |
| `capture-decisions.js` | Post-tool | Journals writes/installs; skips `.memory/` loop |
| `sync-memory.js` | Session end | Updates progress; local fallback if no API key; runs `harness-sync.py` |

| Tool | Hook config |
|------|-------------|
| **Cursor** | [`.cursor/hooks.json`](.cursor/hooks.json) |
| **Claude Code** | `~/.claude/settings.json` → `~/.claude/hooks/` |
| **Antigravity** | `~/.gemini/config/hooks.json` + `/memory-sync` in GEMINI.md |
| **OpenCode** | Manual `/memory-sync` (no native lifecycle hooks) |

## OpenCode reset

Use the global reset when the command set or global router under `~/.config/opencode/` is broken:

```bash
npx knowledge-harness install -g -a opencode --reset-opencode -y
```

Use the project reset when `opencode.json` in the current project is stale or was generated from the older minimal scaffold:

```bash
npx knowledge-harness install -p -a opencode --reset-opencode -y
```

The reset only removes harness-managed OpenCode files:
- installed harness slash commands in `~/.config/opencode/commands/`
- the harness-generated global `~/.config/opencode/AGENTS.md`
- project `opencode.json` only when it matches a known harness scaffold

Custom OpenCode config is preserved and reported instead of overwritten.

## Local model sync

OpenCode itself can use whatever model/provider you configure in OpenCode. The harness now also supports local OpenAI-compatible providers for `sync-memory.js` when you want automated progress summarization outside the live IDE session.

Set these env vars before running the hook or script:

```bash
export HARNESS_MEMORY_PROVIDER=openai-compatible
export HARNESS_OPENAI_BASE_URL=http://127.0.0.1:11434/v1
export HARNESS_OPENAI_MODEL=qwen3:8b
# optional:
export HARNESS_OPENAI_API_KEY=dummy
```

The hook also accepts `OPENAI_BASE_URL`, `OPENAI_MODEL`, and `OPENAI_API_KEY`.

## Companion tools (external — update from publisher)

The harness routes; it does not vendor these. Refresh from upstream when you want a new version.

| Layer | Tool | Role |
|-------|------|------|
| Prose output | [caveman](https://github.com/JuliusBrussee/caveman) | Shrinks what the agent *says*. Upstream also ships `native-core.md` plus work-pattern skills (`investigate-first`, `lean-build`, `surgical-patch`, `verify-and-stop`) as the caveman half of the same ladder. |
| Code output | [ponytail](https://github.com/DietrichGebert/ponytail) | Shrinks what the agent *builds*. Canonical 7-rung text lives in `.memory/meta/lazy-code.md`. |
| Context (code) | [graphify](https://github.com/Graphify-Labs/graphify) | `graphify query` before grep; rung 2 reuse check. |
| Context (intent) | `.memory/` (this harness) | Decided truth, progress, ADRs, debt ledger. |

Do not run caveman on code or ponytail on prose. Optional later (not installed): serena (code-read), rtk (command output).

## SRE integration

- Failure log: [`.memory/failures/log.md`](.memory/failures/log.md)
- Path map for `sre-architect`: [`.memory/meta/sre-routing.md`](.memory/meta/sre-routing.md)
- Before retrying a failed hypothesis → read failures log

## Optional templates

[`templates/loop/`](templates/loop/) — copy into a project if you want a simple agent-loop `program.md`; not installed by default.

## Environment

```bash
export OKF_HOME="$HOME/Data/knowledge-catalog/okf"   # local OKF visualize tool
```
