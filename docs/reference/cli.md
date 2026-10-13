# CLI reference

The `dedoc` command exposes two subcommands: `diagnose` and `list-diagnoses`.
Every mode works offline with no AI key unless you explicitly opt in.

## Quick reference

| Task | Command |
| --- | --- |
| Diagnose one log file | `dedoc diagnose path/to/error.log` |
| Export a machine-readable report | `dedoc diagnose path/to/error.log --format json` |
| Export a Markdown report | `dedoc diagnose path/to/error.log --format markdown` |
| Diagnose with structured context | `dedoc diagnose path/to/error.log --investigate --context context.yaml` |
| Add an optional AI explanation | `dedoc diagnose path/to/error.log --ai` |
| List built-in diagnoses | `dedoc list-diagnoses --format text` |

## `dedoc diagnose <file>`

Diagnose a failure log and print an evidence-backed report.

| Option | Default | Meaning |
| --- | --- | --- |
| `--format`, `-f` | `text` | Output format: `text`, `json`, or `markdown`. |
| `--input-format` | `auto` | Input parsing: `auto`, `text`, `json`, or `jsonl`. |
| `--diagnoses-path` | bundled | Override the diagnosis YAML directory. |
| `--investigate` | off | Run the bounded, read-only investigation agent. |
| `--context`, `-c` | — | YAML/JSON context for investigation (runs, schemas, metrics, query plan, logs). |
| `--ai` | off | Attach an optional AI explanation. |
| `--provider` | `DEDOC_AI_PROVIDER` | `none`, `openai`, `openai_compatible`, `ollama`, `azure_openai`, or `anthropic`. |
| `--ai-model` | `DEDOC_AI_MODEL` | Override the model (Azure OpenAI: the deployment name). |
| `--ai-base-url` | `DEDOC_AI_BASE_URL` | Override the provider base URL. |
| `--color` | `auto` | Colorize text output: `auto` (on a terminal), `always`, or `never`. |
| `--version`, `-V` | | Print the version and exit. |

### Input types

- **Text logs** (`*.log`, `*.txt`) — parsed as free text.
- **JSON** — a single event object, or an array of events.
- **JSONL / NDJSON** — one event per line.

For JSON and JSONL, DEDoc reads common aliases such as `message`, `errorType`,
and `stackTrace`, plus `platform`, `service`, `job`, `stage`, and `task` for
runtime metadata. Input parsing is tolerant: malformed input produces a clear
error, never a traceback, and files over **10 MiB** are rejected.

### Exit codes

| Code | Meaning |
| --- | --- |
| `0` | A report was produced (`diagnosed` or `insufficient_evidence`). |
| `1` | Input or configuration error (missing file, malformed data, no diagnoses). |

### Example output

```bash
$ dedoc diagnose logs/executor-oom.log

Data Engineer Doctor
Input:     logs/executor-oom.log
Platform:  spark
Status:    diagnosed
Confidence: HIGH
Events:    1
Version:   0.1.3

DEDOC-SPARK-001 selected with HIGH confidence (80/100) based on 3 evidence item(s).
Observed error types: OutOfMemoryError, java.lang.OutOfMemoryError

What we found:
  DEDOC-SPARK-001 Executor Out of Memory
  Severity: critical | Platforms: spark, databricks
  Confidence: HIGH (80/100)
  Matched exception types: OutOfMemoryError
  Matched signals: Executor OOM
  Possible causes: Executor Memory Exhausted; Data Skew Caused OOM; Oversized Partition

Evidence:
  1. Exact error signature matched: executor_oom (+40)
      > line 6: 24/10/08 13:10:12 INFO TaskSetManager: Starting task 42.0 ...
  2. Declared exception observed in stack trace: OutOfMemoryError (+20)
      > (same lines as evidence item 1)
  3. Platform detected: spark (diagnosis supports: spark, databricks) (+20)

What to do next:
  Immediate:
    - ...
```

The text report is conclusion-first:

1. **What we found** — the top diagnosis, its confidence, and the evidence that
   matched (signals and hypotheses translated into everyday terms).
2. **Evidence** — each observation with its weight; repeated long excerpts are
   shown once and referenced afterward.
3. **What to do next** — actionable guidance ordered Immediate / Recommended /
   Prevention.
4. **Other candidates considered** — a one-liner per alternative when more than
   one rule matched.

On terminals, the status and confidence band are color-coded (`diagnosed`
green, `insufficient_evidence` yellow; HIGH green / MEDIUM yellow / LOW red).
Pass `--color never` to force plain output, or `--color always` when piping to
a pager that supports ANSI.

When multiple rules match, DEDoc prints a ranked **candidate scoreboard** first,
then full evidence and actions for the top candidate.

## `dedoc list-diagnoses`

List the bundled diagnosis definitions.

| Option | Default | Meaning |
| --- | --- | --- |
| `--format`, `-f` | `text` | Output format: `text` or `json`. |
| `--diagnoses-path` | bundled | Override the diagnosis YAML directory. |

The default text output groups diagnoses by category with a per-group count and
a human-readable category name:

```text
Data Engineer Doctor — 39 diagnosis definition(s)

Schema (6)
  DEDOC-SCHEMA-001   Missing Column            medium   spark, databricks
  ...
```

JSON output is an array of objects with `id`, `name`, `category`, `severity`,
and `platforms` (machine-stable).

## Output model

The JSON output of `diagnose` contains:

- `dedoc_version` and `report_schema_version`
- `status`, `top_confidence_band`, and a human-readable `message`
- `platform` and observed `error_types`
- `matches`: each with `id`, `name`, `category`, `severity`, `score`,
  `confidence_band`, `evidence` (type, weight, description, source, excerpt),
  `hypotheses`, `recommendations`, and `references`

Excerpts are always redacted before rendering (see
[Security & privacy](../explanation/security-model.md)).

## Structured investigation (optional)

The deterministic engine works on the log file alone. When structured runtime
context is available — pipeline runs, schema snapshots, metrics, a query plan,
or additional logs — the **bounded investigation agent** inspects it through a
read-only tool layer and attaches its findings:

```bash
$ dedoc diagnose spark-failure.log --investigate --context context.yaml
```

The context file is YAML or JSON:

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

The investigation agent is **deterministic** — no AI and no API key. It:

- selects probes based on the top hypothesis and the data actually present;
- invokes only read-only, allowlisted tools (`get_metrics`, `get_schema`,
  `compare_runs`, `inspect_query_plan`, `search_logs`,
  `search_knowledge_base`, …);
- stops at the first **contradiction**: a negative signal of the top diagnosis
  observed in structured context;
- records corroborating signals as *supporting* findings;
- abstains (`insufficient_context`) when no context is provided;
- enforces hard limits: default **8 iterations**, **20 tool calls**, and a
  **10 second** wall-clock deadline — every limit is configurable.

Every limit and the tool layer are described in
[Architecture](../explanation/architecture.md).

## Optional AI explanation

AI is never on by default. Enable it with `--ai` and a configured provider:

```bash
export DEDOC_AI_PROVIDER=ollama
export DEDOC_AI_MODEL=llama3.2
dedoc diagnose error.log --ai
```

| Provider | `--provider` | Required environment |
| --- | --- | --- |
| No AI (default) | `none` | — |
| OpenAI | `openai` | `DEDOC_OPENAI_API_KEY` |
| OpenAI-compatible | `openai_compatible` | `DEDOC_AI_BASE_URL` (optional `DEDOC_OPENAI_API_KEY`) |
| Ollama (local) | `ollama` | none |
| Azure OpenAI | `azure_openai` | `DEDOC_AZURE_OPENAI_API_KEY`, `DEDOC_AZURE_OPENAI_ENDPOINT` |
| Anthropic | `anthropic` | `DEDOC_ANTHROPIC_API_KEY` |

`DEDOC_AI_PROVIDER`, `DEDOC_AI_MODEL`, and `DEDOC_AI_BASE_URL` set the defaults;
the matching flags override them per run. API keys are **never** accepted as CLI
arguments or config files — they are read from the environment only.

If the provider is unavailable (missing key or model), AI is skipped and the
deterministic report still succeeds. See
[Security & privacy](../explanation/security-model.md) for exactly what leaves
your machine.

!!! tip "See also"
    - [Configuration](../how-to/configuration.md)
    - [Python SDK reference](sdk.md)
    - [Troubleshooting](../how-to/troubleshooting.md)
    - [Top 25 user queries map](top-25-queries.md)
