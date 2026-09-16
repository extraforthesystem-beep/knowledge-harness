---
type: Architectural Decision
title: Memory Authority — challenge before overriding project truth
description: .memory/ is project truth; conflict/bend requires keep/update/remove/add challenge; progress stays soft; topic recall on demand
tags:
  - decision
  - adr
  - authority
status: accepted
timestamp: "2026-07-28T00:00:00Z"
---

**Decision:** Adopt Memory Authority as harness policy. Hard truth (ADRs, feature body/contract, architecture context) may not be silently overwritten — on conflict, override, remove, or architecture-bend the agent must challenge (`keep / update / remove / add`). Soft ops (progress, frontmatter status/priority, session-end hooks) sync without ceremony. Topic recall over `.memory/` is on demand (domains → keyword search); session inject stays progress-only. Code wins for runtime; memory wins for decided intent until the user overrides.

**Why:** Long-lived projects fail when agents follow a new command and bend ADRs without pushback. Dogfooded in Trade Profit (idea 3), S1–S5 PASS 2026-07-28.

**Alternatives considered:** Ask before every memory write — rejected (breaks hooks and end-of-session sync). Fatten session inject with all related ADRs — rejected (token budget). Bundle session-recall plugins into harness core — rejected (wrong layer; out of scope).

**Does not reverse:** OKF-native store, lean inject/token ablation, cross-IDE parity, no agent-loop in core, platform hooks.

**Honest limit:** Markdown policy is soft enforcement — agents can ignore it; Authority still defines correct behavior.

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
- [Lazy-code ladder — three squeezers, graphify reuse, OKF debt ledger](2026-09-07-lazy-code-ladder-three-squeezers.md)
- [Mechanical ADR append-only hook](2026-09-16-mechanical-adr-append-only-hook.md)
- [Lazy Code Ladder](../meta/lazy-code.md)
- [Harness Router](../meta/router.md)
- [SRE Memory Routing](../meta/sre-routing.md)
- [Session Progress](../progress/status.md)
<!-- /harness-links:autogen -->
