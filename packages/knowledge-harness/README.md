# knowledge-harness

Cross-IDE installer for the OKF Knowledge Harness — like [`npx skills`](https://skills.sh) but for `.memory/` slash commands and hooks.

## One-liner (any IDE / any project)

```bash
# THIS project (run inside the repo)
kh install -p -y
# or shorthand:
kh -p

# Global IDE commands (Cursor / Claude / OpenCode / Antigravity)
kh install -g -y
# or:
kh -g
```

`kh` is linked from your local harness checkout (`npm link`). Do **not** run bare `install -p` — that is the macOS system tool.

OpenCode reset/reinstall:

```bash
npx knowledge-harness install -g -a opencode --reset-opencode -y
npx knowledge-harness install -p -a opencode --reset-opencode -y
```

## Commands

| CLI | Purpose |
|-----|---------|
| `install` | Deploy 6 slash commands + hooks to Claude, Cursor, Antigravity, OpenCode |
| `init` | Scaffold OKF `.memory/` in current project |
| `migrate` | Flat `PROGRESS.md` → OKF layout (python3) |
| `sync` | Regenerate `index.md` + `viz.html` |
| `detect` | Show which IDEs are installed |

## Options

```bash
npx knowledge-harness install -g -y                    # global, all detected agents
npx knowledge-harness install -p -y                    # current project only
npx knowledge-harness install -a cursor -a claude-code -y
npx knowledge-harness install -p -a opencode --reset-opencode -y
```

## OpenCode notes

- The installer now upgrades the legacy minimal `opencode.json` scaffold to the canonical one that includes `permission`.
- `--reset-opencode` removes only harness-managed OpenCode files before reinstalling them.
- For local-model memory sync, configure an OpenAI-compatible endpoint with `HARNESS_MEMORY_PROVIDER=openai-compatible`, `HARNESS_OPENAI_BASE_URL`, and `HARNESS_OPENAI_MODEL`.

## Daily slash commands

- `/memory-sync` — end of session (main)
- `/feature-add` — feature specs
- `/memory-migrate` — one-time legacy upgrade

## skills.sh

Also available as an agent skill:

```bash
npx skills add extraforthesystem-beep/knowledge-harness --skill knowledge-harness -g -y
```

## Develop

```bash
npm run bundle   # copy repo templates → assets/
node bin/knowledge-harness.js install -g -y
```
