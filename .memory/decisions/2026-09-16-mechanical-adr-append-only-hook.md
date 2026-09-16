---
type: Architectural Decision
title: Mechanical ADR append-only hook
description: "Session-start snapshot restores in-place edits to existing .memory/decisions/*.md; new ADR files stay allowed"
tags:
  - decision
  - adr
  - authority
status: accepted
timestamp: "2026-09-16T00:00:00Z"
---

**Decision:** Enforce Memory Authority append-only for **existing** ADR files with a hook. `inject-context.js` snapshots `.memory/decisions/*.md` (not `index.md`, not `archive/`) at session start into `.memory/.adr-snap/`. `capture-decisions.js` restores a file from that snapshot if an agent overwrites it, and injects a one-line challenge. New ADR filenames (absent from the snapshot) are allowed. Soft paths (progress, feature frontmatter, session-end sync) stay unlocked.

**Why:** The 2026-07-28 honest limit was "markdown is soft — agents can ignore it." User asked for a mechanical lock. Cursor has no pre-edit hook, so revert-after-write is the lock. Does not ask before every memory write (rejected in 2026-07-28).

**Does not reverse:** Challenge protocol, progress-as-soft, lean inject, no agent-loop in core.

**Limit:** Python `harness-sync.py` graph-link rewrites are not Cursor `afterFileEdit` events. If an IDE starts reporting those, compare nav-stripped bodies before revert.

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
- [Lazy-code ladder — three squeezers, graphify reuse, OKF debt ledger](2026-09-07-lazy-code-ladder-three-squeezers.md)
- [Lazy Code Ladder](../meta/lazy-code.md)
- [Harness Router](../meta/router.md)
- [SRE Memory Routing](../meta/sre-routing.md)
- [Session Progress](../progress/status.md)
<!-- /harness-links:autogen -->
