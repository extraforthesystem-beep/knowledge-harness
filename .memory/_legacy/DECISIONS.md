# Architectural decisions

<!-- Append-only. Never rewrite or delete entries. -->

### 2026-05-20 `.gitignore` excluded from harness template
**Decision:** `.gitignore` is NOT part of the harness — it's framework/project-dependent
**Why:** The harness is a framework-agnostic memory/context system. Each project brings its own `.gitignore`.
**Alternatives considered:** Including a generic `.gitignore` in the harness — rejected because it would need overwriting per project anyway.

### 2026-05-20 `.graphifyignore` included in harness template
**Decision:** `.graphifyignore` IS part of the harness and should be deployed by the setup script
**Why:** Token efficiency during graphify scans is a harness-level concern (cost/context optimization), not framework-specific.
**Alternatives considered:** Leaving it as a manual step — rejected because it's universal to every project using the harness.

### 2026-05-20 Hook scripts authenticate via parent session credentials
**Decision:** No separate API key configuration in hook scripts
**Why:** `sync-memory.js` and other hooks run as child processes of Claude CLI / Antigravity, inheriting session credentials from the parent process environment.
**Alternatives considered:** Hardcoding or env-var-referencing API keys in the hooks — rejected as redundant and a security risk.

### 2026-05-21 Dynamic Path Resolution for Global Hook Installations
**Status:** accepted
**Decision:** Global hook configurations (`hooks.json` / `settings.json`) should resolve system home directories dynamically rather than using hardcoded absolute file system paths.
**Why:** Improves cross-platform and multi-user compatibility, ensuring that the unified harness remains functional when run across different machines or OS flavors (Windows/macOS/Linux) without requiring manual setup edits.
**Alternatives considered:** Hardcoding machine-specific absolute user paths — rejected because it breaks portability and repo-level sharing.

### 2026-05-21 Direct Shell/CLI Authentication Inheritance for Hooks
**Status:** accepted
**Decision:** Session End memory sync hooks should leverage session-native CLI environment authentication (or standard model aliases) rather than direct standalone fetch methods that require independent API keys.
**Why:** Detached background scripts often lose terminal-level API key variables or encounter token/auth issues. Aligning hooks directly to native CLI parameters prevents unexpected session termination failures.
**Alternatives considered:** Hardcoding proxy endpoints or isolated API key variables in local scripts — rejected as highly insecure and brittle.

