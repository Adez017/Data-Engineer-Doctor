# Contributing to Data Engineer Doctor

Thank you for your interest in contributing.

## Source of truth

[BUILD_PLAN.md](BUILD_PLAN.md) is the implementation source of truth.
Read it before contributing. Do not implement future phases unless explicitly
asked to advance.

## Ground rules

- Inspect existing code, tests, and documentation before editing.
- Prefer small, vertical slices that produce a working, tested capability.
- Never declare completion without running the required verification command:

  ```bash
  make verify
  ```

- Every new diagnosis must include positive, negative, and regression fixtures.
- If a requirement is ambiguous, document the ambiguity and stop rather than
  inventing behavior.
- Public diagnosis IDs (for example `DEDOC-SCHEMA-001`) are part of the public
  API and must not be casually renamed.

## Development setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
make verify
```

## Adding a diagnosis (Phase 2+)

A diagnosis PR must contain:

1. A YAML definition under `diagnoses/<category>/` following the schema in
   [BUILD_PLAN.md](BUILD_PLAN.md) §6.
2. Positive, negative, and regression fixtures under `fixtures/`.
3. Tests wiring those fixtures into the diagnosis loader and rule engine.
4. Documentation, including official references where available.

Every signal name used in a diagnosis YAML must be registered in
`dedoc/analyzer/signals.py` (`SIGNAL_REGISTRY`, a `SignalDef(pattern, exact)`
map); `make validate` rejects signals that have no extractor. Mark a signal
`exact=True` only when its pattern is a verified error signature: exact
signals score 40 (`ERROR_SIGNATURE`) instead of 15 (`CORRELATED_SIGNAL`).
A diagnosis with declared positive signals only matches when at least one
of them is observed (exception-only matches are allowed only when the
diagnosis declares no positive signals).

### Fixture layout

```
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

`meta.yaml` format:

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

- Positive fixtures: `status: diagnosed`, `exit_code: 0`, non-empty
  `diagnosis_ids`, and `confidence_band: HIGH|MEDIUM` matching the top
  match of the report.
- Negative fixtures: `status: insufficient_evidence`, empty `diagnosis_ids`.
- Malformed fixtures: `status: input_error` with `exit_code: 1`, or
  `status: insufficient_evidence` with `exit_code: 0`; never a traceback.

## Pull requests

- Keep PRs small and focused.
- Ensure `make verify` passes locally before opening a PR.
- Update documentation with every behavior change.
