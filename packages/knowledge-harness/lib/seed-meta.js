import path from "node:path";
import { assetsDir, copyFile, ensureDir, pathExists } from "./paths.js";

/** Canonical meta playbooks seeded into `.memory/meta/` on init / project install. */
export const META_SEEDS = [
  "memory-authority.md",
  "router.md",
  "sre-routing.md",
  "lazy-code.md",
];

/**
 * Copy missing meta seed files into cwd/.memory/meta/.
 * No-op when .memory/ is absent (unless createMeta is true).
 */
export function seedMetaFiles(
  cwd = process.cwd(),
  log = console.log,
  { force = false, createMeta = false } = {}
) {
  const memory = path.join(cwd, ".memory");
  if (!pathExists(memory) && !createMeta) return 0;

  const meta = path.join(memory, "meta");
  ensureDir(meta);

  const srcDir = path.join(assetsDir(), "memory");
  let seeded = 0;
  for (const name of META_SEEDS) {
    const src = path.join(srcDir, name);
    const dest = path.join(meta, name);
    if (!pathExists(src)) continue;
    if (pathExists(dest) && !force) continue;
    copyFile(src, dest);
    log(`  [+] .memory/meta/${name}`);
    seeded += 1;
  }
  return seeded;
}
