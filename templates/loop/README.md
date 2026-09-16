# Optional: agent loop template

> **Not part of the default harness.** Copy into a project only when you want ratchet-style agent loops. Everyone else can ignore this folder.

## Enable in a project

```bash
mkdir -p loop
cp path/to/harness/templates/loop/program.md loop/program.md
cp path/to/harness/templates/loop/results.tsv loop/results.tsv
```

Edit `loop/program.md`, then tell your agent:

```
Read loop/program.md and run one iteration of the loop.
```

## Files

| File | Who edits | Role |
|------|-----------|------|
| `program.md` | **You** | Goal, metric, budgets, editable/sealed paths |
| `results.tsv` | **Agent** (append) | Iteration log |
| `memory-loop.md` | Optional | Copy to `.memory/meta/loop.md` if you want OKF link |

Modify freely for your project. Core Knowledge Harness (`.memory/`, sync, routers) stays unchanged.
