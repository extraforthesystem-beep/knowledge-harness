---
type: Feature Spec
title: Mega Harness OKF Integration
description: OKF-native .memory/ bundle with graphify code discovery and harness-sync tooling
status: done
priority: high
depends_on: "[]"
blocks: "[]"
tags: "[harness, okf, graphify]"
timestamp: "2026-06-21T00:00:00Z"
---

## What it does
- Evolves `.memory/` in place into an OKF knowledge bundle (frontmatter, concept linking, index.md, viz.html)
- Keeps harness operational patterns: hooks, slash commands, token budget, PROGRESS workflow
- Adds `scripts/migrate-memory-to-okf.py` and `scripts/harness-sync.py` for local sync (no GCP)
- Uses graphify as the separate codebase discovery layer

## Constraints
- Local-only OKF: `reference-agent visualize` only; no enrich/kcmd/kcagent
- Backward compat: flat files archived to `.memory/_legacy/`
- Token budget target remains <500 tokens for session injection

## Definition of done
- [x] Migration script converts flat `.memory/` to OKF layout
- [x] harness-sync regenerates index, log, viz.html
- [x] CLAUDE.md and AGENTS.md updated to OKF-first router
- [x] Harness.md slash command bodies updated via templates/commands/
- [x] Cross-IDE install script and CROSS-IDE.md

<!-- harness-links:autogen -->
## Graph links

- [Project Context](../context/project.md)
- [Harness Router](../meta/router.md)
- [SRE Memory Routing](../meta/sre-routing.md)
- [Session Progress](../progress/status.md)
<!-- /harness-links:autogen -->
