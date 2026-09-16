---
name: knowledge-harness
description: >-
  Cross-IDE OKF memory harness — install slash commands (/memory-sync, /feature-add),
  hooks, and .memory/ bundle for Cursor, Claude Code, Antigravity, OpenCode.
  Use when setting up project memory, migrating flat PROGRESS.md to OKF, or syncing session state.
---

# Knowledge Harness

One `.memory/` OKF bundle, every IDE. Same workflow as the [Knowledge Harness](https://github.com/extraforthesystem-beep/knowledge-harness) template.

## Quick install (any terminal, any IDE)

```bash
npx knowledge-harness install -g -y
```

Project-only (commit `.cursor/commands/` with repo):

```bash
npx knowledge-harness install -p -y
npx knowledge-harness init
```

## Daily commands (6 in picker)

| Command | When |
|---------|------|
| `/memory-sync` | End of session — progress, ADRs, handoff, index |
| `/feature-add` | New or changed feature spec |
| `/memory-migrate` | Once — flat `.memory/` → OKF |
| `/memory-init` | Blank scaffold (new project) |
| `/memory-compact` | Token budget over 500 |
| `/failure-log` | SRE failed hypothesis |

## Agent workflow

1. Read `.memory/index.md` → `.memory/progress/status.md`
2. Follow Memory Authority (`.memory/meta/memory-authority.md`) — challenge before overriding hard truth
3. Code exploration → `/graphify query` before grep
4. Writing code → `.memory/meta/lazy-code.md` (`graphify query` reuse first; caveman for prose, ponytail for code)
5. After work → `/memory-sync` (regenerates `.memory/meta/debt.md`)

## Token layers

| Layer | Owner |
|-------|--------|
| Prose | caveman (external) |
| Code | ponytail ladder in `lazy-code.md` |
| Context | `graphify query` + `.memory/` |

Companion tools stay with their publishers. `sre-architect` v20 Gate H records which ladder rung stopped the write.

## Measured (2026-09-07, this repo)

`python scripts/benchmark-ablation.py` + `python scripts/benchmark-harness.py --compare`. Tokens = `ceil(chars/4)`.

- Task ablation: WITH 5,795 tok vs WITHOUT 170,022 tok — **96.6% saved**; hit-rate 8/8 vs 7/8
- Session inject (`inject-context.js` → `progress/status.md`, autogen nav stripped): **~399 tok** under budget 500 (was ~766 OVER on 2026-09-07)
- Sync `--skip-graphify`: mean **132 ms** (Jul 27 ~1,252 ms)
- TSVs: `docs/benchmark-ablation.tsv`, `docs/benchmark-results.tsv`, `docs/benchmark-comparison.tsv`

Not LongMemEval. Harness is project memory; pair with one of {claude-mem, agentmemory} for session recall.

## CLI reference

```bash
npx knowledge-harness detect
npx knowledge-harness install -g -y -a cursor -a claude-code
npx knowledge-harness init
npx knowledge-harness migrate
npx knowledge-harness sync
```

## Supported agents

`claude-code`, `cursor`, `opencode`, `antigravity` — auto-detected like [skills.sh](https://skills.sh).

Also installable via skills ecosystem:

```bash
npx skills add extraforthesystem-beep/knowledge-harness --skill knowledge-harness -g -y
```
