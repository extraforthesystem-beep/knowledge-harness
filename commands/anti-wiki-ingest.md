---
description: "Process a new raw document, extract knowledge, and compound it into the Wiki pages."
---

# LLM Wiki Ingestion

When the user runs `/project:anti-wiki-ingest <path_to_source>`, execute the following workflow:

1. **Verify Schema Rules**:
   Read `C:\Users\Grant\.gemini\antigravity\LLM_Wiki_Schema.md` to review the precise INGEST operation rules, YAML frontmatter schemas, and cross-linking constraints. You must follow the exact 10 steps listed there in the Ingest section.

2. **Execute Ingest**:
   Follow the 1-10 sequence from the schema.
   Particularly focus on generating `wiki/sources/...` files with the correct `Source Summary Format`, and splitting newly found entities into `wiki/entities/` and concepts into `wiki/concepts/`.
   Strictly enforce the Markdown and YAML formatting requirements.
