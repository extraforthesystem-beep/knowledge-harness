import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export function expandHome(p) {
  if (p.startsWith("~/")) return path.join(os.homedir(), p.slice(2));
  if (p === "~") return os.homedir();
  return p;
}

export function packageRoot() {
  return path.resolve(__dirname, "..");
}

export function assetsDir() {
  return path.join(packageRoot(), "assets");
}

export function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

export function copyFile(src, dest) {
  ensureDir(path.dirname(dest));
  fs.copyFileSync(src, dest);
}

export function pathExists(p) {
  try {
    fs.accessSync(p);
    return true;
  } catch {
    return false;
  }
}

export function removeIfExists(p) {
  if (pathExists(p)) fs.unlinkSync(p);
}
