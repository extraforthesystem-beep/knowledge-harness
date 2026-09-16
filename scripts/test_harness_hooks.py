#!/usr/bin/env python3
"""Checks for inject-budget + debt-skip + JS strip parity."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SYNC = ROOT / "scripts" / "harness-sync.py"
INJECT = ROOT / "templates" / "hooks" / "inject-context.js"
SYNC_JS = ROOT / "templates" / "hooks" / "sync-memory.js"


def load_sync():
    spec = importlib.util.spec_from_file_location("harness_sync", SYNC)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


SAMPLE = """---
type: Session Progress
title: Session Progress
---

# Progress

hello

<!-- harness-links:autogen -->
## Graph links

- [x](y)
<!-- /harness-links:autogen -->
"""


CAPTURE = ROOT / "templates" / "hooks" / "capture-decisions.js"


class HarnessHookTests(unittest.TestCase):
    def test_strip_for_inject(self):
        mod = load_sync()
        self.assertEqual(mod.strip_for_inject(SAMPLE), "# Progress\n\nhello")

    def test_estimate_inject_tokens_uses_status(self):
        mod = load_sync()
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        memory = Path(tmp.name) / ".memory"
        (memory / "progress").mkdir(parents=True)
        (memory / "progress" / "status.md").write_text(SAMPLE, encoding="utf-8")
        (memory / "context").mkdir()
        (memory / "context" / "project.md").write_text("x" * 4000, encoding="utf-8")
        orig = mod.MEMORY
        mod.MEMORY = memory
        try:
            n = mod.estimate_inject_tokens()
        finally:
            mod.MEMORY = orig
        self.assertEqual(n, mod.estimate_tokens("# Progress\n\nhello"))
        self.assertLess(n, 20)

    def test_js_strip_matches_python(self):
        mod = load_sync()
        py = mod.strip_for_inject(SAMPLE)
        proc = subprocess.run(
            [
                "node",
                "-e",
                "const {stripForInject}=require(process.argv[1]); process.stdout.write(stripForInject(process.argv[2]));",
                str(INJECT),
                SAMPLE,
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.stdout, py)

    def test_debounce(self):
        proc = subprocess.run(
            [
                "node",
                "-e",
                """
const fs = require('fs');
const os = require('os');
const path = require('path');
const {tooSoon, DEBOUNCE_MS} = require(process.argv[1]);
const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'kh-'));
fs.mkdirSync(path.join(dir, '.memory'));
const now = 1_000_000;
if (tooSoon(dir, now)) process.exit(1);
fs.writeFileSync(path.join(dir, '.memory', '.last-sync'), String(now - 1000));
if (!tooSoon(dir, now)) process.exit(2);
fs.writeFileSync(path.join(dir, '.memory', '.last-sync'), String(now - DEBOUNCE_MS - 1));
if (tooSoon(dir, now)) process.exit(3);
""",
                str(SYNC_JS),
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_merge_unsummarized_dedupes(self):
        proc = subprocess.run(
            [
                "node",
                "-e",
                """
const fs = require('fs');
const os = require('os');
const path = require('path');
const {mergeUnsummarized} = require(process.argv[1]);
const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'kh-'));
const n1 = mergeUnsummarized(dir, [{value:'a.js'}, {value:'a.js'}, {value:'b.js'}]);
const n2 = mergeUnsummarized(dir, [{value:'b.js'}, {value:'c.js'}]);
if (n1 !== 2 || n2 !== 1) process.exit(1);
const text = fs.readFileSync(path.join(dir, '.memory', 'progress', 'unsummarized.md'), 'utf8');
if (!text.includes('a.js') || !text.includes('c.js')) process.exit(2);
if (text.split('a.js').length !== 2) process.exit(3);
""",
                str(SYNC_JS),
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_adr_lock_restores_existing(self):
        proc = subprocess.run(
            [
                "node",
                "-e",
                """
const fs = require('fs');
const os = require('os');
const path = require('path');
const {snapshotAdrs, revertAdrIfLocked} = require(process.argv[1]);
const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'kh-'));
const adr = path.join(dir, '.memory', 'decisions', '2026-01-01-old.md');
fs.mkdirSync(path.dirname(adr), { recursive: true });
fs.writeFileSync(adr, 'keep me');
snapshotAdrs(dir);
fs.writeFileSync(adr, 'overwrite');
if (!revertAdrIfLocked(dir, adr)) process.exit(1);
if (fs.readFileSync(adr, 'utf8') !== 'keep me') process.exit(2);
const fresh = path.join(dir, '.memory', 'decisions', '2026-09-16-new.md');
fs.writeFileSync(fresh, 'new adr');
if (revertAdrIfLocked(dir, fresh)) process.exit(3);
if (fs.readFileSync(fresh, 'utf8') !== 'new adr') process.exit(4);
""",
                str(CAPTURE),
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)

    def test_shell_fail_nudge_on_third(self):
        proc = subprocess.run(
            [
                "node",
                "-e",
                """
const fs = require('fs');
const os = require('os');
const path = require('path');
const {handleEvent} = require(process.argv[1]);
const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'kh-'));
let out = '';
const orig = process.stdout.write.bind(process.stdout);
process.stdout.write = (s) => { out += s; return true; };
for (let i = 0; i < 3; i++) {
  handleEvent({ hook_event_name: 'afterShellExecution', command: 'false', exit_code: 1, cwd: dir, workspace_roots: [dir] });
}
process.stdout.write = orig;
if (!out.includes('failed 3')) process.exit(1);
const journal = fs.readFileSync(path.join(dir, '.memory', 'session-journal.jsonl'), 'utf8');
if (journal.split('shell_fail').length !== 4) process.exit(2);
""",
                str(CAPTURE),
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)


if __name__ == "__main__":
    unittest.main()
