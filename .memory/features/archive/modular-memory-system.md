---
type: Feature Spec
title: Modular Memory System
description: "Feature spec: Modular Memory System"
status: done
priority: high
depends_on: "[]"
blocks: "[]"
tags:
  - feature
  - harness
timestamp: "2026-05-20T18:27:37.245926+00:00"
---

## What it does
- Replaces monolithic FEATURES.md file with dedicated modular files under `.memory/features/`
- Updates project workspace routers (CLAUDE.md, AGENTS.md)
- Modifies the global `/feature-add` slash command logic for both Claude CLI and Gemini/Antigravity config paths
- Modernizes environment setup instructions and the PowerShell automated deployment script

## Constraints
- Avoid duplicate entries or duplicate files
- Maintain absolute backward compatibility for existing scripts by checking both hook schemas

## Edge cases
- Multi-word feature name with capital letters and special characters (must be slugified cleanly to kebab-case)
- Modifying an existing feature file should append or merge changes without losing old notes

## Definition of done
- [x] All files in active workspace and global configuration directories successfully updated
- [x] Environment setup documentation validated and updated
- [x] Folder structure and files verified via PowerShell diagnostic checks

<!-- harness-links:autogen -->
## Graph links

- [Project Context](../context/project.md)
- [Mega Harness OKF Integration](mega-harness.md)
- [Harness Router](../meta/router.md)
- [SRE Memory Routing](../meta/sre-routing.md)
- [Session Progress](../progress/status.md)
<!-- /harness-links:autogen -->
