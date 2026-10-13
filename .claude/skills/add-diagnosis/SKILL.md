---
name: add-diagnosis
description: This skill should be used when adding a new deterministic diagnosis to DEDoc, or extending an existing one with a signal or fixture. Trigger phrases include "add a diagnosis", "new diagnosis", "DEDOC-xxx", "add a signal", "add a fixture".
version: 0.1.0
---

# Add a diagnosis

Deterministic, evidence-backed diagnosis for a data-engineering failure. Follow
every step; `make validate` enforces most of these rules.

## 1. Pick the category and ID

- Categories are dotted lowercase (`spark`, `delta`, `adf`, `connectivity`,
  `performance`, `quality`); the directory matches the category root under
  `diagnoses/<category>/`.
- The ID is `DEDOC-<CATEGORY>-<NNN>` (uppercase). Scan the existing files in
  `diagnoses/<category>/` and take the next number. **IDs are additive and
  never reused, regardless of version.**

## 2. Ensure the signals exist

Every name in `signals.positive` / `signals.negative` must be in
`dedoc/analyzer/signals.py::SIGNAL_REGISTRY`, or validation fails.

- Reuse an existing signal when the pattern is the same.
- Otherwise add a `_sig(...)` entry. Set `exact=True` only for a precise error
  signature (e.g. a `[ERROR_CODE]` token); leave `exact=False` for heuristic
  patterns. Names are snake_case.
- If the failure belongs to a new platform, do the `add-platform` skill first.

## 3. Write the diagnosis YAML

Create `diagnoses/<category>/dedoc-<cat>-<nnn>.yaml` modelled on a neighbour.
Required content: `id`, `name`, `category`, `platforms`, at least one
`patterns.exception_types` or `signals.positive`, at least one `hypotheses`
entry, and at least one `references` entry with a real `url`.

## 4. Add fixtures

- `fixtures/positive/<name>/` — `input.log` (or `input.json`) plus `meta.yaml`
  with `expected.diagnosis_ids` including the new id, plus `status`, `exit_code`,
  and optionally `confidence_band`.
- `fixtures/negative/<name>/` — a benign input that must **not** select the
  diagnosis (guards specificity).
- Reference the positive/negative fixture names in the diagnosis's
  `tests.fixtures`.

## 5. Update counts, catalog, and docs

Keep these in sync with the new total:

- `README.md`, `docs/index.md`
- `docs/reference/diagnosis-catalog.md`
- `docs/reference/diagnosis-reference.md`
- `CHANGELOG.md` (under `[Unreleased]`)

## 6. Verify

```bash
make validate      # schema, signals, fixture references, coverage
make link-check    # reference URLs are reachable
make test
make evaluate      # corpus must pass, no regressions
make benchmark     # refresh results.json + baseline.json
```

Then `make verify`. Do not commit or push unless the user explicitly asks.
