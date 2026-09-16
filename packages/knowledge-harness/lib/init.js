import fs from "node:fs";
import path from "node:path";
import { ensureDir, pathExists } from "./paths.js";
import { seedMetaFiles } from "./seed-meta.js";

const NOW = new Date().toISOString();

function fm(type, title, extra = "") {
  return `---
type: ${type}
title: ${title}
description: ${title}
tags:
  - harness
timestamp: "${NOW}"
---
${extra}`;
}

export function initMemory(cwd = process.cwd(), log = console.log) {
  const memory = path.join(cwd, ".memory");
  if (pathExists(path.join(memory, "context/project.md"))) {
    log("OKF .memory/ already exists (.memory/context/project.md). Use: npx knowledge-harness migrate");
    return;
  }

  const dirs = [
    "context",
    "progress",
    "decisions",
    "domains",
    "features",
    "meta",
    "failures",
  ];
  for (const d of dirs) {
    ensureDir(path.join(memory, d));
  }

  fs.writeFileSync(
    path.join(memory, "context/project.md"),
    fm(
      "Project Context",
      "Project Context",
      "\n## Stack\n\n## Current phase\n\n## Key paths\n- Entry: `.memory/index.md`\n"
    ),
    "utf8"
  );

  fs.writeFileSync(
    path.join(memory, "progress/status.md"),
    fm(
      "Session Progress",
      "Session Progress",
      "\n# Progress\n\n## Done\n\n## In progress\n\n## Next\n"
    ),
    "utf8"
  );

  fs.writeFileSync(
    path.join(memory, "failures/log.md"),
    "# Failure Log\n\nAppend-only SRE failed hypotheses.\n",
    "utf8"
  );

  fs.writeFileSync(path.join(memory, "features/.gitkeep"), "", "utf8");
  fs.writeFileSync(path.join(memory, "domains/.gitkeep"), "", "utf8");
  fs.writeFileSync(
    path.join(memory, "domains/index.md"),
    `# Domain Maps

Add one markdown concept per topic area (e.g. \`auth.md\`, \`billing.md\`).
Each file needs YAML frontmatter with \`type: Domain Map\`.

\`harness-sync.py\` auto-discovers \`domains/*.md\` and links them here.
`,
    "utf8"
  );

  log("Meta seeds");
  seedMetaFiles(cwd, log, { createMeta: true });

  log("Created OKF .memory/ layout");
  log("Next: npx knowledge-harness sync  (or python3 scripts/harness-sync.py)");
}
