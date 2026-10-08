# Python SDK

The public SDK is deliberately tiny. Import `diagnose` and `list_diagnoses`
from the top-level `dedoc` package.

```python
from dedoc import diagnose, list_diagnoses
from dedoc.models.report import ReportStatus

# List every bundled diagnosis definition
for d in list_diagnoses():
    print(d.id, d.name, d.category, d.severity.default)

# Diagnose a failure log
report = diagnose("logs/executor-oom.log")

print(report.status)  # ReportStatus.DIAGNOSED
print(report.top_confidence_band)  # ConfidenceBand.HIGH
for match in report.matches:
    print(match.id, match.score, match.confidence_band)
    print(match.hypotheses)
    print(match.recommendations.immediate)
    for item in match.evidence:
        print(item.type, item.weight, item.description, item.excerpt)
```

## Errors

`diagnose` raises:

- `dedoc.core.errors.InputError` — the input file is missing, too large, or
  malformed.
- `dedoc.core.errors.DiagnosisLoadError` — the diagnoses directory is missing,
  empty, or contains an invalid definition.

Internally the `diagnose` string argument is always coerced to a `Path`.

## What is public

Only the names in `dedoc.__all__` are the public API:

- `dedoc.diagnose(...)`
- `dedoc.list_diagnoses(...)`
- `dedoc.Diagnosis`, `dedoc.DiagnosisReport`
- `dedoc.__version__`

Everything else under `dedoc.*` is an implementation detail and may change
without notice between releases. Public IDs (for example `DEDOC-SPARK-001`) are
a stable API and are not renamed casually — see the diagnosis reference.