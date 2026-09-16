# Knowledge Harness router

> **Cross-IDE:** Same harness works in Claude Code, Antigravity, Cursor, and OpenCode. See [CROSS-IDE.md](CROSS-IDE.md). Install: `npx knowledge-harness install -g -y`

Before starting any task:
1. Read [.memory/index.md](.memory/index.md) — entry point, features, token budget
2. Read [.memory/progress/status.md](.memory/progress/status.md) — done / in-progress / next
3. Read [.memory/context/project.md](.memory/context/project.md) if stack or phase matters

When implementing a feature → follow links from index to `.memory/features/<slug>.md`
When making an architectural decision → read `.memory/decisions/` first; add a new concept file (do not edit old ADRs)
When exploring the codebase → use `/graphify query` before grepping files
When writing code → ladder in `.memory/meta/lazy-code.md`: `graphify query` for reuse first; caveman for prose, ponytail for code
When debugging or retrying a fix → read `.memory/failures/log.md` first (SRE micro-loop)
When using `sre-architect` skill → follow `.memory/meta/sre-routing.md` retrieval order
When browsing knowledge → open `.memory/viz.html` or follow concept links in the bundle

After completing any work:
1. Run `/memory-sync` — updates progress, ADRs, context, features, handoff, and regenerates index/viz

> **Memory Authority:** `.memory/` is project truth. On conflict/override/architecture-bend → challenge (keep/update/remove/add) before writing. Progress sync is soft. Topic recall on demand (domains → decisions/features/failures). See [.memory/meta/memory-authority.md](.memory/meta/memory-authority.md).
> **Search-First Guardrail:** Check `.memory/decisions/` and `.memory/features/` before global code search or major features.
> **OS-Tiered Memory:** Keep root instructions under 300 lines. Use scoped nested routers (e.g. `backend/AGENTS.md`) on demand.
> **OKF Format:** `.memory/` is an OKF knowledge bundle — every concept file needs YAML frontmatter with `type`.

## Slash commands

**Daily:** `/feature-add` (new/changed feature) · `/memory-sync` (end of session — does everything else)

**One-time:** `/memory-migrate` (flat legacy → OKF) · `/memory-init` (blank scaffold for new project)

**Rare:** `/memory-compact` (token budget over 500) · `/failure-log` (SRE failed hypothesis)

**Aliases → use `/memory-sync`:** `/handoff` · `/extract-memory` · `/compact` · `/harness-sync` (not installed — merged into `/memory-sync`)

**Optional:** Copy [`templates/loop/`](templates/loop/) into a project if you want a simple agent-loop policy file; skip for normal memory-only use.
