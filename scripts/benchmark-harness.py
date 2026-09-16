#!/usr/bin/env python3
"""Snapshot latency + size metrics for Knowledge Harness long-term memory.

Measures:
  - session inject (progress/status.md via inject-context.js)
  - capture-decisions hook (noop event)
  - harness-sync.py --skip-graphify
  - .memory/ corpus inventory (active vs archive)

With --compare, also prints cited competitor memory-tool benchmarks
(LongMemEval / LoCoMo / token overhead) alongside our measured numbers.

Usage:
  python scripts/benchmark-harness.py
  python scripts/benchmark-harness.py --runs 20 --json
  python scripts/benchmark-harness.py --compare
  python scripts/benchmark-harness.py --tsv docs/benchmark-results.tsv
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MEMORY = ROOT / ".memory"
HOOKS = ROOT / ".cursor" / "hooks"
TOKEN_BUDGET = 500
FM_RE = re.compile(r"^---\s*\n.*?\n---\s*\n", re.DOTALL)

# Published competitor numbers (vendor / survey cited). Not independently
# reproduced here. Harness is structured project memory — pair with one
# deep-recall plugin for semantic session history; do not treat R@5 as
# an apples-to-apples score for .memory/ inject.
COMPETITOR_ROWS: list[dict[str, str]] = [
    {
        "system": "agentmemory (BM25+Vector)",
        "layer": "session-recall",
        "benchmark": "LongMemEval-S",
        "metric": "R@5",
        "value": "95.2",
        "unit": "pct",
        "latency": "~hook / MCP",
        "inject_tokens": "~1900/session (budgeted)",
        "cost": "$0 local emb / ~$10/yr API",
        "source": "rohitg00/agentmemory benchmark/COMPARISON.md",
        "reproduced": "no",
        "notes": "own harness; all-MiniLM-L6-v2; retrieval-only",
    },
    {
        "system": "agentmemory (BM25-only)",
        "layer": "session-recall",
        "benchmark": "LongMemEval-S",
        "metric": "R@5",
        "value": "86.2",
        "unit": "pct",
        "latency": "local",
        "inject_tokens": "top-K only",
        "cost": "$0",
        "source": "rohitg00/agentmemory benchmark/LONGMEMEVAL.md",
        "reproduced": "no",
        "notes": "fallback without embeddings",
    },
    {
        "system": "MemPalace",
        "layer": "session-recall",
        "benchmark": "LongMemEval-S",
        "metric": "R@5",
        "value": "~96.6",
        "unit": "pct",
        "latency": "vector",
        "inject_tokens": "n/a",
        "cost": "$0 OSS",
        "source": "vendor via agentmemory COMPARISON.md",
        "reproduced": "no",
        "notes": "self-reported; no hooks/MCP surface",
    },
    {
        "system": "Letta / MemGPT",
        "layer": "agent-runtime",
        "benchmark": "LoCoMo",
        "metric": "QA acc",
        "value": "83.2 / 74.0",
        "unit": "pct",
        "latency": "model-dep",
        "inject_tokens": "tiered paging",
        "cost": "runtime + LLM",
        "source": "vendor / Letta filesystem blog",
        "reproduced": "no",
        "notes": "83.2 vendor-cited; Letta FS agent 74.0 GPT-4o-mini",
    },
    {
        "system": "Mem0 (base)",
        "layer": "memory-API",
        "benchmark": "LoCoMo",
        "metric": "QA acc",
        "value": "66.9",
        "unit": "pct",
        "latency": "p95 ~1.44s",
        "inject_tokens": "~1.8–2K/conv",
        "cost": "cloud or self-host + LLM extract",
        "source": "mem0.ai blog / arXiv 2504.19413",
        "reproduced": "no",
        "notes": "extraction-based; independent reruns vary",
    },
    {
        "system": "Mem0g (graph)",
        "layer": "memory-API",
        "benchmark": "LoCoMo",
        "metric": "QA acc",
        "value": "68.5",
        "unit": "pct",
        "latency": "p95 ~2.59s",
        "inject_tokens": "~4K/conv",
        "cost": "often Pro-tier",
        "source": "mem0.ai blog",
        "reproduced": "no",
        "notes": "graph variant; not LongMemEval",
    },
    {
        "system": "claude-mem",
        "layer": "session-recall",
        "benchmark": "—",
        "metric": "progressive disclosure",
        "value": "~10x vs full history",
        "unit": "ratio",
        "latency": "hook",
        "inject_tokens": "L1 50–100 / L2 500–1K",
        "cost": "~$60–180/yr (survey)",
        "source": "cc.bruniaux.com memory-systems guide",
        "reproduced": "no",
        "notes": "Claude Code plugin; no public LongMemEval number",
    },
    {
        "system": "Built-in CLAUDE.md / MEMORY.md",
        "layer": "native",
        "benchmark": "scale anecdote",
        "metric": "inject tokens @240 obs",
        "value": "22000+",
        "unit": "tokens",
        "latency": "0 (always-on)",
        "inject_tokens": "full file every session",
        "cost": "$0 infra",
        "source": "agentmemory README comparison",
        "reproduced": "no",
        "notes": "200-line / 25KB caps; no selective retrieval",
    },
    {
        "system": "Full conversation paste",
        "layer": "baseline",
        "benchmark": "token cost",
        "metric": "tokens/year (heavy use)",
        "value": "19500000+",
        "unit": "tokens",
        "latency": "n/a",
        "inject_tokens": "all history",
        "cost": "impossible at scale",
        "source": "agentmemory COMPARISON.md",
        "reproduced": "no",
        "notes": "exceeds context after ~200 observations",
    },
]


def estimate_tokens(text: str) -> int:
    return max(1, math.ceil(len(text) / 4)) if text else 0


def strip_frontmatter(text: str) -> str:
    m = FM_RE.match(text)
    return (text[m.end() :] if m else text).strip()


def percentile(sorted_vals: list[float], p: float) -> float:
    if not sorted_vals:
        return 0.0
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    k = (len(sorted_vals) - 1) * (p / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_vals[int(k)]
    return sorted_vals[f] * (c - k) + sorted_vals[c] * (k - f)


def summarize_ms(samples: list[float]) -> dict[str, float]:
    ordered = sorted(samples)
    return {
        "n": float(len(samples)),
        "mean_ms": statistics.fmean(samples) if samples else 0.0,
        "p50_ms": percentile(ordered, 50),
        "p95_ms": percentile(ordered, 95),
        "min_ms": ordered[0] if ordered else 0.0,
        "max_ms": ordered[-1] if ordered else 0.0,
    }


def time_cmd(
    argv: list[str],
    *,
    runs: int,
    cwd: Path,
    stdin: str | None = None,
    env: dict[str, str] | None = None,
) -> tuple[list[float], str, int]:
    times: list[float] = []
    last_out = ""
    last_code = 0
    for _ in range(runs):
        t0 = time.perf_counter()
        proc = subprocess.run(
            argv,
            cwd=cwd,
            input=stdin,
            text=True,
            capture_output=True,
            env=env,
        )
        times.append((time.perf_counter() - t0) * 1000.0)
        last_out = proc.stdout or ""
        last_code = proc.returncode
    return times, last_out, last_code


def dir_stats(path: Path) -> dict[str, int | float]:
    if not path.exists():
        return {"files": 0, "bytes": 0, "tokens_est": 0}
    files = 0
    nbytes = 0
    tokens = 0
    for p in path.rglob("*"):
        if not p.is_file():
            continue
        if p.name.startswith("."):
            continue
        files += 1
        data = p.read_bytes()
        nbytes += len(data)
        if p.suffix.lower() in {".md", ".json", ".jsonl", ".html", ".txt"}:
            try:
                tokens += estimate_tokens(data.decode("utf-8", errors="ignore"))
            except Exception:
                pass
    return {"files": files, "bytes": nbytes, "tokens_est": tokens}


def inventory() -> dict[str, object]:
    sections = {
        "progress": MEMORY / "progress",
        "context": MEMORY / "context",
        "decisions": MEMORY / "decisions",
        "features": MEMORY / "features",
        "failures": MEMORY / "failures",
        "meta": MEMORY / "meta",
        "domains": MEMORY / "domains",
    }
    out: dict[str, object] = {}
    total_files = 0
    total_bytes = 0
    total_tokens = 0
    for name, path in sections.items():
        active = dir_stats(path)
        archive = dir_stats(path / "archive") if path.is_dir() else {
            "files": 0,
            "bytes": 0,
            "tokens_est": 0,
        }
        # Subtract archive from active when archive is nested under section
        if path.is_dir() and (path / "archive").is_dir():
            active = {
                "files": int(active["files"]) - int(archive["files"]),
                "bytes": int(active["bytes"]) - int(archive["bytes"]),
                "tokens_est": int(active["tokens_est"]) - int(archive["tokens_est"]),
            }
        out[name] = {"active": active, "archive": archive}
        total_files += int(active["files"]) + int(archive["files"])
        total_bytes += int(active["bytes"]) + int(archive["bytes"])
        total_tokens += int(active["tokens_est"]) + int(archive["tokens_est"])

    status = MEMORY / "progress" / "status.md"
    archive = MEMORY / "progress" / "archive.md"
    index = MEMORY / "index.md"
    journal = MEMORY / "session-journal.jsonl"

    inject_body = ""
    if status.exists():
        inject_body = strip_frontmatter(status.read_text(encoding="utf-8"))
    inject_tokens = estimate_tokens(
        f"## Resumed session — project progress\n\n{inject_body}"
    )

    out["totals"] = {
        "files": total_files,
        "bytes": total_bytes,
        "tokens_est": total_tokens,
    }
    out["session_inject"] = {
        "path": str(status.relative_to(ROOT)) if status.exists() else None,
        "chars": len(inject_body),
        "tokens_est": inject_tokens,
        "budget": TOKEN_BUDGET,
        "over_budget": inject_tokens > TOKEN_BUDGET,
    }
    out["progress_archive_tokens"] = (
        estimate_tokens(strip_frontmatter(archive.read_text(encoding="utf-8")))
        if archive.exists()
        else 0
    )
    out["index_reported"] = None
    if index.exists():
        m = re.search(
            r"Estimated injection size:\s*~(\d+)\s*tokens",
            index.read_text(encoding="utf-8"),
        )
        if m:
            out["index_reported"] = int(m.group(1))
    out["journal_lines"] = (
        sum(1 for _ in journal.open(encoding="utf-8")) if journal.exists() else 0
    )
    return out


def run_benchmark(runs: int) -> dict[str, object]:
    env = os.environ.copy()
    env["CURSOR_PROJECT_DIR"] = str(ROOT)

    inject = HOOKS / "inject-context.js"
    capture = HOOKS / "capture-decisions.js"
    sync_py = ROOT / "scripts" / "harness-sync.py"

    results: dict[str, object] = {
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "root": str(ROOT),
        "runs": runs,
        "token_budget": TOKEN_BUDGET,
    }

    # --- inject-context ---
    if inject.exists():
        payload = json.dumps({"cwd": str(ROOT), "workspace_roots": [str(ROOT)]})
        times, out, code = time_cmd(
            ["node", str(inject)],
            runs=runs,
            cwd=ROOT,
            stdin=payload,
            env=env,
        )
        injected_tokens = 0
        try:
            data = json.loads(out) if out.strip() else {}
            ctx = data.get("additional_context") or data.get("additionalContext") or ""
            injected_tokens = estimate_tokens(ctx)
        except json.JSONDecodeError:
            injected_tokens = estimate_tokens(out)
        results["inject_context"] = {
            **summarize_ms(times),
            "exit_code": code,
            "injected_tokens_est": injected_tokens,
            "over_budget": injected_tokens > TOKEN_BUDGET,
        }
    else:
        results["inject_context"] = {"error": "missing hook"}

    # --- capture-decisions (noop: no write / no install) ---
    if capture.exists():
        # Path under .memory/ so capture skips journal writes
        noop = json.dumps(
            {
                "cwd": str(ROOT),
                "hook_event_name": "afterFileEdit",
                "file_path": str(MEMORY / "progress" / "status.md"),
            }
        )
        times, _, code = time_cmd(
            ["node", str(capture)],
            runs=runs,
            cwd=ROOT,
            stdin=noop,
            env=env,
        )
        results["capture_decisions_noop"] = {**summarize_ms(times), "exit_code": code}
    else:
        results["capture_decisions_noop"] = {"error": "missing hook"}

    # --- harness-sync (skip graphify for stable local snapshot) ---
    if sync_py.exists():
        times, _, code = time_cmd(
            [sys.executable, str(sync_py), "--skip-graphify"],
            runs=max(1, min(runs, 5)),  # sync is heavier; cap repeats
            cwd=ROOT,
            env=env,
        )
        results["harness_sync_skip_graphify"] = {
            **summarize_ms(times),
            "exit_code": code,
            "note": "capped at 5 runs",
        }
    else:
        results["harness_sync_skip_graphify"] = {"error": "missing script"}

    results["corpus"] = inventory()
    return results


def fmt_ms(v: float) -> str:
    return f"{v:.2f}"


def print_report(r: dict[str, object]) -> None:
    print("Knowledge Harness — long-term memory benchmark")
    print(f"ts: {r['ts']}  runs: {r['runs']}  budget: <{r['token_budget']} tokens")
    print()

    inj = r.get("inject_context", {})
    if "error" not in inj:
        flag = "OVER" if inj.get("over_budget") else "ok"
        print("Session inject (inject-context.js)")
        print(
            f"  latency  mean={fmt_ms(inj['mean_ms'])}ms  "
            f"p50={fmt_ms(inj['p50_ms'])}ms  p95={fmt_ms(inj['p95_ms'])}ms  "
            f"min={fmt_ms(inj['min_ms'])}ms  max={fmt_ms(inj['max_ms'])}ms"
        )
        print(
            f"  tokens   ~{inj['injected_tokens_est']} injected  "
            f"[{flag}] target <{TOKEN_BUDGET}"
        )
    else:
        print(f"Session inject: {inj['error']}")
    print()

    cap = r.get("capture_decisions_noop", {})
    if "error" not in cap:
        print("Capture hook (noop, no journal write)")
        print(
            f"  latency  mean={fmt_ms(cap['mean_ms'])}ms  "
            f"p50={fmt_ms(cap['p50_ms'])}ms  p95={fmt_ms(cap['p95_ms'])}ms"
        )
    print()

    sync = r.get("harness_sync_skip_graphify", {})
    if "error" not in sync:
        print("harness-sync.py --skip-graphify")
        print(
            f"  latency  mean={fmt_ms(sync['mean_ms'])}ms  "
            f"p50={fmt_ms(sync['p50_ms'])}ms  p95={fmt_ms(sync['p95_ms'])}ms  "
            f"max={fmt_ms(sync['max_ms'])}ms"
        )
    print()

    corpus = r.get("corpus", {})
    si = corpus.get("session_inject", {})
    totals = corpus.get("totals", {})
    print("Long-term corpus (.memory/)")
    print(
        f"  totals   {totals.get('files', 0)} files  "
        f"{totals.get('bytes', 0):,} bytes  "
        f"~{totals.get('tokens_est', 0)} tokens (all readable)"
    )
    print(
        f"  inject   status.md ~{si.get('tokens_est', 0)} tokens  "
        f"(index reports ~{corpus.get('index_reported')})  "
        f"archive.md ~{corpus.get('progress_archive_tokens', 0)} tokens  "
        f"journal {corpus.get('journal_lines', 0)} lines"
    )
    for name in ("progress", "decisions", "features", "context", "meta", "failures", "domains"):
        sec = corpus.get(name)
        if not isinstance(sec, dict):
            continue
        active = sec.get("active", {})
        archive = sec.get("archive", {})
        if int(active.get("files", 0)) == 0 and int(archive.get("files", 0)) == 0:
            continue
        print(
            f"  {name:<10} active={active.get('files', 0)} files/~{active.get('tokens_est', 0)} tok  "
            f"archive={archive.get('files', 0)} files/~{archive.get('tokens_est', 0)} tok"
        )


def append_tsv(path: Path, r: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    inj = r.get("inject_context", {})
    cap = r.get("capture_decisions_noop", {})
    sync = r.get("harness_sync_skip_graphify", {})
    corpus = r.get("corpus", {})
    si = corpus.get("session_inject", {})
    totals = corpus.get("totals", {})
    header = (
        "ts\truns\tinject_mean_ms\tinject_p95_ms\tinject_tokens\tinject_over_budget\t"
        "capture_mean_ms\tsync_mean_ms\tsync_p95_ms\t"
        "corpus_files\tcorpus_bytes\tcorpus_tokens\t"
        "index_reported_tokens\tjournal_lines\n"
    )
    row = (
        f"{r['ts']}\t{r['runs']}\t"
        f"{inj.get('mean_ms', '')}\t{inj.get('p95_ms', '')}\t"
        f"{inj.get('injected_tokens_est', si.get('tokens_est', ''))}\t"
        f"{int(bool(inj.get('over_budget', si.get('over_budget'))))}\t"
        f"{cap.get('mean_ms', '')}\t"
        f"{sync.get('mean_ms', '')}\t{sync.get('p95_ms', '')}\t"
        f"{totals.get('files', '')}\t{totals.get('bytes', '')}\t{totals.get('tokens_est', '')}\t"
        f"{corpus.get('index_reported', '')}\t{corpus.get('journal_lines', '')}\n"
    )
    write_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", encoding="utf-8") as f:
        if write_header:
            f.write(header)
        f.write(row)


def harness_compare_row(r: dict[str, object]) -> dict[str, str]:
    inj = r.get("inject_context", {})
    corpus = r.get("corpus", {})
    si = corpus.get("session_inject", {}) if isinstance(corpus, dict) else {}
    tokens = inj.get("injected_tokens_est", si.get("tokens_est", ""))
    mean_ms = inj.get("mean_ms", "")
    return {
        "system": "knowledge-harness",
        "layer": "project-memory",
        "benchmark": "local-inject",
        "metric": "session_inject_tokens",
        "value": str(tokens),
        "unit": "tokens",
        "latency": f"mean {fmt_ms(float(mean_ms))}ms" if mean_ms != "" else "n/a",
        "inject_tokens": f"~{tokens} (budget <{TOKEN_BUDGET})",
        "cost": "$0 local",
        "source": "scripts/benchmark-harness.py (measured)",
        "reproduced": "yes",
        "notes": (
            "OKF .memory/ spine — not LongMemEval retrieval; "
            "pair with claude-mem OR agentmemory for semantic recall"
        ),
    }


def comparison_rows(r: dict[str, object]) -> list[dict[str, str]]:
    return [harness_compare_row(r), *COMPETITOR_ROWS]


def print_comparison(r: dict[str, object]) -> None:
    rows = comparison_rows(r)
    print()
    print("=" * 72)
    print("Competitive memory-tool benchmarks (cited + measured)")
    print("=" * 72)
    print()
    print(
        "Layers differ: knowledge-harness = structured project memory (.memory/). "
        "agentmemory / claude-mem / Mem0 / Letta = session or agent recall. "
        "LongMemEval R@5 and LoCoMo QA are NOT comparable to harness inject tokens."
    )
    print()
    print(f"{'System':<28} {'Bench':<16} {'Metric':<22} {'Value':<14} {'Inject / cost'}")
    print("-" * 100)
    for row in rows:
        print(
            f"{row['system']:<28} {row['benchmark']:<16} {row['metric']:<22} "
            f"{row['value']:<14} {row['inject_tokens']}"
        )
    print()
    print("Operational axes (fairer for harness)")
    print("-" * 72)
    inj = r.get("inject_context", {})
    sync = r.get("harness_sync_skip_graphify", {})
    print(
        f"  harness session inject   ~{inj.get('injected_tokens_est', '?')} tok / "
        f"{fmt_ms(float(inj['mean_ms'])) if 'mean_ms' in inj else '?'}ms mean  "
        f"[budget <{TOKEN_BUDGET}]"
    )
    if "mean_ms" in sync:
        print(
            f"  harness sync (no graph)  {fmt_ms(float(sync['mean_ms']))}ms mean"
        )
    print("  agentmemory vs CLAUDE.md  ~1.9K tok/session vs 22K+ @240 obs (vendor)")
    print("  Mem0 base                 ~1.8–2K tok/conv · p95 ~1.44s (vendor)")
    print("  claude-mem L1 search      ~50–100 tok progressive disclose (survey)")
    print("  Recommended stack         harness + ONE of {claude-mem, agentmemory}")
    print()
    print("Sources: agentmemory COMPARISON.md / LONGMEMEVAL.md; mem0.ai; Letta blog;")
    print("         cc.bruniaux.com memory-systems; arXiv 2410.10813 (LongMemEval),")
    print("         snap-stanford LoCoMo. Vendor numbers not independently reproduced.")


def write_comparison_tsv(path: Path, r: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = (
        "ts\tsystem\tlayer\tbenchmark\tmetric\tvalue\tunit\tlatency\t"
        "inject_tokens\tcost\tsource\treproduced\tnotes\n"
    )
    lines = [header]
    for row in comparison_rows(r):
        lines.append(
            f"{r['ts']}\t{row['system']}\t{row['layer']}\t{row['benchmark']}\t"
            f"{row['metric']}\t{row['value']}\t{row['unit']}\t{row['latency']}\t"
            f"{row['inject_tokens']}\t{row['cost']}\t{row['source']}\t"
            f"{row['reproduced']}\t{row['notes']}\n"
        )
    path.write_text("".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--runs", type=int, default=15, help="hook timing repeats (default 15)")
    ap.add_argument("--json", action="store_true", help="print full JSON result")
    ap.add_argument(
        "--compare",
        action="store_true",
        help="print cited competitor benchmarks alongside measured harness metrics",
    )
    ap.add_argument(
        "--tsv",
        type=Path,
        default=ROOT / "docs" / "benchmark-results.tsv",
        help="append one row to TSV (default docs/benchmark-results.tsv)",
    )
    ap.add_argument(
        "--comparison-tsv",
        type=Path,
        default=ROOT / "docs" / "benchmark-comparison.tsv",
        help="write competitive comparison TSV (default docs/benchmark-comparison.tsv)",
    )
    ap.add_argument("--no-tsv", action="store_true", help="skip TSV append")
    args = ap.parse_args()

    if not MEMORY.is_dir():
        print("error: .memory/ not found — run from a harness project", file=sys.stderr)
        return 1

    result = run_benchmark(max(1, args.runs))
    if args.compare:
        result["comparison"] = comparison_rows(result)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_report(result)
        if args.compare:
            print_comparison(result)
    if not args.no_tsv:
        append_tsv(args.tsv, result)
        print()
        print(f"appended → {args.tsv.relative_to(ROOT)}")
        if args.compare:
            write_comparison_tsv(args.comparison_tsv, result)
            print(f"wrote    → {args.comparison_tsv.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())