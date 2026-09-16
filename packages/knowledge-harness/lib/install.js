import fs from "node:fs";
import path from "node:path";
import {
  assetsDir,
  copyFile,
  ensureDir,
  pathExists,
  removeIfExists,
} from "./paths.js";
import { AGENTS, resolveAgents } from "./agents.js";
import { seedMetaFiles } from "./seed-meta.js";

export const ACTIVE_CMDS = [
  "memory-sync.md",
  "feature-add.md",
  "memory-migrate.md",
  "memory-init.md",
  "memory-compact.md",
  "failure-log.md",
];

export const REMOVED_CMDS = [
  "handoff.md",
  "extract-memory.md",
  "compact.md",
  "harness-sync.md",
];

const OPENCODE_AGENTS = `# Global Knowledge Harness defaults

Applies to all OpenCode sessions alongside project \`AGENTS.md\`.

**Daily:** \`/feature-add\` · \`/memory-sync\`
**One-time:** \`/memory-migrate\` · \`/memory-init\`
**Rare:** \`/memory-compact\` · \`/failure-log\`

Before any task in a harness project:
1. Read \`.memory/index.md\` if present
2. Read \`.memory/progress/status.md\` (or run \`/memory-migrate\` if flat \`PROGRESS.md\` exists)
3. Follow Memory Authority (\`.memory/meta/memory-authority.md\`) — challenge before overriding hard truth
4. Use \`/graphify query\` for codebase exploration
5. When writing code, follow \`.memory/meta/lazy-code.md\` (\`graphify query\` reuse first; caveman prose, ponytail code)
6. Run \`/memory-sync\` after updating memory

Install: \`kh install -g -y\`

Project rules take precedence. See project \`CROSS-IDE.md\`.
`;

const LEGACY_OPENCODE_JSON = {
  $schema: "https://opencode.ai/config.json",
  instructions: ["AGENTS.md", "CROSS-IDE.md", ".memory/index.md"],
};

const OPENCODE_JSON = {
  ...LEGACY_OPENCODE_JSON,
  permission: {
    "*": "allow",
  },
};

const MANAGED_OPENCODE_JSONS = [LEGACY_OPENCODE_JSON, OPENCODE_JSON];

function stableJson(value) {
  if (Array.isArray(value)) {
    return `[${value.map((item) => stableJson(item)).join(",")}]`;
  }
  if (value && typeof value === "object") {
    return `{${Object.keys(value)
      .sort()
      .map((key) => `${JSON.stringify(key)}:${stableJson(value[key])}`)
      .join(",")}}`;
  }
  return JSON.stringify(value);
}

function readJsonIfExists(file) {
  if (!pathExists(file)) return null;
  try {
    return JSON.parse(fs.readFileSync(file, "utf8"));
  } catch {
    return null;
  }
}

function opencodeJsonState(file) {
  const parsed = readJsonIfExists(file);
  if (!parsed) return "absent";
  const serialized = stableJson(parsed);
  if (serialized === stableJson(OPENCODE_JSON)) return "canonical";
  if (MANAGED_OPENCODE_JSONS.some((item) => stableJson(item) === serialized)) {
    return "managed-legacy";
  }
  return "custom";
}

function looksLikeHarnessProject(cwd) {
  return [
    path.join(cwd, "AGENTS.md"),
    path.join(cwd, "CROSS-IDE.md"),
    path.join(cwd, ".memory"),
    path.join(cwd, "scripts", "harness-sync.py"),
  ].some(pathExists);
}

function installOpenCodeJson(dest, log) {
  const state = opencodeJsonState(dest);
  if (state === "absent") {
    fs.writeFileSync(dest, JSON.stringify(OPENCODE_JSON, null, 2) + "\n", "utf8");
    log(`  [+] ${dest}`);
    return;
  }
  if (state === "managed-legacy") {
    fs.writeFileSync(dest, JSON.stringify(OPENCODE_JSON, null, 2) + "\n", "utf8");
    log(`  [~] ${dest} (upgraded to canonical scaffold)`);
    return;
  }
  if (state === "custom") {
    log(`  [~] ${dest} (preserved custom config)`);
  }
}

function resetOpenCodeTargets(targets, log) {
  for (const target of targets) {
    switch (target.kind) {
      case "commands":
        for (const name of [...ACTIVE_CMDS, ...REMOVED_CMDS]) {
          const file = path.join(target.path, name);
          if (pathExists(file)) {
            removeIfExists(file);
            log(`  [-] ${file}`);
          }
        }
        break;
      case "opencode-agents":
        if (
          pathExists(target.path) &&
          fs.readFileSync(target.path, "utf8").trim() === OPENCODE_AGENTS.trim()
        ) {
          removeIfExists(target.path);
          log(`  [-] ${target.path}`);
        } else if (pathExists(target.path)) {
          log(`  [~] ${target.path} (preserved custom global router)`);
        }
        break;
      case "opencode-json": {
        const state = opencodeJsonState(target.path);
        if (state === "canonical" || state === "managed-legacy") {
          removeIfExists(target.path);
          log(`  [-] ${target.path}`);
        } else if (state === "custom") {
          log(`  [~] ${target.path} (preserved custom config)`);
        }
        break;
      }
      default:
        break;
    }
  }
}

function installCommands(dest, log) {
  const cmdSrc = path.join(assetsDir(), "commands");
  ensureDir(dest);
  for (const f of ACTIVE_CMDS) {
    copyFile(path.join(cmdSrc, f), path.join(dest, f));
    log(`  [+] ${path.join(dest, f)}`);
  }
  for (const f of REMOVED_CMDS) {
    const p = path.join(dest, f);
    if (pathExists(p)) {
      removeIfExists(p);
      log(`  [-] ${p} (alias removed)`);
    }
  }
}

function installHooks(dest, log) {
  const hookSrc = path.join(assetsDir(), "hooks");
  if (!pathExists(hookSrc)) return;
  ensureDir(dest);
  for (const f of fs.readdirSync(hookSrc).filter((n) => n.endsWith(".js"))) {
    copyFile(path.join(hookSrc, f), path.join(dest, f));
    log(`  [+] ${path.join(dest, f)}`);
  }
}

function installCursorExtras(cwd, log) {
  const rulesSrc = path.join(assetsDir(), "rules", "knowledge-harness.mdc");
  if (pathExists(rulesSrc)) {
    const dest = path.join(cwd, ".cursor/rules/knowledge-harness.mdc");
    copyFile(rulesSrc, dest);
    log(`  [+] ${dest}`);
  }
  const hooksJsonSrc = path.join(assetsDir(), "hooks.json");
  const hooksDest = path.join(cwd, ".cursor/hooks.json");
  if (pathExists(hooksJsonSrc) && !pathExists(hooksDest)) {
    copyFile(hooksJsonSrc, hooksDest);
    log(`  [+] ${hooksDest}`);
  }
  installHooks(path.join(cwd, ".cursor/hooks"), log);
}

function installProjectRouters(cwd, log) {
  for (const name of ["AGENTS.md", "CLAUDE.md", "CROSS-IDE.md"]) {
    const src = path.join(assetsDir(), "routers", name);
    const dest = path.join(cwd, name);
    if (pathExists(src) && !pathExists(dest)) {
      copyFile(src, dest);
      log(`  [+] ${dest} (scaffold)`);
    }
  }
  const geminiSrc = path.join(assetsDir(), "routers", "GEMINI.md");
  const geminiDest = path.join(cwd, ".agents/GEMINI.md");
  if (pathExists(geminiSrc) && !pathExists(geminiDest)) {
    copyFile(geminiSrc, geminiDest);
    log(`  [+] ${geminiDest} (scaffold)`);
  }
}

export function installHarness(options) {
  const {
    scope = "global",
    agents: agentList,
    cwd = process.cwd(),
    yes = false,
    project = false,
    resetOpenCode = false,
    log = console.log,
  } = options;

  const resolvedScope = project ? "project" : scope;
  const includeProject = project || resolvedScope === "project";
  const agents = resolveAgents(agentList);
  log(`=== knowledge-harness install ===`);
  log(`Scope: ${resolvedScope} · Agents: ${agents.join(", ")}`);

  if (!yes && process.stdin.isTTY) {
    log("(pass -y to skip prompts in CI)");
  }

  for (const agentId of agents) {
    const agent = AGENTS[agentId];
    log(`\n${agent.label} (${agentId})`);
    const allowOpenCodeProjectConfig =
      agentId === "opencode" && looksLikeHarnessProject(cwd);
    let targets = agent.targets(resolvedScope, cwd);

    if (!includeProject) {
      targets = targets.filter((t) => {
        if (t.kind === "commands" && t.path.startsWith(cwd)) return false;
        if (["rules", "hooks-json", "hooks"].includes(t.kind))
          return false;
        if (t.kind === "opencode-json") return allowOpenCodeProjectConfig;
        return true;
      });
    }

    if (agentId === "opencode" && resetOpenCode) {
      log("  [~] Resetting harness-managed OpenCode files before reinstall");
      resetOpenCodeTargets(targets, log);
    }

    for (const target of targets) {
      switch (target.kind) {
        case "commands":
          installCommands(target.path, log);
          break;
        case "hooks":
          installHooks(target.path, log);
          break;
        case "opencode-agents":
          ensureDir(path.dirname(target.path));
          fs.writeFileSync(target.path, OPENCODE_AGENTS, "utf8");
          log(`  [+] ${target.path}`);
          break;
        case "opencode-json": {
          installOpenCodeJson(target.path, log);
          break;
        }
        default:
          break;
      }
    }

    if (agentId === "opencode" && !includeProject && !allowOpenCodeProjectConfig) {
      log("  [~] Skipped project opencode.json outside a harness project");
      log("      Re-run in a project root or use -p to scaffold project files.");
    }

    if (agentId === "opencode" && !includeProject && allowOpenCodeProjectConfig) {
      installProjectRouters(cwd, log);
    }

    if (agentId === "cursor" && includeProject) {
      installCursorExtras(cwd, log);
    }
  }

  if (includeProject) {
    log("\nProject routers");
    installProjectRouters(cwd, log);
  }

  // Seed missing meta playbooks when .memory/ already exists (project scope)
  if (includeProject && pathExists(path.join(cwd, ".memory"))) {
    log("\nMeta seeds (missing only)");
    const n = seedMetaFiles(cwd, log);
    if (n === 0) log("  [=] .memory/meta/ already complete");
  }

  // Copy sync scripts into project if missing (project scope only)
  const scriptsSrc = path.join(assetsDir(), "scripts");
  if (includeProject && pathExists(scriptsSrc)) {
    const scriptsDest = path.join(cwd, "scripts");
    ensureDir(scriptsDest);
    for (const f of fs.readdirSync(scriptsSrc)) {
      const dest = path.join(scriptsDest, f);
      if (!pathExists(dest)) {
        copyFile(path.join(scriptsSrc, f), dest);
        log(`  [+] ${dest}`);
      }
    }
  }

  log("\n=== Done ===");
  log(`Active commands: ${ACTIVE_CMDS.map((c) => c.replace(".md", "")).join(", ")}`);
  log("Daily: /feature-add · /memory-sync");
  log("Install into this project: kh -p");
  log("Install globally:          kh -g");
  log("Init project memory:       kh init");
}
