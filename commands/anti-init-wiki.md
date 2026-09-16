---
description: "Scaffold the LLM Wiki directory structure and metadata files at the root of the workspace."
---

# LLM Wiki Setup

When the user runs `/project:anti-init-wiki`, you must perform the following actions:

1. **Verify Schema Rules**:
   Read `C:\Users\Grant\.gemini\antigravity\LLM_Wiki_Schema.md` to ensure your operations match the global standards completely.

2. **Create Directories**:
   // turbo-all
   Create `raw/` and `raw/assets/` directories for immutable files.
   Create `wiki/` along with its subdirectories: `wiki/entities/`, `wiki/concepts/`, `wiki/sources/`, `wiki/comparisons/`, and `wiki/meta/`.

3. **Scaffold Metadata Files**:
   Create `wiki/index.md` with:
   ```markdown
   # Wiki Index
   
   Catalog of all synthesized knowledge.
   
   ## Entities
   
   ## Concepts
   
   ## Sources
   
   ```
   Create `wiki/log.md` with:
   ```markdown
   # Wiki Log
   
   Chronological record of Wiki interactions.
   
   ```
   Create `wiki/overview.md` with a placeholder high-level synthesis template.

4. **Confirmation**: Let the user know the persistent knowledge base is ready to ingest sources and that they should place files into `raw/`.
