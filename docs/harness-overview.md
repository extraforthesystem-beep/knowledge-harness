# Knowledge Harness Overview

This document explains the Knowledge Harness as a system: what it is, why it exists, how it updates itself over time, and how its parts fit together across IDEs. It is intentionally not a step-by-step installation guide.

For setup and command installation, see `packages/knowledge-harness/README.md` and `CROSS-IDE.md`.

## What the harness is

The Knowledge Harness is a local-first project memory system for coding agents. It gives multiple IDEs and agent surfaces a shared way to:

- keep durable project context in source control
- track progress, decisions, and feature intent
- hand work across tools without rewriting context
- keep discovery separate from memory
- stay lightweight enough to inject into sessions repeatedly

At its core, the harness treats `.memory/` as the project's long-lived knowledge store and treats agent-specific configs as thin adapters around that store.

## The core model

The harness separates project knowledge into two layers:

1. `.memory/` as the durable knowledge bundle
2. `graphify-out/` as the code discovery and exploration layer

This split is deliberate.

`.memory/` holds the human and agent working context:

- `index.md` as the entry point
- `progress/status.md` for done, in-progress, and next work
- `context/project.md` for stack, phase, and key paths
- `decisions/` for ADR-style architectural choices
- `domains/` (optional) for topic routers when ADR count is high
- `features/` for feature-specific intent and status
- `failures/log.md` for failed hypotheses and retry prevention
- `viz.html` as a browsable knowledge view

`graphify-out/` is not the memory system itself. It is the discovery surface used to understand the codebase, answer structural questions, and reduce blind searching.

In short:

- `.memory/` answers "What are we doing and why?"
- `graphify-out/` answers "How does the codebase connect?"

## Design goals

The harness is built around a few stable goals:

- One knowledge source. The project should not maintain separate memory formats per IDE.
- Local-first operation. The system should work without depending on hosted memory infrastructure.
- Cross-IDE parity. Cursor, Claude Code, Antigravity, and OpenCode should follow the same project logic.
- Thin adapters. Tool-specific files should be small and mostly route into the shared harness workflow.
- Low token overhead. The active memory surface should stay small enough for repeated session injection.
- Explicit history. Progress, decisions, features, and failures should be inspectable in git.

## Main parts

### `.memory/`

`.memory/` is an OKF-native bundle and the main source of truth for project memory. It stores structured concepts instead of one flat notes file.

This is where the harness records:

- current project context
- current and recent work
- architectural decisions
- active feature specs
- failure history and SRE routing hints

Because it is structured, agents can load only the parts they need instead of re-reading everything every time.

### Memory Authority

`.memory/` is project truth until the user overrides it. Agents must **challenge** before conflict, override, remove, or architecture-bend of hard truth (ADRs, feature body/contract, architecture context). Progress sync stays soft. Topic recall is on demand from domains and keyword search — session inject stays lean.

See `.memory/meta/memory-authority.md`.

### Routers

Files like `AGENTS.md`, `CLAUDE.md`, and related tool-specific router surfaces tell the agent how to behave in the repo.

They standardize the session loop:

1. read `.memory/` entry points first
2. consult decisions and features before broad search
3. use graph-based discovery before raw global search
4. sync memory after work

The router is the policy layer. `.memory/` is the content layer.

### Slash commands

The slash commands provide the operator workflow for maintaining the harness.

The most important ones are:

- `/memory-sync` for end-of-session syncing
- `/feature-add` for feature records
- `/memory-migrate` for upgrading legacy flat memory
- `/memory-compact` for keeping the active memory budget small (`scripts/memory-compact.py`)
- `/failure-log` for retry-safe debugging history

These commands are less about convenience and more about consistency. They make sure updates land in the expected places with the expected structure.

### Hooks

Hooks automate the routine parts of the memory lifecycle.

The current hook model centers on three jobs:

- session start: inject current progress context
- post-tool use: capture meaningful writes and installs into a journal
- session end: summarize, update memory, and run sync

The hook layer preserves continuity without requiring the user to manually narrate every session.

### `harness-sync`

`scripts/harness-sync.py` is the structural maintenance tool for the bundle. It regenerates derived artifacts such as:

- `.memory/index.md`
- `.memory/log.md`
- `.memory/viz.html`

It is the "rebuild derived state" step, not the whole memory system by itself.

### Graphify

Graphify is the discovery companion, not a replacement for `.memory/`.

It is used when the task becomes codebase exploration rather than project-memory recall. The harness explicitly prefers graph-backed exploration before blind grep-style searching because the goal is to recover structure, not just text matches.

## How the harness updates itself

The harness has two kinds of updates:

1. source updates
2. derived updates

### Source updates

These are edits to the durable knowledge itself:

- changing `progress/status.md`
- adding a decision file
- updating a feature spec
- changing project context
- appending a failure record

These updates carry meaning. They are the real memory of the project.

### Derived updates

These are regenerated views built from source memory:

- `index.md`
- `viz.html`
- `log.md`

Derived files should reflect the source files, not become a second source of truth.

## The update lifecycle

A typical lifecycle looks like this:

### 1. Session start

The agent reads the current memory entry points, especially:

- `.memory/index.md`
- `.memory/progress/status.md`
- `.memory/context/project.md` when stack or phase matters

If hooks are enabled, the current progress state can also be injected automatically at session start.

### 2. Active work

During work, the agent may:

- update feature state
- record new decisions
- change project context when the phase shifts
- use graph discovery for code exploration

If hooks are present, tool activity can also be journaled while the session is running.

### 3. Session sync

At the end of work, `/memory-sync` is the main normalization step. It is responsible for making sure the project memory reflects what actually happened in the session.

Conceptually, it does four things:

- updates durable memory files
- writes handoff context when needed
- regenerates derived bundle outputs
- checks whether memory size is still within budget

### 4. Ongoing maintenance

Over time, the harness also needs maintenance operations:

- `/memory-migrate` to upgrade older flat memory layouts
- `/memory-compact` to archive stale items and shrink active memory
- `harness-sync.py` to rebuild bundle views after structural changes

## Automatic vs manual behavior

The harness deliberately mixes automation with explicit user-controlled updates.

### Usually automatic

- injecting current progress at session start
- journaling some tool activity
- running end-of-session sync behavior where supported
- regenerating index and visualization artifacts

### Usually manual

- deciding what belongs in a feature spec
- writing architectural decisions
- deciding whether a failed attempt deserves a persistent failure record
- compacting memory when the active set grows too large

This balance matters. Fully automatic memory is noisy. Fully manual memory is forgotten. The harness tries to automate collection and structure, while leaving judgment to the user and agent.

## Cross-IDE behavior

The harness is meant to preserve one workflow across different agent surfaces.

The shared behavior is:

- same `.memory/` bundle
- same router intent
- same slash-command concepts
- same session rhythm

What changes from tool to tool is only the adapter layer:

- command install locations
- hook configuration format
- whether native lifecycle hooks exist
- whether some sync behavior must stay manual

This is why the project keeps the router logic small and keeps the actual knowledge in repo-tracked files.

## Why the OKF structure matters

The move to an OKF-style `.memory/` bundle changes the harness from a flat notebook into a structured knowledge system.

That matters because it:

- supports concept-level linking
- keeps related knowledge in stable files
- makes the memory navigable by both humans and agents
- reduces the need to stuff everything into one constantly growing progress file
- makes project memory easier to share, diff, review, and migrate

The harness is not just "notes for the agent." It is a lightweight project knowledge base.

## Why failures are first-class

The harness includes a failure log and SRE routing because repeated failed attempts waste both tokens and engineering time.

By storing failed hypotheses explicitly, the harness helps an agent answer:

- what has already been tried
- what should not be retried blindly
- what debugging path is preferred next

This turns memory from passive storage into active operational guidance.

## Token budget and compaction

The harness is designed for repeated session reuse, so active memory size matters.

That is why the system keeps a budget target for injected memory and includes compaction as a first-class operation. The goal is not to preserve every detail in the active surface. The goal is to keep the active context sharp while preserving the deeper record in structured files and archives.

In practice, this means:

- active progress should stay concise
- decisions should be split into separate files
- completed or superseded items should be archived when appropriate
- derived indexes should be regenerated from the remaining active set

## What this document is not

This document is not:

- an installation walkthrough
- a command reference
- a per-IDE configuration matrix
- a hook implementation deep dive

Those belong elsewhere:

- setup and command installation: `packages/knowledge-harness/README.md`
- cross-IDE deployment details: `CROSS-IDE.md`
- project memory policy: `AGENTS.md` and `CLAUDE.md`
- concrete project state: `.memory/`
- peer memory-tool benchmarks: `docs/memory-tool-comparison.md` (`python scripts/benchmark-harness.py --compare`)

## Short summary

The Knowledge Harness is a shared, local-first memory system for coding agents. It keeps project knowledge in `.memory/`, keeps code exploration in `graphify-out/`, uses routers and slash commands to enforce a consistent workflow, and uses hooks plus sync steps to keep the memory current without turning it into a noisy second codebase.

Its key idea is simple: one durable knowledge bundle, many agent surfaces, and a clear distinction between memory, discovery, and derived views.
