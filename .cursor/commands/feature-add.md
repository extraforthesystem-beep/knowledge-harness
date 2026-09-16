---
description: Add or update a feature spec under .memory/features/ with OKF frontmatter.
---

## Memory Authority

If the new/changed feature **body** conflicts with an existing decision or feature, stop and challenge (`keep / update / remove / add`) per [.memory/meta/memory-authority.md](../../.memory/meta/memory-authority.md). Frontmatter-only status/priority bumps are soft.

Run the ladder in `.memory/meta/lazy-code.md` before scaffolding a new feature file.

1. Slugify the feature name (kebab-case).
2. Create or update `.memory/features/<slug>.md` with frontmatter:

```yaml
---
type: Feature Spec
title: ...
description: ...
status: planned
priority: medium
depends_on: []
blocks: []
tags: [feature]
timestamp: <ISO8601>
---
```

3. Run `python scripts/harness-sync.py` to refresh index.

Confirm file path and index update.
