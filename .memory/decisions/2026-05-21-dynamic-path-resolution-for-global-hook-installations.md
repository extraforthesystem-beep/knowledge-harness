---
type: Architectural Decision
title: Dynamic Path Resolution for Global Hook Installations
description: ADR from 2026-05-21
tags:
  - decision
  - adr
status: accepted
timestamp: "2026-05-21T00:00:00Z"
---

**Status:** accepted
**Decision:** Global hook configurations (`hooks.json` / `settings.json`) should resolve system home directories dynamically rather than using hardcoded absolute file system paths.
**Why:** Improves cross-platform and multi-user compatibility, ensuring that the unified harness remains functional when run across different machines or OS flavors (Windows/macOS/Linux) without requiring manual setup edits.
**Alternatives considered:** Hardcoding machine-specific absolute user paths — rejected because it breaks portability and repo-level sharing.

<!-- harness-links:autogen -->
## Graph links

- [Project Context](../context/project.md)
- [`.gitignore` excluded from harness template](2026-05-20-gitignore-excluded-from-harness-template.md)
- [`.graphifyignore` included in harness template](2026-05-20-graphifyignore-included-in-harness-template.md)
- [Direct Shell/CLI Authentication Inheritance for Hooks](2026-05-21-direct-shell-cli-authentication-inheritance-for-hooks.md)
- [Cross-IDE harness parity via shared AGENTS.md and install script](2026-06-21-cross-ide-harness-parity.md)
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
