---
type: Architectural Decision
title: Dogfood upstream — sync harden, memory-compact, optional domains
description: "Port production dogfood improvements from idea 3 into the harness: safer sync, ADR-sorted index, lean inject, compact script, optional domain maps"
tags:
  - decision
  - harness
  - dogfood
status: accepted
timestamp: "2026-07-14T16:45:00+00:00"
---

**Status:** accepted

**Context:** Trade Profit (`idea 3`) dogfooded the OKF harness at ADR scale (200+ decisions). Several sync/budget/navigation fixes lived only in that repo. Upstream them so every install gets the same behavior.

**Decision — ship these harness improvements:**

1. **`harness-sync.py` harden**
   - macOS case-insensitive FS: never archive real `index.md` when cleaning stray `INDEX.md`
   - Soft-fail `_legacy` / `log.md` OSError (TCC locks) so sync still completes
   - Cap context inject at 1200 chars; only `in-progress`/`planned` features in token estimate and Active Features table
   - `decisions/index.md` sorted by ADR number (archive section preserved)
   - Optional **domain maps**: auto-discover `.memory/domains/*.md`, add to graph spine, link domains→decisions, show Domain Maps entry point only when present

2. **`memory-compact.py`**
   - Automate `/memory-compact`: move `superseded`/`deprecated` ADRs and completed features older than 14d to `archive/`
   - Command text runs the script instead of manual moves

3. **`memory-init` scaffold**
   - Create empty `domains/` (+ README) so projects know the optional pattern

**Not upstreamed (project-specific):**
- Idea 3 product domain files (deposits, MLM, engine, …)
- Idea 3 `AGENTS.md` Next.js / graphify project rules
- Older idea 3 `sync-harness.sh` (harness copy is newer)

**Consequences:** Re-run `node packages/knowledge-harness/scripts/bundle-assets.mjs` before publish. Existing projects get improvements by copying `scripts/harness-sync.py` + `memory-compact.py` or reinstalling the package.

<!-- harness-links:autogen -->
## Graph links

- [Project Context](../context/project.md)
- [`.gitignore` excluded from harness template](2026-05-20-gitignore-excluded-from-harness-template.md)
- [`.graphifyignore` included in harness template](2026-05-20-graphifyignore-included-in-harness-template.md)
- [Direct Shell/CLI Authentication Inheritance for Hooks](2026-05-21-direct-shell-cli-authentication-inheritance-for-hooks.md)
- [Dynamic Path Resolution for Global Hook Installations](2026-05-21-dynamic-path-resolution-for-global-hook-installations.md)
- [Cross-IDE harness parity via shared AGENTS.md and install script](2026-06-21-cross-ide-harness-parity.md)
- [OKF-native .memory/ bundle as single knowledge store](2026-06-21-okf-native-memory-bundle.md)
- [Platform-agnostic hooks with SRE failure log](2026-06-21-platform-agnostic-hooks-sre.md)
- [Score harness on token-effectiveness ablation, not LongMemEval](2026-07-27-token-effectiveness-not-longmemeval.md)
- [Memory Authority — challenge before overriding project truth](2026-07-28-memory-authority-challenge-protocol.md)
- [Lazy-code ladder — three squeezers, graphify reuse, OKF debt ledger](2026-09-07-lazy-code-ladder-three-squeezers.md)
- [Mechanical ADR append-only hook](2026-09-16-mechanical-adr-append-only-hook.md)
- [Lazy Code Ladder](../meta/lazy-code.md)
- [Harness Router](../meta/router.md)
- [SRE Memory Routing](../meta/sre-routing.md)
- [Session Progress](../progress/status.md)
<!-- /harness-links:autogen -->
