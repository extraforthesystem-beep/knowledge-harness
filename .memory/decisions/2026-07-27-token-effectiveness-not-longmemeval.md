---
type: Architectural Decision
title: Score harness on token-effectiveness ablation, not LongMemEval
description: "Harness competes as agentic project-memory efficiency, not chat-retrieval R@5"
tags: "[decision, adr, benchmark]"
status: accepted
timestamp: "2026-07-27T18:34:00Z"
---

**Decision:** Benchmark Knowledge Harness with (1) local inject/latency, (2) cited peer tables for context, and (3) with/without ablation on project questions. Do **not** claim LongMemEval R@5 or LoCoMo QA scores for `.memory/`.

**Why:** Harness is structured project memory (progress, ADRs, failures). agentmemory / claude-mem / Mem0 / Letta are session or agent recall. Apples-to-apples scoreboard is tokens + time + hit-rate to answer project questions — measured ~97% fewer task tokens WITH vs WITHOUT.

**Alternatives considered:** Run LongMemEval against harness — rejected (wrong layer). Only cite competitor R@5 without ablation — rejected (doesn't prove harness improvement).

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
- [Memory Authority — challenge before overriding project truth](2026-07-28-memory-authority-challenge-protocol.md)
- [Lazy-code ladder — three squeezers, graphify reuse, OKF debt ledger](2026-09-07-lazy-code-ladder-three-squeezers.md)
- [Mechanical ADR append-only hook](2026-09-16-mechanical-adr-append-only-hook.md)
- [Lazy Code Ladder](../meta/lazy-code.md)
- [Harness Router](../meta/router.md)
- [SRE Memory Routing](../meta/sre-routing.md)
- [Session Progress](../progress/status.md)
<!-- /harness-links:autogen -->
