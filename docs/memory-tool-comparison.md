# Memory tool benchmarks — Knowledge Harness vs peers

Local inject/latency numbers come from `python scripts/benchmark-harness.py --compare`.
Retrieval / QA scores below are **vendor- or survey-published** unless marked measured. They are not independently reproduced in this repo.

## Two different layers

| Layer | What it stores | Examples |
|-------|----------------|----------|
| **Project memory** | Progress, ADRs, features, failures — git-tracked, structured | **Knowledge Harness** (`.memory/`) |
| **Session / agent recall** | Semantic past chats, observations, facts | agentmemory, claude-mem, Mem0, Letta |

Harness deliberately does **not** compete on LongMemEval R@5. Pair it with **one** deep-recall plugin (`claude-mem` *or* `agentmemory`) for that job.

```bash
python scripts/benchmark-harness.py --compare
# → docs/benchmark-results.tsv (local snapshot)
# → docs/benchmark-comparison.tsv (cited + measured rows)
```

## Retrieval / QA (published)

| System | Benchmark | Metric | Value | Notes |
|--------|-----------|--------|-------|-------|
| agentmemory BM25+Vector | LongMemEval-S | R@5 | **95.2%** | Local `all-MiniLM-L6-v2`; author harness |
| agentmemory BM25-only | LongMemEval-S | R@5 | 86.2% | No embeddings |
| MemPalace | LongMemEval-S | R@5 | ~96.6% | Self-reported; not reproduced by agentmemory |
| Letta / MemGPT | LoCoMo | QA | 83.2% / 74.0% | Vendor-cited vs Letta filesystem agent |
| Mem0 base | LoCoMo | QA | 66.9% | p95 ~1.44s; ~1.8–2K tok/conv |
| Mem0g graph | LoCoMo | QA | 68.5% | p95 ~2.59s; ~4K tok/conv |
| claude-mem | — | progressive disclose | ~10× vs full history | No public LongMemEval number |
| **knowledge-harness** | — | LongMemEval | **n/a** | Not a chat-retrieval engine |

**Caveat:** LongMemEval ≠ LoCoMo. Vendors disagree on methodology; treat percentages as ballpark claims.

## Token / latency (operational — fairer comparison)

| System | Typical inject / query cost | Latency | Infra cost |
|--------|----------------------------|---------|------------|
| **knowledge-harness** (measured) | **&lt;500 tok** session inject (budget) | **~40–50ms** inject; ~1.2–1.4s sync | $0 local |
| Built-in CLAUDE.md / MEMORY.md | 22K+ tok at ~240 observations | Always-on full file | $0 |
| agentmemory | ~1.9K tok/session (budgeted) | Hook / MCP | $0 local emb / ~$10/yr API |
| claude-mem | L1 ~50–100 · L2 ~500–1K tok | Hook | Survey ~$60–180/yr |
| Mem0 base | ~1.8–2K tok/conv | p95 ~1.44s | Cloud or self-host + LLM extract |
| Full history paste | 19.5M+ tok/year (heavy use) | n/a | Impossible at scale |

## Ablation: harness ON vs OFF (measured)

Run: `python scripts/benchmark-ablation.py` → `docs/benchmark-ablation.tsv`

Simulates answering 8 fixed project questions. **WITH** follows `.memory/` entry points. **WITHOUT** excludes `.memory/` and harness routers (`AGENTS.md` / `CLAUDE.md`) and blind-searches the repo.

| Metric | WITH harness | WITHOUT | Saved |
|--------|--------------|---------|-------|
| Task tokens (8 questions) | ~4,278 | ~163,538 | **~97.4%** |
| Task wall time | ~0.7ms | ~146ms | **~99.5%** |
| Answer hit-rate | **8/8** | 7/8 | +1 correct |
| Session inject vs README dump | ~390 tok | ~464 tok | ~16% (small — win is mid-task) |

Combined session+tasks: **~4.7K vs ~164K tokens** (~97% less).

This measures **token effectiveness of project recall**, not LongMemEval chat retrieval.

## Recommended stack

```
Knowledge Harness (.memory/)     ← project spine (this repo)
        +
ONE of: claude-mem | agentmemory ← semantic session history
        +
graphify                         ← code discovery (not memory)
```

Do **not** install both deep-recall plugins (double inject). See ADR: one deep-recall plugin.

## Sources

- [agentmemory COMPARISON.md](https://github.com/rohitg00/agentmemory/blob/main/benchmark/COMPARISON.md)
- [agentmemory LONGMEMEVAL.md](https://github.com/rohitg00/agentmemory/blob/main/benchmark/LONGMEMEVAL.md)
- [LongMemEval](https://arxiv.org/abs/2410.10813) · [LoCoMo](https://snap-stanford.github.io/LoCoMo/)
- [Mem0 LoCoMo writeup](https://mem0.ai/blog/benchmarked-openai-memory-vs-langmem-vs-memgpt-vs-mem0-for-long-term-memory-here-s-how-they-stacked-up)
- [Letta filesystem LoCoMo](https://www.letta.com/blog/benchmarking-ai-agent-memory/)
- [Claude Code memory systems survey](https://cc.bruniaux.com/guide/memory-systems/)
