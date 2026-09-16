---
type: Architectural Decision
title: Cross-IDE harness parity via shared AGENTS.md and install script
description: One OKF .memory/ bundle; routers and commands deployed to Claude, Antigravity, Cursor, OpenCode
tags: "[decision, adr, cross-ide]"
status: accepted
timestamp: "2026-06-21T00:00:00Z"
---

**Decision:** Use `AGENTS.md` as the universal project router. Deploy slash-command templates via `scripts/install-harness.sh` to Claude (`~/.claude/commands/`), Antigravity (`~/.gemini/.../global_workflows/`), and OpenCode global `AGENTS.md`. Cursor uses project `AGENTS.md` + `.cursor/rules/knowledge-harness.mdc` + `.cursor/hooks.json`.

**Why:** Agents should behave identically regardless of IDE. OKF `.memory/` is the single knowledge store; each tool only needs a thin config surface.

**Alternatives considered:** Per-IDE duplicate memory formats — rejected. Tool-specific export mirrors — rejected.

<!-- harness-links:autogen -->
## Graph links

- [Project Context](../context/project.md)
- [`.gitignore` excluded from harness template](2026-05-20-gitignore-excluded-from-harness-template.md)
- [`.graphifyignore` included in harness template](2026-05-20-graphifyignore-included-in-harness-template.md)
- [Direct Shell/CLI Authentication Inheritance for Hooks](2026-05-21-direct-shell-cli-authentication-inheritance-for-hooks.md)
- [Dynamic Path Resolution for Global Hook Installations](2026-05-21-dynamic-path-resolution-for-global-hook-installations.md)
- [OKF-native .memory/ bundle as single knowledge store](2026-06-21-okf-native-memory-bundle.md)
- [Platform-agnostic hooks with SRE failure log](2026-06-21-platform-agnostic-hooks-sre.md)
- [Dogfood upstream — sync harden, memory-compact, optional domains](2026-07-14-dogfood-sync-compact-domains.md)
- [Score harness on token-effectiveness ablation, not LongMemEval](2026-07-27-token-effectiveness-not-longmemeval.md)
- [Memory Authority — challenge before overriding project truth](2026-07-28-memory-authority-challenge-protocol.md)
- [Lazy-code ladder — three squeezers, graphify reuse, OKF debt ledger](2026-09-07-lazy-code-ladder-three-squeezers.md)
- [Mechanical ADR append-only hook](2026-09-16-mechanical-adr-append-only-hook.md)
- [Lazy Code Ladder](../meta/lazy-code.md)
- [Harness Router](../meta/router.md)
- [SRE Memory Routing](../meta/sre-routing.md)
- [Session Progress](../progress/status.md)
<!-- /harness-links:autogen -->
