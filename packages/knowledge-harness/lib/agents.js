import os from "node:os";
import path from "node:path";
import { expandHome, pathExists } from "./paths.js";

/** Open agent registry — mirrors skills.sh agent IDs where possible. */
export const AGENTS = {
  "claude-code": {
    label: "Claude Code",
    detect: () =>
      pathExists(expandHome("~/.claude")) ||
      pathExists(path.join(os.homedir(), ".claude")),
    targets: (scope, cwd) => {
      const t = [];
      if (scope === "global") {
        t.push({ kind: "commands", path: expandHome("~/.claude/commands") });
        t.push({ kind: "hooks", path: expandHome("~/.claude/hooks") });
      } else {
        t.push({ kind: "commands", path: path.join(cwd, ".claude/commands") });
      }
      return t;
    },
  },
  cursor: {
    label: "Cursor",
    detect: () =>
      pathExists(expandHome("~/.cursor")) ||
      pathExists(path.join(cwd(), ".cursor")),
    targets: (scope, cwd) => {
      const t = [];
      if (scope === "global") {
        t.push({ kind: "commands", path: expandHome("~/.cursor/commands") });
      }
      t.push({ kind: "commands", path: path.join(cwd, ".cursor/commands") });
      t.push({ kind: "rules", path: path.join(cwd, ".cursor/rules") });
      t.push({ kind: "hooks-json", path: path.join(cwd, ".cursor/hooks.json") });
      t.push({ kind: "hooks", path: path.join(cwd, ".cursor/hooks") });
      return t;
    },
  },
  opencode: {
    label: "OpenCode",
    detect: () => pathExists(expandHome("~/.config/opencode")),
    targets: (scope, cwd) => {
      const t = [];
      if (scope === "global") {
        t.push({ kind: "commands", path: expandHome("~/.config/opencode/commands") });
        t.push({ kind: "opencode-agents", path: expandHome("~/.config/opencode/AGENTS.md") });
      }
      t.push({ kind: "opencode-json", path: path.join(cwd, "opencode.json") });
      return t;
    },
  },
  antigravity: {
    label: "Antigravity IDE",
    detect: () =>
      pathExists(expandHome("~/.gemini/antigravity")) ||
      pathExists(expandHome("~/.gemini/config")),
    targets: (scope) => {
      if (scope !== "global") return [];
      return [
        {
          kind: "commands",
          path: expandHome("~/.gemini/antigravity/global_workflows"),
        },
        {
          kind: "commands",
          path: expandHome("~/.gemini/config/global_workflows"),
        },
      ];
    },
  },
};

function cwd() {
  return process.cwd();
}

export function listAgentIds() {
  return Object.keys(AGENTS);
}

export function detectAgents() {
  return listAgentIds().filter((id) => AGENTS[id].detect());
}

export function resolveAgents(requested) {
  if (!requested?.length || requested.includes("*")) {
    const detected = detectAgents();
    return detected.length ? detected : listAgentIds();
  }
  const unknown = requested.filter((id) => !AGENTS[id]);
  if (unknown.length) {
    throw new Error(
      `Unknown agent(s): ${unknown.join(", ")}. Valid: ${listAgentIds().join(", ")}`
    );
  }
  return requested;
}
