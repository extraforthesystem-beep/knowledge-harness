---
description: Scaffold OKF-native .memory/ bundle for a new project.
---

**Upgrading an existing flat harness?** Use `/memory-migrate` instead — do not overwrite with a blank scaffold.

Interview the user, then create the OKF layout:

```
.memory/
├── context/project.md
├── progress/status.md
├── decisions/
├── features/.gitkeep
└── meta/
    ├── memory-authority.md   ← seed from templates/memory/
    ├── router.md
    ├── sre-routing.md
    └── lazy-code.md
```

Each concept file needs YAML frontmatter with `type` (Project Context, Session Progress, Feature Spec, Architectural Decision).

**Meta seeds:** Copy all of `templates/memory/*.md` (or package `assets/memory/*.md`) into `.memory/meta/` — at minimum `memory-authority.md`, `router.md`, `sre-routing.md`, and `lazy-code.md`. Prefer `npx knowledge-harness init` (or `kh -p` to backfill missing seeds on an existing `.memory/`).

After setup, run: `python scripts/harness-sync.py`

Confirm: "OKF memory initialized. Read `.memory/index.md` to start. Meta seeds: `.memory/meta/{memory-authority,router,sre-routing,lazy-code}.md`."
