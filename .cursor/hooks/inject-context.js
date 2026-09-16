#!/usr/bin/env node
// sessionStart hook — injects progress/status.md at session start
// Compatible with Cursor, Claude Code, and Antigravity
const fs = require('fs');
const path = require('path');

const TOKEN_BUDGET = 500;
const NAV_START = '<!-- harness-links:autogen -->';
const NAV_END = '<!-- /harness-links:autogen -->';

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

function stripFrontmatter(text) {
  const m = text.match(/^---\s*\n[\s\S]*?\n---\s*\n([\s\S]*)$/);
  return m ? m[1].trim() : text.trim();
}

function stripForInject(text) {
  let body = stripFrontmatter(text);
  const i = body.indexOf(NAV_START);
  const j = body.indexOf(NAV_END);
  if (i !== -1 && j > i) {
    body = (body.slice(0, i) + body.slice(j + NAV_END.length)).trim();
  }
  return body.trim();
}

function estimateTokens(text) {
  if (!text) return 0;
  return Math.ceil(text.length / 4);
}

function emitContext(dir) {
  try {
    require('./capture-decisions').snapshotAdrs(dir);
  } catch (_) {}

  const progressPath = path.join(dir, '.memory', 'progress', 'status.md');
  const legacyPath = path.join(dir, '.memory', 'PROGRESS.md');
  const activePath = fs.existsSync(progressPath)
    ? progressPath
    : fs.existsSync(legacyPath)
      ? legacyPath
      : null;
  if (!activePath) return;

  const raw = fs.readFileSync(activePath, 'utf8').trim();
  const progress = stripForInject(raw);
  if (!progress) return;

  const estimatedTokens = estimateTokens(progress);
  const budgetWarning =
    estimatedTokens > TOKEN_BUDGET
      ? `\n\n⚠️ Memory budget exceeded: ~${estimatedTokens} tokens injected (target: <${TOKEN_BUDGET}). Run /memory-compact then /harness-sync.`
      : '';

  const failuresPath = path.join(dir, '.memory', 'failures', 'log.md');
  const sreNote = fs.existsSync(failuresPath)
    ? '\n\nSRE: Before retrying a failed hypothesis, read `.memory/failures/log.md`.'
    : '';

  const context = `## Resumed session — project progress\n\n${progress}${budgetWarning}${sreNote}`;

  process.stdout.write(
    JSON.stringify({
      additional_context: context,
      additionalContext: context,
    })
  );
}

module.exports = { stripForInject, estimateTokens, TOKEN_BUDGET, emitContext };

if (require.main === module) {
  let input = '';
  process.stdin.setEncoding('utf8');
  process.stdin.on('data', (chunk) => {
    input += chunk;
  });
  process.stdin.on('end', () => {
    try {
      const event = input.trim() ? JSON.parse(input) : {};
      emitContext(resolveProjectDir(event));
    } catch (_) {
      emitContext(resolveProjectDir({}));
    }
  });

  if (process.stdin.isTTY) {
    emitContext(resolveProjectDir({}));
  }
}
