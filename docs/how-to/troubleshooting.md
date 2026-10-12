# Troubleshooting

## Summary

Quick fixes for common setup, input, and output issues.

## Prerequisites

- Installed DEDoc
- Failing command and input file available

## Steps

1. Re-run with explicit output format:

   ```bash
   dedoc diagnose error.log --format text
   ```

2. Validate input file and type.

3. If using optional modes, isolate variables:
   - Run deterministic mode first
   - Add investigation mode
   - Add AI explanation mode last

## Expected output

A deterministic report or a clear configuration/input error without traceback.

## Common errors

| Symptom | Root cause | Action |
| --- | --- | --- |
| `InputError` malformed input | Bad JSON/JSONL or binary data | Validate/convert source file |
| `InputError` file too large | Over 10 MiB guard | Trim to relevant failure section |
| `DiagnosisLoadError` | Invalid/missing definitions | Restore `diagnoses/` content |
| `ProviderConfigError` | Unsupported provider or missing env | Set valid provider and vars |
| `ProviderError` | Provider unavailable | Retry later or use deterministic mode |

!!! tip "Search keywords"
    Try: `dedoc error`, `inputerror`, `providerconfigerror`, `insufficient evidence`, `diagnosisloaderror`.

!!! tip "See also"
    - [FAQ](faq.md)
    - [Configuration](configuration.md)
    - [Security model](../explanation/security-model.md)
