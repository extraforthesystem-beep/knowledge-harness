---
type: Project Context
title: Project Context
description: Current project stack, phase, branch, and key paths
tags:
  - context
  - harness
timestamp: "2026-09-07T14:03:42.638Z"
---

## Stack
OKF `.memory/` bundle (markdown + Obsidian), hooks, graphify for code discovery; pair with one deep-recall plugin (claude-mem or agentmemory) for semantic session history

## Current phase
Inject/sync hygiene + ADR hook lock + clutter delete. GitHub remote next; npm publish blocked on `npm login`.


## Active branch
Not set (will sync to GitHub later)

## Last updated
2026-09-07 14:03:42

## Key paths
- Entry point: [.memory/index.md](../index.md)
- Cross-IDE: [CROSS-IDE.md](../../CROSS-IDE.md)
- Install commands: `npx knowledge-harness install -g -y`
- Sync: `python scripts/harness-sync.py`
- Compact: `python scripts/memory-compact.py`
- Benchmark: `python scripts/benchmark-harness.py --compare` → results + comparison TSV
- Ablation: `python scripts/benchmark-ablation.py` → `docs/benchmark-ablation.tsv`
- Peer comparison: [docs/memory-tool-comparison.md](../../docs/memory-tool-comparison.md)
- Optional: `.memory/domains/` topic routers
- Graph view: [.memory/viz.html](../viz.html)
- Code discovery: `graphify-out/` — `/graphify query`
- Failures (SRE): [failures/log.md](../failures/log.md)

<!-- harness-links:autogen -->
## Graph links

- [Lazy Code Ladder](../meta/lazy-code.md)
- [Harness Router](../meta/router.md)
- [SRE Memory Routing](../meta/sre-routing.md)
- [Session Progress](../progress/status.md)
<!-- /harness-links:autogen -->
