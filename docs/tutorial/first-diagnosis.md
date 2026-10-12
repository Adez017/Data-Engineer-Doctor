# Tutorial: first diagnosis

## Summary

Run your first diagnosis in under five minutes and verify expected output.

## Prerequisites

- Python 3.11 or 3.12
- DEDoc installed (see [Installation](../how-to/installation.md))
- A sample log file (`*.log`, `*.txt`, `*.json`, or `*.jsonl`)

## Steps

1. Install dependencies.

   ```bash
   pip install -e ".[dev]"
   ```

2. Run diagnosis.

   ```bash
   dedoc diagnose path/to/error.log
   ```

3. Export machine-readable output.

   ```bash
   dedoc diagnose path/to/error.log --format json
   ```

4. List available diagnoses.

   ```bash
   dedoc list-diagnoses --format text
   ```

## Expected output

- Header with input, detected platform, status, confidence, and version
- Top diagnosis with weighted evidence summary
- Ordered actions: Immediate, Recommended, Prevention

## Common errors

| Problem | Likely cause | Fix |
| --- | --- | --- |
| `InputError` for file not found | Wrong path | Use absolute/valid path |
| `InputError` for malformed JSON | Invalid JSON/JSONL | Validate file format |
| No diagnoses loaded | Missing/invalid definitions | Restore `diagnoses/` or use `--diagnoses-path` |

!!! tip "See also"
    - [Troubleshooting](../how-to/troubleshooting.md)
    - [CLI reference](../reference/cli.md)
    - [Configuration](../how-to/configuration.md)
