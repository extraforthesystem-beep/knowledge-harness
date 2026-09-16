#!/usr/bin/env python3
"""Tests for migrate-memory-to-okf.py using an isolated temp bundle."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "migrate-memory-to-okf.py"


def load_module():
    spec = importlib.util.spec_from_file_location("migrate_memory_to_okf", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


class MigrateMemoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.memory = self.root / ".memory"
        self.memory.mkdir()
        self.mod = load_module()
        self._orig_memory = self.mod.MEMORY
        self._orig_legacy = self.mod.LEGACY
        self.mod.MEMORY = self.memory
        self.mod.LEGACY = self.memory / "_legacy"

    def tearDown(self) -> None:
        self.mod.MEMORY = self._orig_memory
        self.mod.LEGACY = self._orig_legacy
        self.tmp.cleanup()

    def _write(self, rel: str, content: str) -> Path:
        path = self.memory / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def test_migrates_flat_layout(self) -> None:
        self._write(
            "CONTEXT.md",
            "# Project context\n\n## Stack\nPython\n",
        )
        self._write(
            "PROGRESS.md",
            "# Progress\n\n## Done\n- item\n",
        )
        self._write(
            "DECISIONS.md",
            """# Architectural decisions

### 2026-05-20 Sample decision title
**Decision:** do the thing
**Why:** because
""",
        )
        self._write(
            "features/my-feature.md",
            """# Feature: My Feature

- **Status:** in-progress
- **Priority:** high

## What it does
Stuff.
""",
        )

        self.mod.scaffold_layout(dry_run=False)
        self.assertTrue(self.mod.migrate_context(force=False, dry_run=False))
        self.assertTrue(self.mod.migrate_progress(force=False, dry_run=False))
        n = self.mod.migrate_decisions_file(
            "DECISIONS.md", self.memory / "decisions", force=False, dry_run=False
        )
        self.assertEqual(n, 1)
        nf = self.mod.migrate_features(force=False, dry_run=False)
        self.assertEqual(nf, 1)
        moved = self.mod.archive_legacy(dry_run=False)
        self.assertIn("CONTEXT.md", moved)
        self.assertIn("PROGRESS.md", moved)

        ctx = (self.memory / "context" / "project.md").read_text(encoding="utf-8")
        self.assertIn("type: Project Context", ctx)
        self.assertIn("## Stack", ctx)
        self.assertNotIn("# Project context", ctx)

        adr = (self.memory / "decisions" / "2026-05-20-sample-decision-title.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("type: Architectural Decision", adr)
        self.assertIn("**Decision:** do the thing", adr)

        feat = (self.memory / "features" / "my-feature.md").read_text(encoding="utf-8")
        self.assertIn("type: Feature Spec", feat)
        self.assertIn("status: in-progress", feat)
        self.assertIn("priority: high", feat)
        self.assertNotIn("**Status:**", feat)

    def test_skips_okf_features(self) -> None:
        self._write(
            "features/existing.md",
            """---
type: Feature Spec
title: Existing
status: done
priority: low
---

Body only.
""",
        )
        n = self.mod.migrate_features(force=False, dry_run=False)
        self.assertEqual(n, 0)
        text = (self.memory / "features" / "existing.md").read_text(encoding="utf-8")
        self.assertIn("Body only.", text)

    def test_slugify_backticks(self) -> None:
        title = "`.gitignore` excluded from harness template"
        self.assertEqual(
            self.mod.slugify(title),
            "gitignore-excluded-from-harness-template",
        )

    def test_resolves_from_legacy(self) -> None:
        legacy = self.memory / "_legacy"
        legacy.mkdir()
        (legacy / "CONTEXT.md").write_text("# Project context\n\nlegacy\n", encoding="utf-8")
        src = self.mod.resolve_source("CONTEXT.md")
        self.assertEqual(src, legacy / "CONTEXT.md")

    def test_force_skips_older_legacy_over_newer_dest(self) -> None:
        self._write("progress/status.md", "---\ntype: Session Progress\n---\n\nnewer\n")
        legacy = self.memory / "_legacy"
        legacy.mkdir()
        (legacy / "PROGRESS.md").write_text("# Progress\n\nolder\n", encoding="utf-8")
        import os
        import time

        time.sleep(0.05)
        os.utime(self.memory / "progress" / "status.md")
        self.assertFalse(self.mod.migrate_progress(force=True, dry_run=False))
        text = (self.memory / "progress" / "status.md").read_text(encoding="utf-8")
        self.assertIn("newer", text)
        self.assertNotIn("older", text)


if __name__ == "__main__":
    raise SystemExit(unittest.main())
