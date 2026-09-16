# Loop program (optional)

> Human-owned. Edit this file; do not ask the agent to rewrite policy mid-run unless you explicitly want that.
> Keep it short. Optional template — not installed by default.

## Goal

<!-- One sentence: what “done” means for this loop -->
Ship one verified improvement per iteration toward: _

## Metric (mechanical)

- **Pass command:** `npm test`   <!-- or: pytest, go test, etc. -->
- **Success:** exit code 0
- **Fail:** non-zero → discard changes (reset to last good commit) and log why

Do not treat the model’s self-assessment as success.

## Budget (hard stops)

| Gate | Limit |
|------|-------|
| Max iterations this session | 5 |
| No-progress (same failure twice) | stop + handoff |
| Wall-clock / token budget | _fill in_ |

On any hard stop: append to `loop/results.tsv`, write a short note in `.memory/progress/status.md` (or handoff), then **exit**.

## Editable (agent may change)

- `src/**`   <!-- tighten to one file/dir if you want -->

## Sealed (agent must not change)

- `**/test*/**`, `**/*_test.*`, `**/ci/**`, `loop/program.md`
- `.memory/decisions/**` (append-only via human / `/memory-sync` policy)

If a diff touches sealed paths → reject the iteration.

## One iteration

1. Read this file + `.memory/failures/log.md` (if present)
2. Propose one bounded change inside **Editable**
3. Run **Pass command**
4. If pass → commit; append `keep` row to `loop/results.tsv`
5. If fail → reset to last good; append `discard` row; do not widen scope
6. Stop when Goal is met or a hard stop fires

## Results log

Append one line per iteration to `loop/results.tsv`:

```text
timestamp	iteration	verdict	metric_or_exit	note
```
