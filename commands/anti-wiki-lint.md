---
description: "Perform health checks over the Wiki to fix broken links, identify contradictions, and suggest research."
---

# LLM Wiki Linting

When the user runs `/project:anti-wiki-lint`, perform a health sweep on the `wiki/` folder:

1. **Verify Schema Rules**:
   Read `C:\Users\Grant\.gemini\antigravity\LLM_Wiki_Schema.md` to review the precise LINT operation checklist.

2. **Execute Lint**:
   Follow the 1-5 sequence from the schema.
   Scan `wiki/`, build the lint report and add contradictions to `wiki/meta/open-questions.md`. Write the log update to `wiki/log.md` with the `## [YYYY-MM-DD] lint | {summary}` snippet syntax.
