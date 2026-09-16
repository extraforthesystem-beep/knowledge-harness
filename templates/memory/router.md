---
type: Meta
title: Harness Router
description: Harness slash commands and agent workflow
tags:
  - meta
  - harness
timestamp: "2026-07-28T00:00:00Z"
---

# Harness slash commands

**Daily:** `/feature-add` · `/memory-sync` (end of session — progress, ADRs, handoff, index/viz)

**One-time:** `/memory-migrate` · `/memory-init`

**Rare:** `/memory-compact` · `/failure-log`

**Aliases → `/memory-sync` (not installed):** `/handoff` · `/extract-memory` · `/compact` · `/harness-sync`

# Agent workflow

1. Read `.memory/index.md` then `progress/status.md`
2. Topic recall on demand → [Memory Authority](memory-authority.md); for features → `features/<slug>.md`; for architecture → `decisions/` (or `domains/` topic map first if present)
3. Hard truth conflict/bend → challenge before write; progress is soft
4. For code exploration → `/graphify query` before grep
5. For writing code → [lazy-code.md](lazy-code.md) (`graphify query` reuse first)
6. After work → run `/memory-sync`
