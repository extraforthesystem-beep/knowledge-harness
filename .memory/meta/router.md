---
type: Meta
title: Harness Router
description: Harness slash commands and agent workflow
tags:
  - meta
  - harness
timestamp: "2026-07-14T16:47:48.266999+00:00"
---

# Harness slash commands

**Daily:** `/feature-add` · `/memory-sync` (end of session — progress, ADRs, handoff, index/viz)

**One-time:** `/memory-migrate` · `/memory-init`

**Rare:** `/memory-compact` · `/failure-log`

**Aliases → `/memory-sync` (not installed):** `/handoff` · `/extract-memory` · `/compact` · `/harness-sync`

# Agent workflow

1. Read `.memory/index.md` then `progress/status.md`
2. Topic recall on demand → [Memory Authority](memory-authority.md); for features → `features/<slug>.md`; for architecture → `decisions/` (or `domains/` topic map first if present)
3. Hard truth conflict/bend → challenge before write; progress is soft
4. For code exploration → `/graphify query` before grep
5. For writing code → [lazy-code.md](lazy-code.md) (`graphify query` reuse first)
6. After work → run `/memory-sync`

<!-- harness-links:autogen -->
## Graph links

- [Project Context](../context/project.md)
- [`.gitignore` excluded from harness template](../decisions/2026-05-20-gitignore-excluded-from-harness-template.md)
- [`.graphifyignore` included in harness template](../decisions/2026-05-20-graphifyignore-included-in-harness-template.md)
- [Direct Shell/CLI Authentication Inheritance for Hooks](../decisions/2026-05-21-direct-shell-cli-authentication-inheritance-for-hooks.md)
- [Dynamic Path Resolution for Global Hook Installations](../decisions/2026-05-21-dynamic-path-resolution-for-global-hook-installations.md)
- [Cross-IDE harness parity via shared AGENTS.md and install script](../decisions/2026-06-21-cross-ide-harness-parity.md)
- [OKF-native .memory/ bundle as single knowledge store](../decisions/2026-06-21-okf-native-memory-bundle.md)
- [Platform-agnostic hooks with SRE failure log](../decisions/2026-06-21-platform-agnostic-hooks-sre.md)
- [Dogfood upstream — sync harden, memory-compact, optional domains](../decisions/2026-07-14-dogfood-sync-compact-domains.md)
- [Score harness on token-effectiveness ablation, not LongMemEval](../decisions/2026-07-27-token-effectiveness-not-longmemeval.md)
- [Memory Authority — challenge before overriding project truth](../decisions/2026-07-28-memory-authority-challenge-protocol.md)
- [Lazy-code ladder — three squeezers, graphify reuse, OKF debt ledger](../decisions/2026-09-07-lazy-code-ladder-three-squeezers.md)
- [Mechanical ADR append-only hook](../decisions/2026-09-16-mechanical-adr-append-only-hook.md)
- [Ponytail Debt](debt.md)
- [Lazy Code Ladder](lazy-code.md)
- [Memory Authority](memory-authority.md)
- [SRE Memory Routing](sre-routing.md)
- [Session Progress Archive](../progress/archive.md)
- [Session Progress](../progress/status.md)
<!-- /harness-links:autogen -->
