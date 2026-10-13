---
name: run-evals
description: This skill should be used when grading the pipeline against the fixtures corpus, reading evaluation metrics, adding evaluation cases, or updating regression baselines. Trigger phrases include "run evals", "evaluation", "benchmark", "baseline", "regression".
version: 0.1.0
---

# Run the evaluation

`DEDoc` grades itself against the fixture corpus (§19). The corpus is every
directory under `fixtures/` that has an `input.*` file and a `meta.yaml`
describing the expected outcome.

## Commands

```bash
make evaluate     # grade against corpus with --strict, compare baseline
make benchmark    # write benchmarks/results.json and benchmarks/baseline.json
python -m dedoc.evaluation --help
```

- `make evaluate` exits non-zero under `--strict` when any case fails or
  regresses against `benchmarks/baseline.json`.
- `make benchmark` regenerates results and the regression baseline. Only do
  this when the corpus legitimately changed.

## Reading results

Metrics reported include status/exit-code accuracy, diagnosis-id precision and
recall, confidence calibration, evidence coverage, unsupported-claim rate, and
regression rate. Investigate any non-`n/a` failure; do not "fix" a metric by
weakening a fixture.

## Adding a case

1. Create `fixtures/<positive|negative|malformed>/<name>/` with an `input.*`
   and a `meta.yaml` (`expected.status`, `expected.exit_code`,
   `expected.diagnosis_ids`, optional `expected.confidence_band`).
2. `make validate` (fixture references and coverage).
3. `make evaluate`, then `make benchmark` to refresh the baseline.

## Hygiene

- Baselines live in `benchmarks/`; keep them in sync with the corpus and commit
  them together with the fixture changes.
- New diagnosis ids must be covered by a positive fixture's
  `expected.diagnosis_ids`.
