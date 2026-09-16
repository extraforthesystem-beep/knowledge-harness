---
description: Archive superseded decisions and completed features to keep token budget lean.
---

1. Run `python scripts/memory-compact.py` — moves `status: superseded` ADRs and completed features older than 14d to archive/
2. Manually renumber any duplicate ADR numbers if found (see `formerly:` frontmatter on renumbered ADRs)
3. Run `python scripts/harness-sync.py`
4. Verify token budget in `.memory/index.md` is under 500 tokens

Confirm what was archived.
