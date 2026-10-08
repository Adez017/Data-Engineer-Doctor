# Usage

## Command-line interface

The `dedoc` command exposes two subcommands.

### `dedoc diagnose <file>`

Diagnose a failure log and print an evidence-backed report.

| Option | Meaning |
| --- | --- |
| `--format`, `-f` | Output format: `text` (default), `json`, or `markdown`. |
| `--input-format` | Override input detection: `auto` (default), `text`, `json`, `jsonl`. |
| `--diagnoses-path` | Override the diagnosis YAML directory (for custom forks/experiments). |
| `--version`, `-V` | Print the version and exit. |

**Input types**

- Text logs (`*.log`, `*.txt`): the whole file is treated as one failure event.
- JSON: a single event object, or an array of event objects.
- JSONL / NDJSON: one event object per line.

Inputs are read tolerantly (binary garbage becomes a clean error, never a
traceback). Files larger than 10 MiB are rejected.

**Exit codes**

- `0` — a report was produced (the status is `diagnosed` or `insufficient_evidence`).
- `1` — input or configuration error (missing file, malformed JSON, no diagnoses).

### `dedoc list-diagnoses`

List every bundled diagnosis definition.

| Option | Meaning |
| --- | --- |
| `--format`, `-f` | `text` (default) or `json`. |
| `--diagnoses-path` | Override the diagnosis YAML directory. |

JSON output is an array of objects with `id`, `name`, `category`, `severity`,
and `platforms`.

### Examples

```bash
$ dedoc diagnose logs/executor-oom.log

Data Engineer Doctor
Input:     logs/executor-oom.log
Platform:  spark
Status:    diagnosed
Confidence: HIGH
Events:    1
Version:   0.1.0

DEDOC-SPARK-001 selected with HIGH confidence (80/100) based on 3 evidence item(s).
Observed error types: OutOfMemoryError, java.lang.OutOfMemoryError

[DEDOC-SPARK-001] Executor Out of Memory
  Category: spark.executor_oom | Severity: critical | Platforms: spark, databricks
  Matched exception types: OutOfMemoryError
  Matched signals: executor_oom
  Hypotheses: executor_memory_exhausted, data_skew_caused_oom, oversized_partition
  Confidence: HIGH (80/100)
  Evidence:
    - [error_signature] Exact error signature matched: executor_oom (+40)
        > line 7: java.lang.OutOfMemoryError: Java heap space
    - [stacktrace_evidence] Declared exception observed in stack trace: OutOfMemoryError (+20)
    - [platform_match] Platform detected: spark (diagnosis supports: spark, databricks) (+20)
  ...
```

```bash
$ dedoc diagnose error.json --format markdown

# Data Engineer Doctor Report

- **Status:** diagnosed
- **Top confidence band:** HIGH
...
```

## Output model

The JSON output of `diagnose` contains:

- `dedoc_version` and `report_schema_version`
- `status`, `top_confidence_band`, and a human-readable `message`
- `platform` and observed `error_types`
- `matches`: each with `id`, `name`, `category`, `severity`, `score`,
  `confidence_band`, `evidence` (type, weight, description, source, excerpt),
  `hypotheses`, `recommendations`, and `references`

The excerpt is always redacted before rendering.