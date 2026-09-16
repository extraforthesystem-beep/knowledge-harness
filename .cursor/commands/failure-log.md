---
description: Append a FAIL-XXX entry to .memory/failures/log.md when a hypothesis fails verification.
---

When a fix or hypothesis fails SRE verification (after rollback attempt 3), **or** when the shell hook reports the same command failed 3×:

1. Read `.memory/failures/log.md`
2. Append a new entry:

```markdown
## FAIL-XXX: Title
- **Date:** YYYY-MM-DD
- **Hypothesis:** ...
- **Result:** Failed — ...
- **Lesson:** ...
```

3. Run `python scripts/harness-sync.py`

Confirm FAIL id assigned.
