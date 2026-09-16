#!/usr/bin/env python3
"""One-time migration: flat .memory/*.md → OKF concept layout."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MEMORY = ROOT / ".memory"
LEGACY = MEMORY / "_legacy"

FLAT_FILES = ("CONTEXT.md", "PROGRESS.md", "DECISIONS.md", "DECISIONS-archive.md", "INDEX.md")
OKF_DIRS = (
    "context",
    "progress",
    "decisions",
    "decisions/archive",
    "features",
    "features/archive",
    "meta",
)

ADR_RE = re.compile(
    r"^###\s+(?P<date>\d{4}-\d{2}-\d{2})\s+(?P<title>.+)$", re.MULTILINE
)
STATUS_RE = re.compile(r"^\-\s+\*\*Status:\*\*\s+(.+)$", re.MULTILINE)
PRIORITY_RE = re.compile(r"^\-\s+\*\*Priority:\*\*\s+(.+)$", re.MULTILINE)
FM_RE = re.compile(r"^---\s*\n.*?\n---\s*\n", re.DOTALL)
TITLE_RE = re.compile(r"^#\s+Feature:\s*(.+)$", re.MULTILINE)


def slugify(text: str) -> str:
    s = text.lower().strip()
    s = re.sub(r"[`'\"]", "", s)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")[:80] or "untitled"


def fm_block(**fields: str | list[str]) -> str:
    lines = ["---"]
    for key, val in fields.items():
        if isinstance(val, list):
            if val:
                lines.append(f"{key}:")
                for item in val:
                    lines.append(f"  - {item}")
            else:
                lines.append(f"{key}: []")
        else:
            escaped = str(val).replace('"', '\\"')
            if any(c in escaped for c in ":{}[]#&*!|>'\"%@`"):
                lines.append(f'{key}: "{escaped}"')
            else:
                lines.append(f"{key}: {escaped}")
    lines.append("---")
    return "\n".join(lines)


def has_okf_frontmatter(text: str) -> bool:
    m = FM_RE.match(text)
    if not m:
        return False
    block = m.group(0)
    return "type:" in block


def resolve_source(name: str) -> Path | None:
    """Return flat source file from bundle root or _legacy/."""
    for base in (MEMORY, LEGACY):
        path = base / name
        if path.exists():
            return path
    return None


def write_concept(path: Path, frontmatter: str, body: str, *, dry_run: bool) -> None:
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    body = body.strip() + "\n"
    path.write_text(f"{frontmatter}\n\n{body}", encoding="utf-8")


def source_is_newer_than_dest(src: Path, dest: Path) -> bool:
    if not dest.exists():
        return True
    return src.stat().st_mtime >= dest.stat().st_mtime


def parse_adrs(text: str) -> list[tuple[str, str, str]]:
    entries: list[tuple[str, str, str]] = []
    matches = list(ADR_RE.finditer(text))
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        entries.append((m.group("date"), m.group("title").strip(), body))
    return entries


def scaffold_layout(*, dry_run: bool) -> None:
    for rel in OKF_DIRS:
        path = MEMORY / rel
        if dry_run:
            continue
        path.mkdir(parents=True, exist_ok=True)
        gitkeep = path / ".gitkeep"
        if rel.startswith("features") and not any(path.glob("*.md")):
            gitkeep.touch(exist_ok=True)


def migrate_context(*, force: bool, dry_run: bool) -> bool:
    dest = MEMORY / "context" / "project.md"
    if dest.exists() and not force:
        return False
    src = resolve_source("CONTEXT.md")
    if not src or (dest.exists() and not source_is_newer_than_dest(src, dest)):
        return False
    body = src.read_text(encoding="utf-8")
    if body.startswith("# Project context"):
        body = body.replace("# Project context\n", "", 1)
    elif body.startswith("# Project Context"):
        body = body.replace("# Project Context\n", "", 1)
    ts = datetime.fromtimestamp(src.stat().st_mtime, tz=timezone.utc).isoformat()
    fm = fm_block(
        type="Project Context",
        title="Project Context",
        description="Current project stack, phase, branch, and key paths",
        tags=["context", "harness"],
        timestamp=ts,
    )
    write_concept(dest, fm, body, dry_run=dry_run)
    return True


def migrate_progress(*, force: bool, dry_run: bool) -> bool:
    dest = MEMORY / "progress" / "status.md"
    if dest.exists() and not force:
        return False
    src = resolve_source("PROGRESS.md")
    if not src or (dest.exists() and not source_is_newer_than_dest(src, dest)):
        return False
    body = src.read_text(encoding="utf-8")
    if body.startswith("# Progress"):
        body = body.replace("# Progress\n", "", 1)
    ts = datetime.fromtimestamp(src.stat().st_mtime, tz=timezone.utc).isoformat()
    fm = fm_block(
        type="Session Progress",
        title="Session Progress",
        description="Done, in-progress, and next work items",
        tags=["progress", "harness"],
        timestamp=ts,
    )
    write_concept(dest, fm, body, dry_run=dry_run)
    return True


def migrate_decisions_file(
    src_name: str, dest_dir: Path, *, force: bool, dry_run: bool
) -> int:
    src = resolve_source(src_name)
    if not src:
        return 0
    text = src.read_text(encoding="utf-8")
    entries = parse_adrs(text)
    count = 0
    for date, title, body in entries:
        slug = slugify(title)
        path = dest_dir / f"{date}-{slug}.md"
        if path.exists() and not force:
            continue
        fm = fm_block(
            type="Architectural Decision",
            title=title,
            description=f"ADR from {date}",
            tags=["decision", "adr"],
            status="accepted",
            timestamp=f"{date}T00:00:00Z",
        )
        write_concept(path, fm, body, dry_run=dry_run)
        count += 1
    return count


def migrate_feature(path: Path, *, force: bool, dry_run: bool) -> bool:
    if path.name in (".gitkeep", "index.md"):
        return False
    dest = MEMORY / "features" / path.name
    text = path.read_text(encoding="utf-8")
    if has_okf_frontmatter(text):
        return False
    if dest.exists() and has_okf_frontmatter(dest.read_text(encoding="utf-8")) and not force:
        return False

    status = STATUS_RE.search(text)
    priority = PRIORITY_RE.search(text)
    title_match = TITLE_RE.search(text)
    title = title_match.group(1).strip() if title_match else path.stem.replace("-", " ").title()
    body = text
    if title_match:
        body = text[title_match.end() :].lstrip("\n")
    body = STATUS_RE.sub("", body)
    body = PRIORITY_RE.sub("", body)
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    ts = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()
    fm = fm_block(
        type="Feature Spec",
        title=title,
        description=f"Feature spec: {title}",
        status=status.group(1).strip() if status else "planned",
        priority=priority.group(1).strip() if priority else "medium",
        depends_on=[],
        blocks=[],
        tags=["feature", "harness"],
        timestamp=ts,
    )
    write_concept(dest, fm, body, dry_run=dry_run)
    return True


def migrate_features(*, force: bool, dry_run: bool) -> int:
    count = 0
    src_dir = MEMORY / "features"
    if not src_dir.exists():
        return 0
    for path in sorted(src_dir.glob("*.md")):
        if migrate_feature(path, force=force, dry_run=dry_run):
            count += 1
    legacy_features = LEGACY / "features"
    if legacy_features.exists():
        for path in sorted(legacy_features.glob("*.md")):
            dest = MEMORY / "features" / path.name
            if dest.exists() and not force:
                continue
            if migrate_feature(path, force=force, dry_run=dry_run):
                count += 1
    return count


def meta_seed_sources() -> list[Path]:
    """Prefer repo templates/memory/*.md; fall back to package assets if present."""
    candidates = [
        ROOT / "templates" / "memory",
        ROOT / "packages" / "knowledge-harness" / "assets" / "memory",
    ]
    for d in candidates:
        if d.is_dir() and any(d.glob("*.md")):
            return sorted(d.glob("*.md"))
    return []


def migrate_meta_seeds(*, force: bool, dry_run: bool) -> list[str]:
    """Seed .memory/meta/ from templates (router, sre-routing, memory-authority, …)."""
    written: list[str] = []
    seeds = meta_seed_sources()
    if not seeds:
        # Minimal fallback when templates are unavailable (e.g. copied script alone)
        if migrate_meta_router_fallback(force=force, dry_run=dry_run):
            written.append("router.md")
        return written

    meta_dir = MEMORY / "meta"
    if not dry_run:
        meta_dir.mkdir(parents=True, exist_ok=True)
    for src in seeds:
        dest = meta_dir / src.name
        if dest.exists() and not force:
            continue
        if dry_run:
            written.append(src.name)
            continue
        shutil.copy2(src, dest)
        written.append(src.name)
    return written


def migrate_meta_router_fallback(*, force: bool, dry_run: bool) -> bool:
    dest = MEMORY / "meta" / "router.md"
    if dest.exists() and not force:
        return False
    ts = datetime.now(timezone.utc).isoformat()
    fm = fm_block(
        type="Meta",
        title="Harness Router",
        description="Harness slash commands and agent workflow",
        tags=["meta", "harness"],
        timestamp=ts,
    )
    body = """# Harness slash commands

**Daily:** `/feature-add` · `/memory-sync` (end of session — progress, ADRs, handoff, index/viz)

**One-time:** `/memory-migrate` · `/memory-init`

**Rare:** `/memory-compact` · `/failure-log`

**Aliases → `/memory-sync` (not installed):** `/handoff` · `/extract-memory` · `/compact` · `/harness-sync`

# Agent workflow

1. Read `.memory/index.md` then `progress/status.md`
2. Topic recall on demand → Memory Authority (`memory-authority.md`); for features → `features/<slug>.md`; for architecture → `decisions/`
3. Hard truth conflict/bend → challenge before write; progress is soft
4. For code exploration → `/graphify query` before grep
5. After work → run `/memory-sync`
"""
    write_concept(dest, fm, body, dry_run=dry_run)
    return True


def archive_legacy(*, dry_run: bool) -> list[str]:
    moved: list[str] = []
    LEGACY.mkdir(parents=True, exist_ok=True)
    for name in FLAT_FILES:
        src = MEMORY / name
        if src.exists():
            dest = LEGACY / name
            if dry_run:
                moved.append(name)
                continue
            if dest.exists():
                stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
                dest = LEGACY / f"{name}.{stamp}.bak"
            shutil.move(str(src), str(dest))
            moved.append(name)
    bak = MEMORY / "PROGRESS.md.bak"
    if bak.exists():
        if dry_run:
            moved.append("PROGRESS.md.bak")
        else:
            dest = LEGACY / "PROGRESS.md.bak"
            if dest.exists():
                stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
                dest = LEGACY / f"PROGRESS.md.bak.{stamp}"
            shutil.move(str(bak), str(dest))
            moved.append("PROGRESS.md.bak")
    return moved


def already_migrated() -> bool:
    return (MEMORY / "context" / "project.md").exists()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Migrate flat .memory/*.md files to OKF concept layout"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing OKF concepts from flat sources",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report actions without writing files",
    )
    args = parser.parse_args()

    if not MEMORY.exists():
        print("ERROR: .memory/ not found", file=sys.stderr)
        return 1

    if already_migrated() and not args.force:
        flat_remaining = [n for n in FLAT_FILES if (MEMORY / n).exists()]
        if flat_remaining:
            print(
                "OKF layout present; archiving leftover flat files:",
                ", ".join(flat_remaining),
            )
            moved = archive_legacy(dry_run=args.dry_run)
            if moved and not args.dry_run:
                print(f"  moved to _legacy/: {', '.join(moved)}")
            return 0
        print(
            "OKF layout already present (.memory/context/project.md). "
            "Use --force to re-migrate from flat sources."
        )
        return 0

    print("Migrating .memory/ to OKF layout...")
    scaffold_layout(dry_run=args.dry_run)

    ctx = migrate_context(force=args.force, dry_run=args.dry_run)
    prog = migrate_progress(force=args.force, dry_run=args.dry_run)
    n_active = migrate_decisions_file(
        "DECISIONS.md", MEMORY / "decisions", force=args.force, dry_run=args.dry_run
    )
    n_archive = migrate_decisions_file(
        "DECISIONS-archive.md",
        MEMORY / "decisions" / "archive",
        force=args.force,
        dry_run=args.dry_run,
    )
    n_features = migrate_features(force=args.force, dry_run=args.dry_run)
    meta = migrate_meta_seeds(force=args.force, dry_run=args.dry_run)
    moved = archive_legacy(dry_run=args.dry_run)

    prefix = "[dry-run] " if args.dry_run else ""
    print(f"{prefix}context/project.md {'written' if ctx else 'skipped'}")
    print(f"{prefix}progress/status.md {'written' if prog else 'skipped'}")
    print(f"{prefix}decisions/ ({n_active} active ADR(s))")
    print(f"{prefix}decisions/archive/ ({n_archive} archived ADR(s))")
    print(f"{prefix}features/ ({n_features} feature(s) migrated)")
    if meta:
        print(f"{prefix}meta/ ({', '.join(meta)})")
    else:
        print(f"{prefix}meta/ (skipped — already present)")
    if moved:
        print(f"{prefix}_legacy/ ({', '.join(moved)})")
    print("Run: python scripts/harness-sync.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
