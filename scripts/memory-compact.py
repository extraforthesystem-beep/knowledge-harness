#!/usr/bin/env python3
"""Archive superseded ADRs and stale completed features. Does not renumber ADRs."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MEMORY = ROOT / ".memory"
DECISIONS = MEMORY / "decisions"
FEATURES = MEMORY / "features"
ARCHIVE_DECISIONS = DECISIONS / "archive"
ARCHIVE_FEATURES = FEATURES / "archive"

FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
DONE_STATUSES = frozenset({"done", "completed", "deployed"})
FEATURE_AGE_DAYS = 14


def parse_frontmatter(text: str) -> dict[str, str]:
    m = FM_RE.match(text)
    if not m:
        return {}
    fm: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.strip().startswith("- "):
            key, _, val = line.partition(":")
            fm[key.strip()] = val.strip().strip('"')
    return fm


def archive_superseded_adrs() -> list[str]:
    moved: list[str] = []
    for md in sorted(DECISIONS.glob("*.md")):
        if md.name == "index.md":
            continue
        fm = parse_frontmatter(md.read_text(encoding="utf-8"))
        status = fm.get("status", "").lower()
        if status not in ("superseded", "deprecated"):
            continue
        dest = ARCHIVE_DECISIONS / md.name
        ARCHIVE_DECISIONS.mkdir(parents=True, exist_ok=True)
        shutil.move(str(md), str(dest))
        moved.append(md.name)
    return moved


def archive_stale_features() -> list[str]:
    moved: list[str] = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=FEATURE_AGE_DAYS)
    for md in sorted(FEATURES.glob("*.md")):
        if md.name == "index.md":
            continue
        text = md.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        status = fm.get("status", "").lower()
        if status not in DONE_STATUSES:
            continue
        ts_raw = fm.get("timestamp", "")
        try:
            ts = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
        except ValueError:
            ts = datetime.fromtimestamp(md.stat().st_mtime, tz=timezone.utc)
        if ts > cutoff:
            continue
        dest = ARCHIVE_FEATURES / md.name
        ARCHIVE_FEATURES.mkdir(parents=True, exist_ok=True)
        shutil.move(str(md), str(dest))
        moved.append(md.name)
    return moved


def main() -> int:
    adr_moves = archive_superseded_adrs()
    feat_moves = archive_stale_features()

    print(f"Archived {len(adr_moves)} superseded ADR(s):")
    for name in adr_moves:
        print(f"  - {name}")
    if not adr_moves:
        print("  (none)")

    print(f"Archived {len(feat_moves)} completed feature(s) older than {FEATURE_AGE_DAYS}d:")
    for name in feat_moves:
        print(f"  - {name}")
    if not feat_moves:
        print("  (none)")

    if adr_moves or feat_moves:
        sync = ROOT / "scripts" / "harness-sync.py"
        if sync.exists():
            print("Running harness-sync...")
            subprocess.run([sys.executable, str(sync), "--skip-graphify"], check=False, cwd=str(ROOT))
    else:
        print("No moves — run harness-sync manually if indexes are stale.")

    print("Note: ADR renumbering is manual — check duplicate ADR numbers separately.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
