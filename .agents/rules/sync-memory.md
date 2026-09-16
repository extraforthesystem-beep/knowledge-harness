# Memory Sync Protocol

**Trigger:** At the conclusion of a session, completion of a major milestone, or when shifting context significantly.

## Execution Rules
1. **Never Overwrite Blindly:** Append to the `Decision Log` in `context-handoff.md` instead of deleting past entries.
2. **Format:** Use the established markdown table format in `context-handoff.md`:
   `| Date | Agent | Decision / Action | Rationale |`
3. **Be Terse:** Use Caveman principles to keep logs concise and token-efficient.
4. **Update Active Goals:** Modify the `Active Goals` section to reflect the current state of the project.
5. **Cross-Agent Awareness:** Always read `context-handoff.md` at the start of a session before asking the user for context they may have already provided to another agent (e.g., Claude Code).
