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
| `--investigate` | Run the bounded investigation agent over optional structured context. |
| `--context`, `-c` | Structured context file (YAML/JSON): runs, schemas, metrics, query plan, logs. |
| `--version`, `-V` | Print the version and exit. |

**Input types**

- Text logs (`*.log`, `*.txt`): the whole file is treated as one failure event.
- JSON: a single event object, or an array of event objects.
- JSONL / NDJSON: one event object per line.

Inputs are read tolerantly (binary garbage becomes a clean error, never a
traceback). Files larger than 10 MiB are rejected.

**Exit codes**

- `0` means a report was produced (the status is `diagnosed` or
  `insufficient_evidence`).
- `1` means an input or configuration error (missing file, malformed JSON, no
  diagnoses).

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

Diagnosis: DEDOC-SPARK-001 Executor Out of Memory
  Category: spark.executor_oom | Severity: critical | Platforms: spark, databricks
  Matched exception types: OutOfMemoryError
  Matched signals: executor_oom
  Hypotheses: executor_memory_exhausted, data_skew_caused_oom, oversized_partition
  Confidence: HIGH (80/100)
  Evidence:
    - [error_signature] Exact error signature matched: executor_oom (+40)
        > line 6: 24/10/08 13:10:12 INFO TaskSetManager: Starting task 42.0 ...
        > line 7: java.lang.OutOfMemoryError: Java heap space
    - [stacktrace_evidence] Declared exception observed in stack trace: OutOfMemoryError (+20)
    - [platform_match] Platform detected: spark (diagnosis supports: spark, databricks) (+20)
  ...
```

When several diagnosis rules match, DEDoc prints a ranked **candidate scoreboard**
first, then full evidence and actions for the top candidate. The other candidates
get a compact one-liner under **Other candidates considered**.

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

## Optional structured investigation (Phase 4)

The deterministic engine works on the log file alone. When structured runtime
context is available (pipeline runs, schema snapshots, metrics, a query plan,
or additional logs), the **bounded investigation agent** inspects it through a
read-only tool layer and attaches its findings to the report:

```bash
$ dedoc diagnose spark-failure.log --investigate --context context.yaml
```

The context file is YAML or JSON. Example:

```yaml
current_run: { run_id: "run-2026-10-09-01", status: failed, stage: "stage-7" }
previous_runs:
  - run_id: "run-2026-10-09-00"
    status: succeeded
schemas:
  customer:
    columns: [id, name, email]
metrics:
  executor.memory.used: { value: 0.92, labels: { executor: exec5 } }
query_plan: "Exchange LogSink: output row count 1200"
logs:
  - "24/10/08 13:10:12 WARN Adding partitioning column for full scan"
```

The agent is **deterministic**: there is no AI and no API key. It:

- selects probes based on the top hypothesis and the data actually present
- invokes only read-only, allowlisted tools (`get_metrics`, `get_schema`,
  `compare_runs`, `inspect_query_plan`, `search_logs`, `search_knowledge_base`, ...)
- stops at the first **contradiction**: a negative signal of the top diagnosis
  observed in structured context
- records corroborating signals as *supporting* findings
- abstains (`insufficient_context`) when no context is provided
- enforces hard limits: default **8 iterations**, **20 tool calls**, and a
  **10 second** wall-clock deadline. Every limit is configurable

The text/markdown report gains an **Investigation** section; JSON output adds an
`investigation` object (`status`, `iterations`, `tool_calls`, `reason`,
`findings`, `contradictions`, `calls`). Tools never mutate production state and
all log-derived text is redacted before it appears in a report.