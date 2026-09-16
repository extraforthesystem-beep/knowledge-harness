---
description: "Search and synthesize answers over the LLM Wiki using the index as a token-saving routing layer."
---

# LLM Wiki Querying

When the user runs `/project:anti-wiki-query <question>`, execute the following workflow to save tokens:

1. **Verify Schema Rules**:
   Read `C:\Users\Grant\.gemini\antigravity\LLM_Wiki_Schema.md` to review the precise QUERY operation sequence mapping out exact behaviors.

2. **Execute Query**:
   Follow the 1-5 sequence from the schema.
   Read `wiki/index.md` first, isolate relevant targets, read those, and synthesize with proper `[[wikilinks]]`. Always remember to offer to file substantive insights into `wiki/comparisons/` or direct page files.
