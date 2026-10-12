# Evaluation & benchmarks

DEDoc ships its evaluation framework as a first-class part of the project
(BUILD_PLAN.md §19). It grades the deterministic pipeline against the curated
`fixtures/` corpus and reports the metrics that define quality — so a change is
either an improvement, a regression, or noise, never a guess.

## Run it

```bash
make evaluate        # strict gate used by make verify (and CI)
make benchmark       # writes benchmarks/results.json + benchmarks/baseline.json
```

Or directly:

```bash
python -m dedoc.evaluation --strict --baseline benchmarks/baseline.json
python -m dedoc.evaluation --format json --output benchmarks/results.json
```

The command exits non-zero (when `--strict`) if any case fails or a previously
passing case regressed.

## Metrics

Every value is computed from observable pipeline output compared with each
fixture's `meta.yaml` expectation — never from a model's self-reported
certainty.

| Metric | Meaning |
| --- | --- |
| Diagnosis accuracy | Cases whose full outcome matches the expectation, over all cases. |
| Precision | Of the cases where DEDoc emitted a diagnosis, the fraction that were correct. |
| Recall | Of the applicable (positive) cases, the fraction DEDoc diagnosed correctly. |
| Abstention quality | Of the cases that must abstain or fail cleanly, the fraction done correctly (specificity). |
| Confidence calibration | Positive cases whose top confidence band matches the expected band. |
| Evidence coverage | Diagnosed cases whose top match carries at least one evidence item. |
| Unsupported-claim rate | Diagnosed cases with no evidence or a score below the diagnosis threshold (target: `0`). |
| Remediation coverage | Diagnosed cases whose top match carries at least one recommendation. |
| Regression rate | Of the baseline-passing cases, the fraction that no longer pass. |
| Tool efficiency | Useful evidence per investigation step — only meaningful with context-bearing cases (currently `n/a`). |

A value of `n/a` means the metric has no applicable cases yet.

## Corpus

Each case is a directory under `fixtures/` containing an `input.*` file and a
`meta.yaml` with the expected outcome:

```yaml
expected:
  status: diagnosed
  exit_code: 0
  confidence_band: HIGH
  diagnosis_ids: [DEDOC-SPARK-001]
```

Cases are grouped by `kind`:

- **positive** — a diagnosis is expected (`diagnosis_ids` non-empty).
- **negative** — DEDoc must abstain (`insufficient_evidence`, empty `diagnosis_ids`).
- **malformed** — bad input must be handled tolerantly or fail cleanly (exit code `1`, no traceback).

Adding a fixture automatically enrolls it in the evaluation, the fixtures CLI
test, and the coverage checks.

## Regression baseline

`benchmarks/baseline.json` records which cases passed when it was generated.
Passing `--baseline` compares the current run against it and reports a
regression rate; `make evaluate` uses it as a CI gate. Regenerate it
intentionally with `make benchmark` (or `--write-baseline`) when the corpus
changes.

`benchmarks/results.json` is the published benchmark result for the current
release: it contains the metrics and per-case detail with repository-relative
paths so it is stable to commit.

See [`benchmarks/README.md`](https://github.com/Adez017/Data-Engineer-Doctor/blob/main/benchmarks/README.md)
for the corpus policy (synthetic/sanitized inputs only) and the publishing
workflow. For try-it-now sample inputs that are *not* part of the graded corpus,
see the runnable `examples/` set (`make examples`).
