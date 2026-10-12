# Python SDK reference

## Summary

Public SDK surface and expected behavior.

## Prerequisites

- Python 3.11+
- `from dedoc import diagnose, list_diagnoses`

## Public API

- `dedoc.diagnose(...)`
- `dedoc.list_diagnoses(...)`
- `dedoc.Diagnosis`, `dedoc.DiagnosisReport`, `dedoc.AIExplanation`
- `dedoc.AgentConfig`, `dedoc.InvestigationContext`, `dedoc.InvestigationRecord`
- `dedoc.ProviderConfig`
- `dedoc.__version__`

## Expected output

- `DiagnosisReport` with status, confidence, matches, and optional sections
- `investigation` present only when investigation mode is enabled
- `ai_explanation` present only when AI explanation mode is enabled and available

## Common errors

- `InputError`
- `DiagnosisLoadError`
- `AgentConfigError`
- `ProviderConfigError`
- `ProviderError`

!!! tip "See also"
    - [Configuration](../how-to/configuration.md)
    - [Confidence model](../explanation/confidence-model.md)
    - [Security model](../explanation/security-model.md)
