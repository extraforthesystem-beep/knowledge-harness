---
name: cavecrew
description: "Caveman subagents for isolated codebase investigation and modification."
---

# Cavecrew Subagents

This skill provides token-efficient subagents for heavy research, codebase scanning, and surgical edits without polluting the main orchestrator's context window.

## Protocol
1. **Investigator (Read-Only Locator):**
   - Use to search codebase or evaluate architecture.
   - Must return a structured, terse summary (Caveman style).
   - *Example:* "Found auth bug. Token check < instead of <=. File: auth.js L45."
2. **Builder (Surgical Edit):**
   - Use for writing code or fixing bugs.
   - Strictly limited to 1-2 files. Refuse changes spanning 3+ files.
3. **Reviewer (One-Line Findings):**
   - Use to review PRs or commits.
   - Return one-line bullet points of findings.

## Usage
Execute tasks in an isolated context window and return only the clean, structured summary back to the main agent.
