# Python SDK reference

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

## Public API

- `dedoc.diagnose(...)`
- `dedoc.list_diagnoses(...)`
- `dedoc.Diagnosis`, `dedoc.DiagnosisReport`, `dedoc.AIExplanation`
- `dedoc.AgentConfig`, `dedoc.InvestigationContext`, `dedoc.InvestigationRecord`
- `dedoc.ProviderConfig`
- `dedoc.__version__`

These are the entire supported surface. Everything else under `dedoc.*` is an
implementation detail that may change between versions. Public diagnosis IDs
(such as `DEDOC-SCHEMA-001`) are a stable API and are never renamed or
repurposed.

## Expected output

- A `DiagnosisReport` with status, confidence, and matches.
- `investigation` is present only when investigation mode is enabled.
- `ai_explanation` is present only when AI mode is enabled and available.

## Errors

`diagnose` raises:

| Error | Raised when |
| --- | --- |
| `dedoc.core.errors.InputError` | The input file is missing, too large, or malformed (also an invalid investigation context mapping). |
| `dedoc.core.errors.DiagnosisLoadError` | The diagnoses directory is missing, empty, or contains an invalid definition. |
| `dedoc.core.errors.AgentConfigError` | The investigation `AgentConfig` has invalid hard limits. |
| `dedoc.core.errors.ProviderConfigError` | An explicitly configured `ProviderConfig` is invalid (unknown provider or bad bounds). |
| `dedoc.core.errors.ProviderError` | An explicitly enabled AI provider could not complete its request. |

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

## Optional AI explanation

AI is never on by default. Enable it with `ai=True` (environment defaults) or
pass an explicit `ProviderConfig`:

```python
from dedoc import diagnose
from dedoc.providers import ProviderConfig

# From DEDOC_AI_* environment variables
report = diagnose("logs/executor-oom.log", ai=True)
print(report.ai_explanation.text if report.ai_explanation else "no AI")

# Explicit configuration (keys still come from the environment)
report = diagnose(
    "logs/executor-oom.log",
    provider_config=ProviderConfig(provider="ollama", model="llama3.2"),
)
```

`ProviderConfig` is secret-free — never put an API key in it. Keys are read from
`DEDOC_OPENAI_API_KEY`, `DEDOC_AZURE_OPENAI_API_KEY`, or
`DEDOC_ANTHROPIC_API_KEY`; local Ollama needs none.

If the provider is not available (missing key or model) the report is still
produced normally with `ai_explanation: null`. See
[Security & privacy](../explanation/security-model.md) for what is redacted and
sent.

!!! tip "See also"
    - [CLI reference](cli.md)
    - [Configuration](../how-to/configuration.md)
    - [Confidence model](../explanation/confidence-model.md)
    - [Security & privacy](../explanation/security-model.md)
