#!/usr/bin/env python3
"""Ablation: Knowledge Harness ON vs OFF for token-effective project recall.

Simulates how an agent gathers answers for fixed project questions:

  A — with harness: follow .memory/ entry points only
  B — without: blind repo search, excluding .memory/

Measures tokens read, wall time, files opened, and whether the answer needle
was found. Also compares session-start context (inject vs dumping routers).

Usage:
  python scripts/benchmark-ablation.py
  python scripts/benchmark-ablation.py --tsv docs/benchmark-ablation.tsv
"""

from __future__ import annotations

import argparse
import math
import re
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MEMORY = ROOT / ".memory"
FM_RE = re.compile(r"^---\s*\n.*?\n---\s*\n", re.DOTALL)

SKIP_DIRS = {
    ".git",
    ".venv",
    "node_modules",
    "graphify-out",
    ".memory",
    ".notebooklm-run",
    "__pycache__",
    ".cursor",
    "agent-tools",
}

# On this dogfood repo, router files ARE the harness. Exclude them from the
# WITHOUT arm so "no harness" means bare project search, not AGENTS.md leakage.
WITHOUT_EXCLUDE_NAMES = {
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    "CROSS-IDE.md",
}


def estimate_tokens(text: str) -> int:
    return max(1, math.ceil(len(text) / 4)) if text else 0


def strip_frontmatter(text: str) -> str:
    m = FM_RE.match(text)
    return (text[m.end() :] if m else text).strip()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


@dataclass
class ProbeResult:
    condition: str
    task_id: str
    found: bool
    files: int
    tokens: int
    ms: float
    paths: list[str] = field(default_factory=list)


@dataclass
class Task:
    task_id: str
    question: str
    needles: list[str]  # case-insensitive; any match = success
    harness_paths: list[str]  # relative to ROOT, read in order


TASKS: list[Task] = [
    Task(
        "next_work",
        "What are the next work items?",
        ["Republish npm", "install-harness.sh", "SYSTEM-MAP", "deep-recall"],
        [".memory/index.md", ".memory/progress/status.md"],
    ),
    Task(
        "current_phase",
        "What is the current project phase?",
        ["Competitor memory-tool comparison", "Long-term memory benchmark", "dogfood"],
        [".memory/index.md", ".memory/context/project.md"],
    ),
    Task(
        "okf_decision",
        "What did we decide about the OKF memory store?",
        ["OKF knowledge bundle", "no export mirror", "no GCP"],
        [".memory/index.md", ".memory/decisions/index.md", ".memory/decisions/2026-06-21-okf-native-memory-bundle.md"],
    ),
    Task(
        "one_deep_recall",
        "Should we install both claude-mem and agentmemory?",
        ["One deep-recall plugin", "not both", "Avoid double inject"],
        [".memory/index.md", ".memory/progress/status.md"],
    ),
    Task(
        "sync_command",
        "How do we sync / regenerate the memory index?",
        ["harness-sync.py", "memory-sync"],
        [".memory/index.md", ".memory/context/project.md"],
    ),
    Task(
        "failure_log",
        "Where do we record failed hypotheses before retrying?",
        ["Failure Log", "FAIL-XXX", "Hypothesis"],
        [".memory/index.md", ".memory/failures/log.md"],
    ),
    Task(
        "cross_ide",
        "Is the harness cross-IDE or Claude-only?",
        ["Cross-IDE", "Cursor", "OpenCode", "Antigravity"],
        [".memory/index.md", ".memory/decisions/index.md", ".memory/decisions/2026-06-21-cross-ide-harness-parity.md"],
    ),
    Task(
        "install_path",
        "How do you install the harness globally?",
        ["knowledge-harness install", "npx knowledge-harness"],
        [".memory/index.md", ".memory/context/project.md"],
    ),
]


def contains_needle(text: str, needles: list[str]) -> bool:
    low = text.lower()
    return any(n.lower() in low for n in needles)


def run_harness(task: Task) -> ProbeResult:
    t0 = time.perf_counter()
    tokens = 0
    files = 0
    paths: list[str] = []
    blob = ""
    found = False
    for rel in task.harness_paths:
        path = ROOT / rel
        if not path.is_file():
            continue
        text = strip_frontmatter(read_text(path))
        tokens += estimate_tokens(text)
        files += 1
        paths.append(rel)
        blob += "\n" + text
        if contains_needle(blob, task.needles):
            found = True
            break
    ms = (time.perf_counter() - t0) * 1000.0
    return ProbeResult("with_harness", task.task_id, found, files, tokens, ms, paths)


def candidate_files(query_terms: list[str], limit: int = 40) -> list[Path]:
    """Blind search: rg for task terms, excluding .memory and heavy dirs."""
    pattern = "|".join(re.escape(t) for t in query_terms if t.strip())
    if not pattern:
        pattern = task_id_fallback(query_terms)
    globs = [
        "--glob",
        "!.git/**",
        "--glob",
        "!.venv/**",
        "--glob",
        "!node_modules/**",
        "--glob",
        "!graphify-out/**",
        "--glob",
        "!.memory/**",
        "--glob",
        "!.notebooklm-run/**",
        "--glob",
        "!**/__pycache__/**",
        "--glob",
        "*.{md,py,js,ts,json,sh,txt}",
    ]
    try:
        proc = subprocess.run(
            ["rg", "-l", "-i", "-e", pattern, *globs, str(ROOT)],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
    except FileNotFoundError:
        return fallback_walk(query_terms, limit)

    out: list[Path] = []
    for line in (proc.stdout or "").splitlines():
        p = Path(line.strip())
        if not p.is_file():
            continue
        if p.name in WITHOUT_EXCLUDE_NAMES:
            continue
        # Prefer docs/README/scripts near root
        out.append(p)
        if len(out) >= limit:
            break
    if not out:
        return fallback_walk(query_terms, limit)
    # Rank: shorter path / docs / README first
    def rank(p: Path) -> tuple[int, int, str]:
        rel = str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)
        score = 0
        name = p.name.lower()
        if name in {"readme.md"}:
            score -= 100
        if rel.startswith("docs/"):
            score -= 50
        if rel.startswith("scripts/"):
            score -= 20
        if rel.startswith("packages/"):
            score -= 10
        return (score, len(rel), rel)

    out.sort(key=rank)
    return out


def task_id_fallback(terms: list[str]) -> str:
    return "|".join(terms) if terms else "harness"


def fallback_walk(terms: list[str], limit: int) -> list[Path]:
    hits: list[Path] = []
    term_l = [t.lower() for t in terms]
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.name in WITHOUT_EXCLUDE_NAMES:
            continue
        if p.suffix.lower() not in {".md", ".py", ".js", ".ts", ".json", ".sh", ".txt"}:
            continue
        try:
            text = read_text(p).lower()
        except OSError:
            continue
        if any(t in text for t in term_l):
            hits.append(p)
            if len(hits) >= limit:
                break
    return hits


def run_without(task: Task) -> ProbeResult:
    t0 = time.perf_counter()
    # Search using question keywords + needles
    terms = list(task.needles) + [
        w for w in re.findall(r"[A-Za-z][A-Za-z0-9_-]{3,}", task.question)
    ]
    # Dedup preserve order
    seen: set[str] = set()
    uniq: list[str] = []
    for t in terms:
        k = t.lower()
        if k not in seen:
            seen.add(k)
            uniq.append(t)

    files_list = candidate_files(uniq)
    tokens = 0
    files = 0
    paths: list[str] = []
    blob = ""
    found = False
    # Cap reads to mimic impatient agent (first N hits)
    for path in files_list[:25]:
        try:
            text = strip_frontmatter(read_text(path))
        except OSError:
            continue
        rel = str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
        tokens += estimate_tokens(text)
        files += 1
        paths.append(rel)
        blob += "\n" + text
        if contains_needle(blob, task.needles):
            found = True
            break
    ms = (time.perf_counter() - t0) * 1000.0
    return ProbeResult("without_harness", task.task_id, found, files, tokens, ms, paths)


def session_start_costs() -> dict[str, object]:
    """Compare session-start context: harness inject vs dumping router docs."""
    status = MEMORY / "progress" / "status.md"
    inject = ""
    if status.exists():
        inject = (
            "## Resumed session — project progress\n\n"
            + strip_frontmatter(read_text(status))
        )
    with_tok = estimate_tokens(inject)

    # "Normal without harness": dump README only (routers ARE the harness here)
    dump_files = [
        ROOT / "README.md",
        ROOT / "packages" / "knowledge-harness" / "README.md",
    ]
    dump_text = []
    dump_paths = []
    for p in dump_files:
        if p.is_file():
            dump_text.append(read_text(p))
            dump_paths.append(p.name)
    without_tok = estimate_tokens("\n\n".join(dump_text))

    return {
        "with_harness_inject_tokens": with_tok,
        "without_dump_tokens": without_tok,
        "without_files": dump_paths,
        "tokens_saved": max(0, without_tok - with_tok),
        "pct_saved": (
            round(100.0 * (without_tok - with_tok) / without_tok, 1)
            if without_tok
            else 0.0
        ),
    }


def pct(a: float, b: float) -> float:
    if b <= 0:
        return 0.0
    return round(100.0 * (b - a) / b, 1)


def print_report(
    with_rows: list[ProbeResult],
    without_rows: list[ProbeResult],
    session: dict[str, object],
) -> None:
    print("Knowledge Harness — ablation (WITH vs WITHOUT)")
    print(f"ts: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")
    print()
    print("Session-start context")
    print(
        f"  WITH  inject  ~{session['with_harness_inject_tokens']} tokens"
    )
    print(
        f"  WITHOUT dump  ~{session['without_dump_tokens']} tokens "
        f"({', '.join(session['without_files'])})"
    )
    print(
        f"  saved         ~{session['tokens_saved']} tokens "
        f"({session['pct_saved']}%)"
    )
    print()
    print(f"{'task':<16} {'found W/WO':<10} {'tok WITH':>9} {'tok WITHOUT':>12} {'saved%':>7} {'ms W':>8} {'ms WO':>8}")
    print("-" * 80)

    tw = tb = mw = mb = 0
    fw = fb = 0
    for w, o in zip(with_rows, without_rows):
        tw += w.tokens
        tb += o.tokens
        mw += w.ms
        mb += o.ms
        fw += int(w.found)
        fb += int(o.found)
        print(
            f"{w.task_id:<16} {str(w.found):<5}/{str(o.found):<4} "
            f"{w.tokens:>9} {o.tokens:>12} {pct(w.tokens, o.tokens):>6}% "
            f"{w.ms:>7.1f} {o.ms:>7.1f}"
        )

    n = len(with_rows)
    print("-" * 80)
    print(
        f"{'TOTAL':<16} {fw}/{n} / {fb}/{n}  "
        f"{tw:>9} {tb:>12} {pct(tw, tb):>6}% "
        f"{mw:>7.1f} {mb:>7.1f}"
    )
    print()
    print("Summary")
    print(f"  task tokens saved     {tb - tw}  ({pct(tw, tb)}%)")
    print(f"  task time saved       {mb - mw:.1f}ms  ({pct(mw, mb)}%)")
    print(f"  answer hit-rate WITH  {fw}/{n}  WITHOUT {fb}/{n}")
    print(
        f"  combined (session+tasks) WITH ~{int(session['with_harness_inject_tokens']) + tw}  "
        f"WITHOUT ~{int(session['without_dump_tokens']) + tb}"
    )


def write_tsv(
    path: Path,
    with_rows: list[ProbeResult],
    without_rows: list[ProbeResult],
    session: dict[str, object],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        "ts\tscope\ttask_id\tcondition\tfound\tfiles\ttokens\tms\tpaths\n"
    ]
    lines.append(
        f"{ts}\tsession_start\tinject\twith_harness\t1\t1\t"
        f"{session['with_harness_inject_tokens']}\t0\tprogress/status.md\n"
    )
    lines.append(
        f"{ts}\tsession_start\tdump_routers\twithout_harness\t1\t"
        f"{len(session['without_files'])}\t{session['without_dump_tokens']}\t0\t"
        f"{';'.join(session['without_files'])}\n"
    )
    for w, o in zip(with_rows, without_rows):
        for row in (w, o):
            lines.append(
                f"{ts}\ttask\t{row.task_id}\t{row.condition}\t"
                f"{int(row.found)}\t{row.files}\t{row.tokens}\t{row.ms:.2f}\t"
                f"{';'.join(row.paths)}\n"
            )
    path.write_text("".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--tsv",
        type=Path,
        default=ROOT / "docs" / "benchmark-ablation.tsv",
        help="write ablation TSV (default docs/benchmark-ablation.tsv)",
    )
    ap.add_argument("--no-tsv", action="store_true")
    args = ap.parse_args()

    if not MEMORY.is_dir():
        print("error: .memory/ not found", flush=True)
        return 1

    session = session_start_costs()
    with_rows = [run_harness(t) for t in TASKS]
    without_rows = [run_without(t) for t in TASKS]
    print_report(with_rows, without_rows, session)
    if not args.no_tsv:
        write_tsv(args.tsv, with_rows, without_rows, session)
        print(f"wrote → {args.tsv.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
