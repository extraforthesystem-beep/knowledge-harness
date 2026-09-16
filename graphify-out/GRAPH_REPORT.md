# Graph Report - .  (2026-05-17)

## Corpus Check
- Corpus is ~47,546 words - fits in a single context window. You may not need a graph.

## Summary
- 139 nodes · 224 edges · 13 communities detected
- Extraction: 79% EXTRACTED · 21% INFERRED · 0% AMBIGUOUS · INFERRED: 46 edges (avg confidence: 0.62)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Notebook Library Management|Notebook Library Management]]
- [[_COMMUNITY_Authentication Management|Authentication Management]]
- [[_COMMUNITY_Browser Session Handling|Browser Session Handling]]
- [[_COMMUNITY_Cleanup Management|Cleanup Management]]
- [[_COMMUNITY_Environment Setup|Environment Setup]]
- [[_COMMUNITY_Browser Utilities|Browser Utilities]]
- [[_COMMUNITY_Script Runner|Script Runner]]
- [[_COMMUNITY_Initialization|Initialization]]
- [[_COMMUNITY_Configuration|Configuration]]
- [[_COMMUNITY_Browser Utils Rationale 24|Browser Utils Rationale 24]]
- [[_COMMUNITY_Browser Utils Rationale 47|Browser Utils Rationale 47]]
- [[_COMMUNITY_Browser Utils Rationale 69|Browser Utils Rationale 69]]
- [[_COMMUNITY_Browser Utils Rationale 93|Browser Utils Rationale 93]]

## God Nodes (most connected - your core abstractions)
1. `NotebookLibrary` - 18 edges
2. `AuthManager` - 15 edges
3. `BrowserFactory` - 15 edges
4. `StealthUtils` - 15 edges
5. `BrowserSession` - 13 edges
6. `ask_notebooklm()` - 9 edges
7. `CleanupManager` - 9 edges
8. `main()` - 9 edges
9. `SkillEnvironment` - 9 edges
10. `main()` - 8 edges

## Surprising Connections (you probably didn't know these)
- `Ask a question in this session          Args:             question: The quest` --uses--> `StealthUtils`  [INFERRED]
  skills\notebooklm\scripts\browser_session.py → skills\notebooklm\scripts\browser_utils.py
- `ask_notebooklm()` --calls--> `launch_persistent_context()`  [INFERRED]
  skills\notebooklm\scripts\ask_question.py → skills\notebooklm\scripts\browser_utils.py
- `ask_notebooklm()` --calls--> `human_type()`  [INFERRED]
  skills\notebooklm\scripts\ask_question.py → skills\notebooklm\scripts\browser_utils.py
- `ask_notebooklm()` --calls--> `random_delay()`  [INFERRED]
  skills\notebooklm\scripts\ask_question.py → skills\notebooklm\scripts\browser_utils.py
- `Ask a question to NotebookLM      Args:         question: Question to ask` --uses--> `NotebookLibrary`  [INFERRED]
  skills\notebooklm\scripts\ask_question.py → skills\notebooklm\scripts\notebook_manager.py

## Communities

### Community 0 - "Notebook Library Management"
Cohesion: 0.1
Nodes (17): main(), main(), NotebookLibrary, Remove a notebook from the library          Args:             notebook_id: ID, Update notebook metadata          Args:             notebook_id: ID of notebo, Manages a collection of NotebookLM notebooks with metadata, Get a specific notebook by ID, List all notebooks in the library (+9 more)

### Community 1 - "Authentication Management"
Cohesion: 0.15
Nodes (17): ask_notebooklm(), Ask a question to NotebookLM      Args:         question: Question to ask, AuthManager, main(), Save browser state to disk, Save authentication metadata, Clear all authentication data          Returns:             True if cleared s, Perform re-authentication (clear and setup)          Args:             headle (+9 more)

### Community 2 - "Browser Session Handling"
Cohesion: 0.14
Nodes (13): BrowserSession, Get the current latest response text, Wait for and extract the new answer, Reset the chat by reloading the page, Represents a single persistent browser session for NotebookLM      Each sessio, Close this session and clean up resources, Get information about this session, Check if session has expired (default: 15 minutes) (+5 more)

### Community 3 - "Cleanup Management"
Cohesion: 0.18
Nodes (10): CleanupManager, main(), Get size of file or directory in bytes, Format size in human-readable form, Manages cleanup of NotebookLM skill data      Features:     - Preview what wi, Perform the actual cleanup          Args:             preserve_library: Keep, Print a preview of what will be cleaned, Command-line interface for cleanup management (+2 more)

### Community 4 - "Environment Setup"
Cohesion: 0.18
Nodes (9): main(), Get the correct Python executable to use, Run a script with the virtual environment, Get instructions for manual activation, Main entry point for environment setup, Manages skill-specific virtual environment, Ensure virtual environment exists and is set up, Check if we're already running in the skill's venv (+1 more)

### Community 5 - "Browser Utilities"
Cohesion: 0.33
Nodes (7): Ask a question in this session          Args:             question: The quest, human_type(), _inject_cookies(), launch_persistent_context(), random_delay(), Browser Utilities for NotebookLM Skill Handles browser launching, stealth featu, realistic_click()

### Community 6 - "Script Runner"
Cohesion: 0.47
Nodes (5): ensure_venv(), get_venv_python(), main(), Get the virtual environment Python executable, Ensure virtual environment exists

### Community 7 - "Initialization"
Cohesion: 0.67
Nodes (2): ensure_venv_and_run(), Ensure virtual environment exists and run the requested script.     This is cal

### Community 8 - "Configuration"
Cohesion: 1.0
Nodes (1): Configuration for NotebookLM Skill Centralizes constants, selectors, and paths

### Community 9 - "Browser Utils Rationale 24"
Cohesion: 1.0
Nodes (1): Launch a persistent browser context with anti-detection features         and co

### Community 10 - "Browser Utils Rationale 47"
Cohesion: 1.0
Nodes (1): Inject cookies from state.json if available

### Community 11 - "Browser Utils Rationale 69"
Cohesion: 1.0
Nodes (1): Type with human-like speed

### Community 12 - "Browser Utils Rationale 93"
Cohesion: 1.0
Nodes (1): Click with realistic movement

## Knowledge Gaps
- **41 isolated node(s):** `Check if session has expired (default: 15 minutes)`, `Browser Utilities for NotebookLM Skill Handles browser launching, stealth featu`, `Factory for creating configured browser contexts`, `Launch a persistent browser context with anti-detection features         and co`, `Inject cookies from state.json if available` (+36 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Configuration`** (2 nodes): `Configuration for NotebookLM Skill Centralizes constants, selectors, and paths`, `config.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Browser Utils Rationale 24`** (1 nodes): `Launch a persistent browser context with anti-detection features         and co`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Browser Utils Rationale 47`** (1 nodes): `Inject cookies from state.json if available`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Browser Utils Rationale 69`** (1 nodes): `Type with human-like speed`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Browser Utils Rationale 93`** (1 nodes): `Click with realistic movement`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `NotebookLibrary` connect `Notebook Library Management` to `Authentication Management`?**
  _High betweenness centrality (0.199) - this node is a cross-community bridge._
- **Why does `Ask a question to NotebookLM      Args:         question: Question to ask` connect `Authentication Management` to `Notebook Library Management`, `Browser Session Handling`?**
  _High betweenness centrality (0.189) - this node is a cross-community bridge._
- **Why does `StealthUtils` connect `Browser Session Handling` to `Authentication Management`, `Browser Utilities`?**
  _High betweenness centrality (0.135) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `NotebookLibrary` (e.g. with `Ask a question to NotebookLM      Args:         question: Question to ask` and `main()`) actually correct?**
  _`NotebookLibrary` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `AuthManager` (e.g. with `Ask a question to NotebookLM      Args:         question: Question to ask` and `BrowserFactory`) actually correct?**
  _`AuthManager` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `BrowserFactory` (e.g. with `Ask a question to NotebookLM      Args:         question: Question to ask` and `AuthManager`) actually correct?**
  _`BrowserFactory` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `StealthUtils` (e.g. with `Ask a question to NotebookLM      Args:         question: Question to ask` and `BrowserSession`) actually correct?**
  _`StealthUtils` has 13 INFERRED edges - model-reasoned connections that need verification._