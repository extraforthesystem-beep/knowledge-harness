---
type: Architectural Decision
title: Platform-agnostic hooks with SRE failure log
description: Port idea-3 hook upgrades — cross-IDE tool mapping, local fallback, failures log, harness-sync on session end
tags: "[decision, adr, hooks, sre]"
status: accepted
timestamp: "2026-06-21T00:00:00Z"
---

**Decision:** Ship upgraded Node hooks in `.cursor/hooks/` (inject, capture, sync) with OKF paths, token budget warnings, `.memory/` loop prevention, local journal fallback, and auto `harness-sync.py` on session end. Add `.memory/failures/log.md` and `.memory/meta/sre-routing.md` for SRE skill integration.

**Why:** Preserves battle-tested behavior from the pre-OKF harness while using OKF concept paths. Works across Cursor, Claude Code, and Antigravity via shared `~/.claude/hooks/` deploy.

**Alternatives considered:** Shell-only hooks — rejected; Node hooks already handle multi-IDE tool schema mapping.

<!-- harness-links:autogen -->
## Graph links

- [Project Context](../context/project.md)
- [`.gitignore` excluded from harness template](2026-05-20-gitignore-excluded-from-harness-template.md)
- [`.graphifyignore` included in harness template](2026-05-20-graphifyignore-included-in-harness-template.md)
- [Direct Shell/CLI Authentication Inheritance for Hooks](2026-05-21-direct-shell-cli-authentication-inheritance-for-hooks.md)
- [Dynamic Path Resolution for Global Hook Installations](2026-05-21-dynamic-path-resolution-for-global-hook-installations.md)
- [Cross-IDE harness parity via shared AGENTS.md and install script](2026-06-21-cross-ide-harness-parity.md)
- [OKF-native .memory/ bundle as single knowledge store](2026-06-21-okf-native-memory-bundle.md)
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
