# Diagnosis catalog

## Summary

Bundled deterministic diagnoses by category.

## Counts

- Total diagnoses: **33**
- Categories: connectivity, delta, performance, quality, schema, spark

## Category coverage

| Category | Count |
| --- | --- |
| connectivity | 5 |
| delta | 5 |
| performance | 4 |
| quality | 5 |
| schema | 6 |
| spark | 8 |

See full IDs, names, and signal mappings in [the detailed reference](../diagnosis-reference.md).

## Expected behavior

- A top diagnosis requires minimum evidence score threshold
- Positive signals and exception patterns contribute weighted evidence
- Negative signals disqualify a diagnosis

!!! tip "See also"
    - [Confidence model](../explanation/confidence-model.md)
    - [CLI reference](cli.md)
    - [Recipes](../how-to/recipes.md)
