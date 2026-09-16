---
description: Alias — usually automatic via hooks; manual refresh via /memory-sync step 2.
---

Usually automatic via session-end hooks. For manual refresh, run step 2 of `/memory-sync`:

```bash
python scripts/harness-sync.py
```

Optionally skip graphify: `python scripts/harness-sync.py --skip-graphify`
