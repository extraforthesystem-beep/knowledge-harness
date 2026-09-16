---
type: Architectural Decision
title: Hook scripts authenticate via parent session credentials
description: ADR from 2026-05-20
tags:
  - decision
  - adr
status: accepted
timestamp: "2026-05-20T00:00:00Z"
---

**Decision:** No separate API key configuration in hook scripts
**Why:** `sync-memory.js` and other hooks run as child processes of Claude CLI / Antigravity, inheriting session credentials from the parent process environment.
**Alternatives considered:** Hardcoding or env-var-referencing API keys in the hooks — rejected as redundant and a security risk.

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
- [Harness Router](../meta/router.md)
- [SRE Memory Routing](../meta/sre-routing.md)
- [Session Progress](../progress/status.md)
<!-- /harness-links:autogen -->
