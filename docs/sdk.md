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

- `dedoc.core.errors.InputError`: the input file is missing, too large, or
  malformed.
- `dedoc.core.errors.DiagnosisLoadError`: the diagnoses directory is missing,
  empty, or contains an invalid definition.

Internally the `diagnose` string argument is always coerced to a `Path`.

## Structured investigation

`diagnose(..., investigate=True)` runs the bounded investigation agent,
optionally over structured context built with `context_from_mapping`:

```python
from dedoc import diagnose
from dedoc.tools import InvestigationContext, context_from_mapping
from dedoc.agents import AgentConfig

context = context_from_mapping(
    {
        "metrics": {"executor.memory.used": {"value": 0.92, "labels": {"executor": "exec5"}}},
        "current_run": {"run_id": "run-1", "status": "failed"},
        "previous_runs": [{"run_id": "run-0", "status": "succeeded"}],
    }
)

report = diagnose(
    "logs/executor-oom.log",
    investigate=True,
    context=context,
    agent_config=AgentConfig(max_iterations=6, max_tool_calls=10, timeout_seconds=5),
)

if report.investigation is not None:
    print(report.investigation.status, report.investigation.tool_calls)
    for finding in report.investigation.findings:
        print(finding.kind, finding.description)
    for contradiction in report.investigation.contradictions:
        print(contradiction.description)
```

Without `investigate=True` the report simply has `investigation: null` and no
tool ever runs.

## Errors

`diagnose` raises:

- `dedoc.core.errors.InputError`: the input file is missing, too large, or
  malformed (also raised for an invalid investigation context mapping).
- `dedoc.core.errors.DiagnosisLoadError`: the diagnoses directory is missing,
  empty, or contains an invalid definition.
- `dedoc.core.errors.AgentConfigError`: the investigation `AgentConfig` has
  invalid hard limits.

Internally the `diagnose` string argument is always coerced to a `Path`.

## What is public

Only the names in `dedoc.__all__` are the public API:

- `dedoc.diagnose(...)`
- `dedoc.list_diagnoses(...)`
- `dedoc.Diagnosis`, `dedoc.DiagnosisReport`
- `dedoc.AgentConfig`, `dedoc.InvestigationContext`,
  `dedoc.InvestigationRecord`
- `dedoc.__version__`

Everything else under `dedoc.*` is an implementation detail and may change
without notice between releases. Public IDs (for example `DEDOC-SPARK-001`) are
a stable API and are not renamed casually. See the diagnosis reference.