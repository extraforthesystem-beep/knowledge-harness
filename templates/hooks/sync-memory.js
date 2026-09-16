#!/usr/bin/env node
// sessionEnd / stop hook — journal → progress or unsummarized sidecar, then harness-sync
// Compatible with Cursor, Claude Code, Antigravity, and manual OpenCode/local-model setups
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// ponytail: 2min stop debounce, sessionEnd if Cursor adds it
const DEBOUNCE_MS = 120000;
const UNSUMMARIZED_HEADER =
  '# Unsummarized (hook digest — fold into status.md on /memory-sync, then delete this file)\n\n';

function resolveProjectDir(input) {
  if (input?.workspace_roots?.[0]) return input.workspace_roots[0];
  if (input?.cwd) return input.cwd;
  return (
    process.env.CURSOR_PROJECT_DIR ||
    process.env.CLAUDE_PROJECT_DIR ||
    process.env.ANTIGRAVITY_PROJECT_DIR ||
    process.env.OPENCODE_PROJECT_DIR ||
    process.cwd()
  );
}

function lastSyncPath(dir) {
  return path.join(dir, '.memory', '.last-sync');
}

function tooSoon(dir, now = Date.now()) {
  try {
    const t = Number(fs.readFileSync(lastSyncPath(dir), 'utf8'));
    return Number.isFinite(t) && now - t < DEBOUNCE_MS;
  } catch (_) {
    return false;
  }
}

function markSynced(dir) {
  const p = lastSyncPath(dir);
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(p, String(Date.now()));
}

function splitFrontmatter(content) {
  const m = content.match(/^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$/);
  if (!m) return { fm: '', body: content };
  return { fm: m[1], body: m[2] };
}

function joinFrontmatter(fm, body) {
  if (!fm) return body;
  return `---\n${fm}\n---\n\n${body}`;
}

function progressPaths(dir) {
  const okf = path.join(dir, '.memory', 'progress', 'status.md');
  const legacy = path.join(dir, '.memory', 'PROGRESS.md');
  if (fs.existsSync(okf)) return { path: okf, okf: true };
  if (fs.existsSync(legacy)) return { path: legacy, okf: false };
  return { path: okf, okf: true };
}

function runHarnessSync(dir) {
  const script = path.join(dir, 'scripts', 'harness-sync.py');
  if (!fs.existsSync(script)) return;
  try {
    execSync('python3 scripts/harness-sync.py --skip-graphify', {
      cwd: dir,
      stdio: 'ignore',
      timeout: 120000,
    });
  } catch (_) {
    try {
      execSync('python scripts/harness-sync.py --skip-graphify', {
        cwd: dir,
        stdio: 'ignore',
        timeout: 120000,
      });
    } catch (_) {}
  }
}

function touchContext(dir) {
  const contextPath = path.join(dir, '.memory', 'context', 'project.md');
  const legacyContext = path.join(dir, '.memory', 'CONTEXT.md');
  const target = fs.existsSync(contextPath)
    ? contextPath
    : fs.existsSync(legacyContext)
      ? legacyContext
      : null;
  if (!target) return;

  let content = fs.readFileSync(target, 'utf8');
  const todayStr = new Date().toISOString().replace('T', ' ').substring(0, 19);
  const { fm, body } = splitFrontmatter(content);
  const updatedBody = body.replace(
    /## Last updated[\s\S]*?(?=\n##|$)/i,
    `## Last updated\n${todayStr}\n`
  );
  let updatedFm = fm;
  if (updatedFm) {
    updatedFm = updatedFm.replace(
      /timestamp:\s*.+/,
      `timestamp: "${new Date().toISOString()}"`
    );
  }
  fs.writeFileSync(target, joinFrontmatter(updatedFm, updatedBody.trim() + '\n'));
}

function cleanupBackups(memoryDir) {
  if (!fs.existsSync(memoryDir)) return;
  const now = Date.now();
  const sevenDaysMs = 7 * 24 * 60 * 60 * 1000;
  for (const file of fs.readdirSync(memoryDir)) {
    if (!file.endsWith('.bak')) continue;
    const filePath = path.join(memoryDir, file);
    const stats = fs.statSync(filePath);
    if (now - stats.mtimeMs > sevenDaysMs) {
      fs.unlinkSync(filePath);
      console.log(`[memory] Removed stale backup: ${file}`);
    }
  }
}

function stripMarkdownFence(text) {
  if (!text) return text;
  const trimmed = text.trim();
  const ticks = "`" + "``";
  if (trimmed.startsWith(ticks + "markdown")) {
    return trimmed.substring(11, trimmed.length - 3).trim();
  }
  if (trimmed.startsWith(ticks)) {
    return trimmed.substring(3, trimmed.length - 3).trim();
  }
  return trimmed;
}

function buildPrompt(currentProgress, journal, okf) {
  return `Update this session progress markdown based on today's journal.
Only add genuinely new information. Keep total under 50 lines in the body.
No filler words. Use file names and module names, not vague descriptions.
Do not add "Modified files:" basename dumps — those belong in progress/unsummarized.md.
${okf ? "Output ONLY the markdown body (no YAML frontmatter)." : "Output the complete PROGRESS.md only."}

CURRENT PROGRESS:
${currentProgress}

SESSION JOURNAL:
${JSON.stringify(journal, null, 2)}`;
}

async function parseJsonResponse(res, provider) {
  let data;
  try {
    data = await res.json();
  } catch (err) {
    throw new Error(`${provider} returned invalid JSON: ${err.message}`);
  }
  if (!res.ok) {
    const detail =
      data?.error?.message ||
      data?.error ||
      data?.message ||
      JSON.stringify(data);
    throw new Error(`${provider} request failed (${res.status}): ${detail}`);
  }
  return data;
}

function extractOpenAIContent(content) {
  if (typeof content === "string") return content;
  if (Array.isArray(content)) {
    return content
      .map((part) => {
        if (typeof part === "string") return part;
        if (part?.type === "text") return part.text || "";
        return part?.text || "";
      })
      .join("")
      .trim();
  }
  return "";
}

async function callAnthropic(prompt) {
  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": process.env.ANTHROPIC_API_KEY,
      "anthropic-version": "2023-06-01",
    },
    body: JSON.stringify({
      model: process.env.HARNESS_ANTHROPIC_MODEL || "claude-sonnet-5",
      max_tokens: 1000,
      messages: [{ role: "user", content: prompt }],
    }),
  });

  const data = await parseJsonResponse(res, "Anthropic");
  return stripMarkdownFence(data.content?.[0]?.text?.trim());
}

async function callGemini(prompt) {
  const model = process.env.HARNESS_GEMINI_MODEL || "gemini-2.5-pro";
  const url =
    `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent` +
    `?key=${process.env.GEMINI_API_KEY}`;
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      contents: [{ parts: [{ text: prompt }] }],
    }),
  });

  const data = await parseJsonResponse(res, "Gemini");
  return stripMarkdownFence(data.candidates?.[0]?.content?.parts?.[0]?.text?.trim());
}

function resolveOpenAICompatibleConfig() {
  const baseUrl =
    process.env.HARNESS_OPENAI_BASE_URL ||
    process.env.OPENAI_BASE_URL ||
    process.env.OPENAI_API_BASE ||
    process.env.LLM_BASE_URL ||
    "";
  const model =
    process.env.HARNESS_OPENAI_MODEL ||
    process.env.OPENAI_MODEL ||
    process.env.LLM_MODEL ||
    "";
  const apiKey =
    process.env.HARNESS_OPENAI_API_KEY ||
    process.env.OPENAI_API_KEY ||
    process.env.LLM_API_KEY ||
    "";

  if (!baseUrl && !model && !apiKey) return null;
  if (!baseUrl || !model) {
    throw new Error(
      "OpenAI-compatible sync requires HARNESS_OPENAI_BASE_URL/OPENAI_BASE_URL and HARNESS_OPENAI_MODEL/OPENAI_MODEL."
    );
  }

  return {
    baseUrl: baseUrl.replace(/\/$/, ""),
    model,
    apiKey,
  };
}

async function callOpenAICompatible(prompt, config) {
  const headers = {
    "Content-Type": "application/json",
  };
  if (config.apiKey) {
    headers.Authorization = `Bearer ${config.apiKey}`;
  }

  const res = await fetch(`${config.baseUrl}/chat/completions`, {
    method: "POST",
    headers,
    body: JSON.stringify({
      model: config.model,
      temperature: 0,
      stream: false,
      messages: [{ role: "user", content: prompt }],
    }),
  });

  const data = await parseJsonResponse(res, "OpenAI-compatible provider");
  return stripMarkdownFence(
    extractOpenAIContent(data.choices?.[0]?.message?.content)?.trim()
  );
}

function resolveProvider() {
  const explicit = (process.env.HARNESS_MEMORY_PROVIDER || "auto").trim().toLowerCase();
  if (explicit && explicit !== "auto") {
    if (explicit === "anthropic") return { type: "anthropic" };
    if (explicit === "gemini") return { type: "gemini" };
    if (explicit === "openai" || explicit === "openai-compatible") {
      return { type: "openai-compatible", config: resolveOpenAICompatibleConfig() };
    }
    if (explicit === "local" || explicit === "local-append") {
      return { type: "local-append" };
    }
    throw new Error(
      "HARNESS_MEMORY_PROVIDER must be one of: auto, anthropic, gemini, openai-compatible, local-append."
    );
  }

  const openAIConfig = resolveOpenAICompatibleConfig();
  if (openAIConfig) return { type: "openai-compatible", config: openAIConfig };
  if (process.env.ANTHROPIC_API_KEY) return { type: "anthropic" };
  if (process.env.GEMINI_API_KEY) return { type: "gemini" };
  return { type: "local-append" };
}

function mergeUnsummarized(dir, journal) {
  const dest = path.join(dir, '.memory', 'progress', 'unsummarized.md');
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  const existing = fs.existsSync(dest) ? fs.readFileSync(dest, 'utf8') : '';
  const seen = new Set(
    existing
      .split('\n')
      .filter((line) => line.startsWith('- [x] '))
      .map((line) => line.slice(6).trim())
  );
  const added = [];
  for (const entry of journal) {
    const value = String(entry.value || '').trim();
    if (!value || seen.has(value)) continue;
    seen.add(value);
    added.push(`- [x] ${value}`);
  }
  if (!added.length) return 0;
  const head = existing.trim() ? existing.trim() + '\n' : UNSUMMARIZED_HEADER;
  fs.writeFileSync(dest, head + added.join('\n') + '\n');
  return added.length;
}

function finishLocal(dir, journalPath, added) {
  fs.writeFileSync(journalPath, '');
  if (tooSoon(dir)) {
    console.log(
      `[memory] local digest +${added} (harness-sync debounced ${DEBOUNCE_MS / 1000}s)`
    );
    process.exit(0);
  }
  runHarnessSync(dir);
  markSynced(dir);
  console.log(`[memory] local digest +${added}; harness-sync ran`);
  process.exit(0);
}

async function run(projectDir, input) {
  if (input && input.trim()) {
    try {
      projectDir = resolveProjectDir(JSON.parse(input));
    } catch (_) {}
  }

  const dir = projectDir;
  const journalPath = path.join(dir, '.memory', 'session-journal.jsonl');
  const { path: progressPath, okf } = progressPaths(dir);

  if (!fs.existsSync(journalPath)) process.exit(0);

  const journalRaw = fs.readFileSync(journalPath, 'utf8').trim();
  if (!journalRaw) process.exit(0);

  const journal = journalRaw
    .split('\n')
    .filter(Boolean)
    .map((line) => {
      try {
        return JSON.parse(line);
      } catch (_) {
        return null;
      }
    })
    .filter(Boolean);

  const currentRaw = fs.existsSync(progressPath)
    ? fs.readFileSync(progressPath, 'utf8')
    : '';
  const { fm, body: currentBody } = splitFrontmatter(currentRaw);
  const currentProgress = okf ? currentBody : currentRaw;

  try {
    const provider = resolveProvider();

    if (provider.type === 'local-append') {
      const added = mergeUnsummarized(dir, journal);
      finishLocal(dir, journalPath, added);
      return;
    }

    if (tooSoon(dir)) {
      console.log('[memory] debounce: keep journal, skip LLM sync');
      process.exit(0);
    }

    const prompt = buildPrompt(currentProgress, journal, okf);
    let updatedBody = null;

    if (provider.type === "anthropic") {
      updatedBody = await callAnthropic(prompt);
    } else if (provider.type === "gemini") {
      updatedBody = await callGemini(prompt);
    } else if (provider.type === "openai-compatible") {
      updatedBody = await callOpenAICompatible(prompt, provider.config);
    }

    if (!updatedBody) {
      console.error('[memory] Empty model response received.');
      process.exit(1);
    }

    const finalContent = okf
      ? joinFrontmatter(fm, updatedBody.trim() + '\n')
      : updatedBody;

    if (fs.existsSync(progressPath)) {
      fs.copyFileSync(progressPath, progressPath + '.bak');
    }
    fs.mkdirSync(path.dirname(progressPath), { recursive: true });
    fs.writeFileSync(progressPath, finalContent);

    touchContext(dir);
    cleanupBackups(path.join(dir, '.memory'));

    fs.writeFileSync(journalPath, '');
    runHarnessSync(dir);
    markSynced(dir);
    console.log('[memory] Progress updated from session journal; harness-sync ran');
    process.exit(0);
  } catch (err) {
    console.error('[memory] sync failed:', err.message);
    process.exit(1);
  }
}

module.exports = { tooSoon, mergeUnsummarized, DEBOUNCE_MS, stripMarkdownFence };

if (require.main === module) {
  let projectDir =
    process.env.CURSOR_PROJECT_DIR ||
    process.env.CLAUDE_PROJECT_DIR ||
    process.env.ANTIGRAVITY_PROJECT_DIR ||
    process.env.OPENCODE_PROJECT_DIR ||
    process.cwd();

  let input = '';
  process.stdin.setEncoding('utf8');
  process.stdin.on('data', (chunk) => {
    input += chunk;
  });
  process.stdin.on('end', () => {
    run(projectDir, input);
  });

  if (process.stdin.isTTY) {
    run(projectDir, '');
  }
}
