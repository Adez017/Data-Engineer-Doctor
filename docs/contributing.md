# Contributing

Thanks for wanting to improve Data Engineer Doctor. This page is the quick
guide; the canonical rules live in
[`CONTRIBUTING.md`](https://github.com/Adez017/Data-Engineer-Doctor/blob/main/CONTRIBUTING.md)
and the implementation source of truth is
[`BUILD_PLAN.md`](https://github.com/Adez017/Data-Engineer-Doctor/blob/main/BUILD_PLAN.md).

## Development setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
make verify
```

`make verify` is the single gate CI runs: formatting, lint, strict typing,
tests, knowledge-base validation, evaluation, link-check, docs build,
dependency audit, and package build.

## Ground rules

- Inspect existing code, tests, and docs before editing.
- Prefer small, vertical slices that produce a working, tested capability.
- Never declare completion without `make verify` passing.
- If a requirement is ambiguous, document the ambiguity and stop rather than
  inventing behavior.
- Public diagnosis IDs (for example `DEDOC-SCHEMA-001`) are part of the public
  API and must not be renamed or repurposed.
- Never invent error messages, error codes, or documentation URLs. A signature
  must be validated against real, official wording or labelled as an unverified
  hypothesis.

## Adding a diagnosis

1. **Register the signals.** Add any new pattern to `SIGNAL_REGISTRY` in
   `dedoc/analyzer/signals.py`. Mark it `exact=True` only when it is a verified
   error signature (scores 40 instead of 15). `make validate` rejects signals
   with no extractor.
2. **Write the YAML** under `diagnoses/<category>/`: exception patterns,
  positive/negative signals, at least one hypothesis, an official reference,
   and a `tests.fixtures` list.
3. **Add fixtures** under `fixtures/` (see below).
- Run `make verify`. Coverage is enforced: every diagnosis must be exercised by
  at least one positive fixture, and every reference URL must be reachable.

## Fixture layout

```text
fixtures/
├── positive/<name>/     # must be diagnosed as <expected.diagnosis_ids>
│   ├── input.log
│   └── meta.yaml
├── negative/<name>/     # must abstain (no false positives)
│   ├── input.log
│   └── meta.yaml
└── malformed/<name>/    # must not crash the tool
    ├── input.json
    └── meta.yaml
```

`meta.yaml`:

```yaml
name: spark-schema-mismatch-resolved-column
kind: positive              # positive | negative | malformed
description: What failure this fixture represents.
expected:
  status: diagnosed          # diagnosed | insufficient_evidence | input_error
  exit_code: 0               # 0 for reports, 1 for clean input errors
  confidence_band: HIGH      # HIGH | MEDIUM (positive fixtures only)
  diagnosis_ids:
    - DEDOC-SCHEMA-001
```

Fixture rules (enforced by `tests/unit/test_fixtures.py`):

- **Positive**: `status: diagnosed`, `exit_code: 0`, non-empty
  `diagnosis_ids`, and a `confidence_band` matching the top match.
- **Negative**: `status: insufficient_evidence`, empty `diagnosis_ids`.
- **Malformed**: `status: input_error` with `exit_code: 1`, or
  `status: insufficient_evidence` with `exit_code: 0`; never a traceback.

Adding a fixture automatically enrolls it in the evaluation corpus and coverage
checks. See [Evaluation & benchmarks](reference/evaluation.md).

## What never to do

- Do not claim root-cause certainty without supporting evidence.
- Do not invent error messages, codes, or documentation URLs.
- Do not add behavior that mutates production resources.
- Do not rename or repurpose a released diagnosis ID.

## Pull requests

- Keep PRs small and focused.
- Run `make verify` locally before opening a PR.
- Update documentation with every behavior change.
- Report security issues privately — see
  [Security & privacy](explanation/security-model.md), not a public issue.

!!! tip "See also"
    - [Evaluation & benchmarks](reference/evaluation.md)
    - [Full diagnosis reference](reference/diagnosis-reference.md)
    - [Architecture overview](explanation/architecture.md)
