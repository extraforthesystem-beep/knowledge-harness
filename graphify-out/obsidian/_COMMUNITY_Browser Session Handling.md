---
type: community
cohesion: 0.14
members: 22
---

# Browser Session Handling

**Cohesion:** 0.14 - loosely connected
**Members:** 22 nodes

## Members
- [[.__init__()_1]] - code - skills\notebooklm\scripts\browser_session.py
- [[._initialize()]] - code - skills\notebooklm\scripts\browser_session.py
- [[._snapshot_latest_response()]] - code - skills\notebooklm\scripts\browser_session.py
- [[._wait_for_latest_answer()]] - code - skills\notebooklm\scripts\browser_session.py
- [[._wait_for_ready()]] - code - skills\notebooklm\scripts\browser_session.py
- [[.get_info()]] - code - skills\notebooklm\scripts\browser_session.py
- [[.is_expired()]] - code - skills\notebooklm\scripts\browser_session.py
- [[.reset()]] - code - skills\notebooklm\scripts\browser_session.py
- [[BrowserSession]] - code - skills\notebooklm\scripts\browser_session.py
- [[Check if session has expired (default 15 minutes)]] - rationale - skills\notebooklm\scripts\browser_session.py
- [[Close this session and clean up resources]] - rationale - skills\notebooklm\scripts\browser_session.py
- [[Get information about this session]] - rationale - skills\notebooklm\scripts\browser_session.py
- [[Get the current latest response text]] - rationale - skills\notebooklm\scripts\browser_session.py
- [[Human-like interaction utilities]] - rationale - skills\notebooklm\scripts\browser_utils.py
- [[Initialize a new browser session          Args             session_id Uniqu]] - rationale - skills\notebooklm\scripts\browser_session.py
- [[Initialize the browser session and navigate to NotebookLM]] - rationale - skills\notebooklm\scripts\browser_session.py
- [[Represents a single persistent browser session for NotebookLM      Each sessio]] - rationale - skills\notebooklm\scripts\browser_session.py
- [[Reset the chat by reloading the page]] - rationale - skills\notebooklm\scripts\browser_session.py
- [[StealthUtils]] - code - skills\notebooklm\scripts\browser_utils.py
- [[Wait for NotebookLM page to be ready]] - rationale - skills\notebooklm\scripts\browser_session.py
- [[Wait for and extract the new answer]] - rationale - skills\notebooklm\scripts\browser_session.py
- [[browser_session.py]] - code - skills\notebooklm\scripts\browser_session.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Browser_Session_Handling
SORT file.name ASC
```

## Connections to other communities
- 6 edges to [[_COMMUNITY_Browser Utilities]]
- 4 edges to [[_COMMUNITY_Authentication Management]]

## Top bridge nodes
- [[StealthUtils]] - degree 15, connects to 2 communities
- [[BrowserSession]] - degree 13, connects to 2 communities
- [[._initialize()]] - degree 6, connects to 2 communities
- [[._snapshot_latest_response()]] - degree 3, connects to 1 community
- [[._wait_for_latest_answer()]] - degree 3, connects to 1 community