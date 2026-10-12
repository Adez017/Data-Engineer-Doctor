# CLI reference

## Summary

Authoritative command-line reference for `dedoc`.

## Prerequisites

- DEDoc installed

## Commands

## `dedoc diagnose <file>`

Diagnose a failure log and print an evidence-backed report.

| Option | Meaning |
| --- | --- |
| `--format`, `-f` | Output format: `text` (default), `json`, `markdown` |
| `--input-format` | `auto` (default), `text`, `json`, `jsonl` |
| `--diagnoses-path` | Override diagnosis YAML directory |
| `--investigate` | Run bounded read-only investigation mode |
| `--context`, `-c` | YAML/JSON context for investigation |
| `--ai` | Enable optional AI explanation mode |
| `--provider` | `none`, `openai`, `openai_compatible`, `ollama`, `azure_openai`, `anthropic` |
| `--ai-model` | Override model/deployment |
| `--ai-base-url` | Override provider base URL |
| `--version`, `-V` | Print version and exit |

## `dedoc list-diagnoses`

List bundled diagnosis definitions.

| Option | Meaning |
| --- | --- |
| `--format`, `-f` | `text` (default), `markdown`, or `json` |
| `--diagnoses-path` | Override diagnosis YAML directory |
| `--color` | `auto`, `always`, `never` |

## Input types

- Text logs (`*.log`, `*.txt`)
- JSON object/array
- JSONL / NDJSON

## Exit codes

- `0`: report produced (`diagnosed` or `insufficient_evidence`)
- `1`: input/configuration error

## Common errors

| Error | Meaning |
| --- | --- |
| `InputError` | Missing/invalid input file or malformed data |
| `DiagnosisLoadError` | Broken or missing diagnosis definitions |
| `ProviderConfigError` | Invalid AI provider configuration |
| `ProviderError` | Provider request failed |

!!! tip "See also"
    - [Configuration](../how-to/configuration.md)
    - [Troubleshooting](../how-to/troubleshooting.md)
    - [Top 25 user queries map](top-25-queries.md)
