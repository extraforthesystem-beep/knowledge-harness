import { spawnSync } from "node:child_process";
import path from "node:path";
import { detectAgents, listAgentIds } from "./agents.js";
import { installHarness } from "./install.js";
import { initMemory } from "./init.js";
import { printDetect } from "./detect.js";
import { assetsDir, pathExists } from "./paths.js";

function usage() {
  return `knowledge-harness — cross-IDE OKF memory harness (like npx skills for .memory/)

Usage (from any project directory):
  kh install -p -y              Install into THIS project
  kh install -g -y              Install global IDE commands
  kh -p                         Shorthand → install -p -y
  kh -g                         Shorthand → install -g -y

  kh init                       Scaffold .memory/ OKF bundle
  kh migrate [--dry-run]        Flat → OKF migration (needs python3)
  kh sync                       Regenerate index/viz (needs python3)
  kh detect                     List detected IDEs

Install options:
  -g, --global          Install to user home (default)
  -p, --project         Install to current project only
  -a, --agent <id>      Target agent (repeatable): ${listAgentIds().join(", ")}
  --reset-opencode      Remove harness-managed OpenCode files before reinstall
  -y, --yes             Non-interactive
  --all                 All known agents (same as -a '*')

Examples:
  cd ~/Data/my-app && kh install -p -y
  kh init && kh install -p -y

Note: bare \`install -p\` is the macOS system tool — use \`kh install -p -y\` instead.
`;
}

function parseArgs(argv) {
  let args = [...argv];
  // Shorthand: kh -p / kh -g → install -p -y / install -g -y
  if (args[0] === "-p" || args[0] === "--project") {
    args = ["install", "-p", "-y", ...args.slice(1)];
  } else if (args[0] === "-g" || args[0] === "--global") {
    args = ["install", "-g", "-y", ...args.slice(1)];
  }

  const cmd = args.shift() || "help";
  const opts = {
    global: true,
    project: false,
    yes: false,
    all: false,
    agents: [],
    resetOpenCode: false,
    dryRun: false,
  };
  while (args.length) {
    const a = args.shift();
    if (a === "-g" || a === "--global") opts.global = true;
    else if (a === "-p" || a === "--project") {
      opts.project = true;
      opts.global = false;
    } else if (a === "-y" || a === "--yes") opts.yes = true;
    else if (a === "--all") opts.all = true;
    else if (a === "--reset-opencode") opts.resetOpenCode = true;
    else if (a === "--dry-run") opts.dryRun = true;
    else if (a === "-a" || a === "--agent") opts.agents.push(args.shift());
    else if (a === "-h" || a === "--help") return { cmd: "help", opts };
    else throw new Error(`Unknown flag: ${a}`);
  }
  if (opts.all) opts.agents = ["*"];
  if (!opts.agents.length) opts.agents = detectAgents().length ? detectAgents() : ["*"];
  return { cmd, opts };
}

function runPython(scriptName, extraArgs = []) {
  const local = path.join(process.cwd(), "scripts", scriptName);
  const bundled = path.join(assetsDir(), "scripts", scriptName);
  const script = pathExists(local) ? local : pathExists(bundled) ? bundled : null;
  if (!script) {
    console.error(`Missing ${scriptName}. Run: npx knowledge-harness install -p -y`);
    process.exit(1);
  }
  const py = process.platform === "win32" ? "python" : "python3";
  const r = spawnSync(py, [script, ...extraArgs], { stdio: "inherit" });
  process.exit(r.status ?? 1);
}

export function main(argv = process.argv.slice(2)) {
  try {
    const { cmd, opts } = parseArgs(argv);
    switch (cmd) {
      case "install":
      case "i":
        installHarness({
          scope: opts.global ? "global" : "project",
          agents: opts.agents,
          yes: opts.yes,
          project: opts.project,
          resetOpenCode: opts.resetOpenCode,
        });
        break;
      case "init":
        initMemory();
        break;
      case "migrate":
        runPython("migrate-memory-to-okf.py", opts.dryRun ? ["--dry-run"] : []);
        break;
      case "sync":
        runPython("harness-sync.py", ["--skip-graphify"]);
        break;
      case "detect":
        printDetect();
        break;
      case "help":
      default:
        console.log(usage());
        break;
    }
  } catch (err) {
    console.error(err.message || err);
    process.exit(1);
  }
}
