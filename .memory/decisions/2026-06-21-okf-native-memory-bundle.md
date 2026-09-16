---
type: Architectural Decision
title: OKF-native .memory/ bundle as single knowledge store
description: .memory/ is the OKF bundle; graphify is code discovery; no export mirror or GCP
tags: "[decision, adr, okf]"
status: accepted
timestamp: "2026-06-21T00:00:00Z"
---

**Decision:** Evolve `.memory/` in place into an OKF knowledge bundle. Graphify remains the codebase discovery layer. No separate `okf/` export folder and no GCP Knowledge Catalog toolchain.

**Why:** OKF provides structured, linkable, portable concepts. Harness hooks and slash commands provide the operational layer. Merging both eliminates duplicate storage and aligns with local-first workflow.

**Alternatives considered:** Export mirror (`.memory/` → `okf/`) — rejected as duplicate maintenance. GCP enrich/kcmd — rejected; user requires fully local operation.

<!-- harness-links:autogen -->
## Graph links

- [Project Context](../context/project.md)
- [`.gitignore` excluded from harness template](2026-05-20-gitignore-excluded-from-harness-template.md)
- [`.graphifyignore` included in harness template](2026-05-20-graphifyignore-included-in-harness-template.md)
- [Direct Shell/CLI Authentication Inheritance for Hooks](2026-05-21-direct-shell-cli-authentication-inheritance-for-hooks.md)
- [Dynamic Path Resolution for Global Hook Installations](2026-05-21-dynamic-path-resolution-for-global-hook-installations.md)
- [Cross-IDE harness parity via shared AGENTS.md and install script](2026-06-21-cross-ide-harness-parity.md)
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
