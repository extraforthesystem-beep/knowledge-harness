#!/usr/bin/env node
// postToolUse / afterShellExecution / afterFileEdit — journal, ADR lock, fail nudge
// Compatible with Cursor, Claude Code, and Antigravity
const fs = require('fs');
const path = require('path');

const FAIL_NUDGE = 3;
const ADR_SNAP = path.join('.memory', '.adr-snap');

function resolveProjectDir(input) {
  if (input?.workspace_roots?.[0]) return input.workspace_roots[0];
  if (input?.cwd) return input.cwd;
  return (
    process.env.CURSOR_PROJECT_DIR ||
    process.env.CLAUDE_PROJECT_DIR ||
    process.env.ANTIGRAVITY_PROJECT_DIR ||
    process.cwd()
  );
}

function normalizePath(filePath) {
  return filePath.replace(/\\/g, '/');
}

function emitContext(text) {
  process.stdout.write(
    JSON.stringify({ additional_context: text, additionalContext: text })
  );
}

function categorizeFile(filePath) {
  const categories = {
    schema_changed: /\.(prisma|schema|migration)/i,
    config_changed: /\.(env|config|json|yaml|yml|toml)$/i,
    api_changed: /(routes|controllers|api|endpoints)\//i,
    test_changed: /\.(test|spec)\./i,
    memory_changed: /\.memory\//i,
  };

  for (const [type, pattern] of Object.entries(categories)) {
    if (pattern.test(filePath)) return type;
  }
  return 'file_changed';
}

function appendJournal(dir, entry) {
  const journalPath = path.join(dir, '.memory', 'session-journal.jsonl');
  fs.mkdirSync(path.dirname(journalPath), { recursive: true });
  fs.appendFileSync(journalPath, JSON.stringify(entry) + '\n');
}

function capturePackageInstall(cmd, dir) {
  if (
    cmd &&
    (cmd.includes('npm install') ||
      cmd.includes('pnpm add') ||
      cmd.includes('yarn add') ||
      cmd.includes('pip install') ||
      cmd.includes('uv add'))
  ) {
    appendJournal(dir, { type: 'package_added', value: cmd, ts: Date.now() });
  }
}

function relativeToProject(dir, filePath) {
  try {
    if (path.isAbsolute(filePath)) {
      const rel = path.relative(dir, filePath).split(path.sep).join('/');
      if (rel && !rel.startsWith('..')) return rel;
    }
  } catch (_) {}
  return normalizePath(filePath);
}

function snapshotAdrs(dir) {
  const src = path.join(dir, '.memory', 'decisions');
  const dest = path.join(dir, ADR_SNAP);
  if (!fs.existsSync(src)) return 0;
  fs.mkdirSync(dest, { recursive: true });
  let n = 0;
  for (const name of fs.readdirSync(src)) {
    if (!name.endsWith('.md') || name === 'index.md') continue;
    const from = path.join(src, name);
    if (!fs.statSync(from).isFile()) continue;
    fs.copyFileSync(from, path.join(dest, name));
    n++;
  }
  return n;
}

function lockedAdr(dir, filePath) {
  if (!filePath) return null;
  const rel = relativeToProject(dir, filePath);
  const norm = normalizePath(rel);
  if (!norm.includes('.memory/decisions/')) return null;
  if (norm.endsWith('index.md') || norm.includes('/archive/')) return null;
  const snap = path.join(dir, ADR_SNAP, path.basename(norm));
  if (!fs.existsSync(snap)) return null;
  const dest = path.isAbsolute(filePath) ? filePath : path.join(dir, norm);
  return { rel: norm, snap, dest };
}

function revertAdrIfLocked(dir, filePath) {
  const hit = lockedAdr(dir, filePath);
  if (!hit || !fs.existsSync(hit.dest)) return false;
  const now = fs.readFileSync(hit.dest, 'utf8');
  const old = fs.readFileSync(hit.snap, 'utf8');
  if (now === old) return false;
  fs.copyFileSync(hit.snap, hit.dest);
  appendJournal(dir, { type: 'adr_blocked', value: hit.rel, ts: Date.now() });
  emitContext(
    `Memory Authority: restored \`${hit.rel}\` — existing ADRs are append-only. Add \`.memory/decisions/YYYY-MM-DD-slug.md\`.`
  );
  return true;
}

function countShellFails(dir, cmd) {
  const journalPath = path.join(dir, '.memory', 'session-journal.jsonl');
  if (!fs.existsSync(journalPath)) return 0;
  let n = 0;
  for (const line of fs.readFileSync(journalPath, 'utf8').split('\n')) {
    if (!line) continue;
    try {
      const e = JSON.parse(line);
      if (e.type === 'shell_fail' && e.value === cmd) n++;
    } catch (_) {}
  }
  return n;
}

function captureShellOutcome(event, dir) {
  const cmd = String(event.command || event.cmd || '').trim();
  const code = event.exit_code ?? event.exitCode ?? event.status;
  if (cmd) capturePackageInstall(cmd, dir);
  if (code === 0 || code === undefined || code === null || code === '') return;
  const key = (cmd || '(unknown)').slice(0, 200);
  appendJournal(dir, { type: 'shell_fail', value: key, ts: Date.now() });
  const n = countShellFails(dir, key);
  if (n >= FAIL_NUDGE) {
    emitContext(
      `SRE: \`${key}\` failed ${n}× this session. Append \`.memory/failures/log.md\` (/failure-log) before retrying the same hypothesis.`
    );
  }
}

function captureFileWrite(filePath, dir) {
  if (!filePath) return;
  if (revertAdrIfLocked(dir, filePath)) return;
  const normalized = normalizePath(filePath);
  if (normalized.includes('.memory/')) return;

  appendJournal(dir, {
    type: categorizeFile(filePath),
    value: relativeToProject(dir, filePath),
    ts: Date.now(),
  });
}

function handleEvent(event) {
  const dir = resolveProjectDir(event);
  const hookName = event.hook_event_name || '';

  if (hookName === 'afterShellExecution') {
    captureShellOutcome(event, dir);
    return;
  }

  if (hookName === 'beforeShellExecution') {
    capturePackageInstall(event.command, dir);
    return;
  }

  if (hookName === 'afterFileEdit') {
    captureFileWrite(event.file_path, dir);
    return;
  }

  const toolName = event.tool_name || '';
  const toolInput = event.tool_input || {};
  const toolResponse = event.tool_response || {};

  if (toolName === 'Shell' || toolName === 'Bash' || toolName === 'run_command') {
    captureShellOutcome(
      {
        command: toolInput.command || toolInput.CommandLine,
        exit_code: toolResponse.exit_code ?? toolResponse.exitCode ?? toolResponse.status,
      },
      dir
    );
    return;
  }

  const writeTools = new Set([
    'Write',
    'Edit',
    'MultiEdit',
    'StrReplace',
    'ApplyPatch',
    'write_to_file',
    'replace_file_content',
    'multi_replace_file_content',
  ]);

  if (writeTools.has(toolName)) {
    const filePath =
      toolInput.file_path ||
      toolInput.path ||
      toolInput.TargetFile ||
      toolInput.target_file;
    captureFileWrite(filePath, dir);
  }
}

module.exports = {
  snapshotAdrs,
  revertAdrIfLocked,
  lockedAdr,
  countShellFails,
  captureShellOutcome,
  handleEvent,
  FAIL_NUDGE,
};

if (require.main === module) {
  let input = '';
  process.stdin.setEncoding('utf8');
  process.stdin.on('data', (chunk) => {
    input += chunk;
  });
  process.stdin.on('end', () => {
    try {
      if (!input.trim()) return;
      handleEvent(JSON.parse(input));
    } catch (_) {}
  });
}
