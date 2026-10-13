---
name: add-platform
description: This skill should be used when adding a new platform/engine adapter to DEDoc (for example Microsoft Fabric or Airflow/dbt), including detection markers, signals, diagnoses, catalog grouping, and fixtures. Trigger phrases include "add platform", "new platform adapter", "support Fabric", "support Airflow".
version: 0.1.0
---

# Add a platform adapter

A platform is: detection markers, a set of signals, a group of diagnoses, and
fixtures. The existing `adf` adapter is the reference implementation.

## 1. Platform detection

In `dedoc/analyzer/signals.py`:

- Add a `_<PLATFORM>_MARKERS` tuple of lowercase substrings that uniquely
  identify the platform in raw logs.
- Insert a branch in `detect_platform(...)` in the correct **priority order**.
  Current order is `databricks -> adf -> spark`; place the new platform where
  its markers could not be shadowed by a broader platform, and document why.

## 2. Signals

Add the new platform's named signals to `SIGNAL_REGISTRY` with `_sig(...)`.
Prefer `exact=True` for precise error codes; otherwise `exact=False`.

## 3. Diagnoses

- Create `diagnoses/<platform>/` and add `dedoc-<cat>-<nnn>.yaml` files using
  the `add-diagnosis` skill (schema, hypotheses, references).
- Register a catalog group in `dedoc/formatters/catalog.py` with a human label
  (e.g. `"Azure Data Factory"`).

## 5. Fixtures

- `fixtures/positive/<platform>-<issue>/` for each diagnosis.
- At least one `fixtures/negative/<platform>-benign-*/` so benign platform logs
  abstain.

## 6. Docs and counts

Update platform lists and diagnosis counts in `README.md`, `docs/index.md`,
`docs/reference/diagnosis-catalog.md`, and `docs/reference/diagnosis-reference.md`,
plus a `CHANGELOG.md` entry.

## 7. Verify

```bash
make validate && make link-check && make test && make evaluate && make benchmark && make verify
```

Do not commit or push unless the user explicitly asks.
