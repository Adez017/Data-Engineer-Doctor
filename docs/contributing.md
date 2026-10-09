# Contributing

Contributions are welcome. The project is designed so that adding a diagnosis
is possible without understanding the entire codebase. This page is a summary;
see `CONTRIBUTING.md` at the repository root for the full workflow.

## Ways to contribute

- Add a diagnosis (see below).
- Improve fixtures: richer positive cases, sharper negative guards.
- Improve redaction, evidence scoring, or the report formatters.
- Fix documentation, link checks, or CI.

## Adding a diagnosis

1. Pick an unused stable ID in the right category, for example
   `DEDOC-SPARK-00X`.
2. Register any new **signal** in `dedoc/analyzer/signals.py`
   (`SIGNAL_REGISTRY`). A signal is a named regular expression; `exact=True`
   marks it as a known, verified error signature (weight 40), otherwise it is a
   correlated runtime signal (weight 15). Never invent error semantics: a
   signature must be validated against real, official error wording or labelled
   as an unverified hypothesis.
3. Write the YAML definition under `diagnoses/<category>/`, with:
   - the exception patterns observed for this failure,
   - positive/negative signals,
   - at least one hypothesis and one reference to official documentation,
   - a `tests.fixtures` list.
4. Create the fixtures under `fixtures/`:
   - `positive/<name>/input.*` + `meta.yaml` (must list the expected
     diagnosis ids and a `confidence_band`),
   - a negative fixture whose log must **not** match your diagnosis.
5. Run `make verify`. Coverage is enforced: every diagnosis must be exercised
   by at least one positive fixture, and every reference URL must be reachable.

## What never to do

- Do not claim root-cause certainty without supporting evidence.
- Do not invent error messages, error codes, or documentation URLs
  (validate or label them as unverified hypotheses).
- Do not add behavior that mutates production resources.
- Do not rename or repurpose a released diagnosis ID.