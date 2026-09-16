---
type: Architectural Decision
title: Lazy-code ladder — three squeezers, graphify reuse, OKF debt ledger
description: Ponytail owns code writes; caveman owns prose; graphify + .memory own context; harvest ponytail markers into meta/debt.md
tags:
  - decision
  - adr
  - ponytail
  - graphify
  - caveman
status: accepted
timestamp: "2026-09-07T00:00:00Z"
---

**Decision:** Every code write in a harness project climbs the 7-rung ponytail ladder in `.memory/meta/lazy-code.md`. Rung 2 is `graphify query "<capability>"` (reuse before rewrite). Prose stays caveman. Context stays graphify + `.memory/`. `harness-sync.py` harvests `ponytail:` comments into `.memory/meta/debt.md`. `/sre-architect` Gate H records which rung stopped the write.

**Why:** Caveman squeezes talk; without a code ladder agents still rewrite helpers and add deps. Graphify is already the search-first tool — reuse checks must use it, not a second grep path. Debt that lives only in `/ponytail-debt` skill output is not an OKF node, so it vanishes between sessions.

**Alternatives considered:** Vendor the full ponytail SKILL.md into the package — rejected (publisher updates; harness is a router). Use caveman `native-core.md` as the canonical ladder — rejected (user supplied ponytail 7-rung text). On-demand `/ponytail-debt` only — rejected (ledger must be an OKF concept). Add serena/rtk — rejected (not installed; optional later).

**Does not reverse:** Memory-only core (no agent-loop), token-effectiveness ablation scoring, cross-IDE parity, Memory Authority, OKF-native store, graphify as code discovery.

**Honest limit:** Markdown policy is soft enforcement — agents can ignore the ladder; debt harvest only sees comment-prefixed `ponytail:` markers.

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
- [Dogfood upstream — sync harden, memory-compact, optional domains](2026-07-14-dogfood-sync-compact-domains.md)
- [Score harness on token-effectiveness ablation, not LongMemEval](2026-07-27-token-effectiveness-not-longmemeval.md)
- [Memory Authority — challenge before overriding project truth](2026-07-28-memory-authority-challenge-protocol.md)
- [Mechanical ADR append-only hook](2026-09-16-mechanical-adr-append-only-hook.md)
- [Lazy Code Ladder](../meta/lazy-code.md)
- [Harness Router](../meta/router.md)
- [SRE Memory Routing](../meta/sre-routing.md)
- [Session Progress](../progress/status.md)
<!-- /harness-links:autogen -->
