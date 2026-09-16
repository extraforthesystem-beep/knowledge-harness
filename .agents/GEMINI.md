# Antigravity project router

> Mirrors [AGENTS.md](../AGENTS.md). Antigravity reads `.agents/GEMINI.md` as local source of truth when present.

See [AGENTS.md](../AGENTS.md) for the full Knowledge Harness router.

**OKF bundle:** `.memory/` — start at `.memory/index.md`
**Code discovery:** `graphify-out/` — use `/graphify query`
**Writing code:** ladder in `.memory/meta/lazy-code.md` — `graphify query` for reuse first; caveman for prose, ponytail for code
**End of session:** `/memory-sync` (daily) · `/feature-add` when adding features
**Legacy upgrade:** `/memory-migrate` if flat `.memory/PROGRESS.md` exists (no `context/project.md`)

Cross-IDE details: [CROSS-IDE.md](../CROSS-IDE.md)
