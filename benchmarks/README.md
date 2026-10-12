# Benchmarks

The benchmark corpus grades DEDoc's diagnostic pipeline end to end. It is the
corpus referenced by the evaluation framework
(`docs/reference/evaluation.md` / `make evaluate`) and by the Definition of Done.

## Corpus

Cases live in `fixtures/` — no separate copy is maintained here. They are
grouped by intent:

- `fixtures/positive/` — a real-world-style failure that must be diagnosed with
  the expected ID (`40` cases).
- `fixtures/negative/` — healthy/benign logs where DEDoc must **abstain**
  (`insufficient_evidence`) rather than guess (`3` cases).
- `fixtures/malformed/` — empty, binary, or truncated input where DEDoc must
  fail safely without crashing (`3` cases).

All inputs are synthetic or derived from public error messages. Do **not** add
private customer logs without explicit permission and sanitization.

## Metrics

`python -m dedoc.evaluation` reports:

| Metric | Meaning |
| --- | --- |
| Diagnosis accuracy | Fraction of cases with the expected outcome |
| Precision / Recall | Correct diagnoses vs. produced / expected |
| Abstention quality | Negatives and malformed inputs correctly left undiagnosed |
| Confidence calibration | Expected band matches the case's expected band |
| Evidence coverage | Cases with at least one cited evidence signal |
| Unsupported-claim rate | Diagnosed cases with no supporting signal |
| Remediation coverage | Cases that include recommended next actions |
| Regression rate | `null` unless a baseline is supplied to compare against |
| Tool efficiency | `null` — not applicable to the local (no-tooling) path |

## Artifacts

| File | Purpose |
| --- | --- |
| `baseline.json` | One `name -> ok` entry per case. Committed and used by `make evaluate` to detect regressions. |
| `results.json` | Full run: metrics plus per-case details. Committed for reproducibility. |

Regenerate both after any change to diagnoses, signals, or the corpus:

```bash
make benchmark         # writes results.json and refreshes baseline.json
make evaluate          # strict: fails on any regression vs. baseline.json
```

`make verify` runs `evaluate`, so a regressed case fails CI. Update the baseline
only when the new behavior is intentional, and call it out in the changelog.

## Publishing

`results.json` is the artifact cited in releases and the README, so the project
can be evaluated on engineering merit. Keep it in sync with the released tag.
