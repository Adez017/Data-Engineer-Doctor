# Usage

## Quick reference

| Task | Command |
| --- | --- |
| Diagnose one log file | `dedoc diagnose path/to/error.log` |
| Export machine-readable report | `dedoc diagnose path/to/error.log --format json` |
| Export markdown report | `dedoc diagnose path/to/error.log --format markdown` |
| Diagnose with structured context | `dedoc diagnose path/to/error.log --investigate --context context.yaml` |
| Add optional AI explanation | `dedoc diagnose path/to/error.log --ai` |
| List built-in diagnoses | `dedoc list-diagnoses --format text` |

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
| `--ai` | Attach an optional AI explanation. Provider and keys are read from `DEDOC_AI_*` environment variables. |
| `--provider` | Override the AI provider: `none`, `openai`, `openai_compatible`, `ollama`, `azure_openai`, or `anthropic`. |
| `--ai-model` | Override the AI model (for Azure OpenAI use the deployment name). |
| `--ai-base-url` | Override the provider base URL. |
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
| `--format`, `-f` | `text` (default), `markdown`, or `json`. |
| `--diagnoses-path` | Override the diagnosis YAML directory. |
| `--color` | `auto` (default; colors only on a terminal), `always`, or `never`. |

The `diagnose` options also include `--investigate`, `--context`, and the
optional AI flags (`--ai`, `--provider`, `--ai-model`, `--ai-base-url`).

JSON output is an array of objects with `id`, `name`, `category`, `severity`,
and `platforms`.

### Example output

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
      > (same lines as evidence item 1)

What to do next:
  Immediate:
    - Identify the failing task and stage; a single large partition or a skew often causes the failure.
    - Retry with more executor memory (spark.executor.memory and spark.executor.memoryOverhead) ...
  Recommended:
    - Increase parallelism (spark.sql.shuffle.partitions) so tasks process less data per partition.
  Prevention:
    - Enable and review AQE skew join optimization for joins on skewed keys.
  ...
```

The text report is written in plain language, conclusion-first:

1. **What we found** — the top diagnosis, its confidence, and what evidence
   matched (signals and hypotheses translated into everyday terms).
2. **Evidence** — each observation with its weight; repeated long excerpts are
   shown once and referenced afterward.
3. **What to do next** — actionable guidance, ordered Immediate / Recommended /
   Prevention.
4. **Other candidates considered** — a one-liner per alternative when more than
   one rule matched.

On terminals, the status and confidence band are color-coded
(`diagnosed` green, `insufficient_evidence` yellow, HIGH green / MEDIUM yellow /
LOW red). Pass `--color never` to force plain output, or `--color always` if
you are piping to a pager that supports ANSI codes.

When multiple diagnosis rules match, DEDoc prints a ranked **candidate scoreboard**
first, then full evidence and actions for the top candidate.

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

## Structured investigation (optional, Phase 4)

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

The investigation agent is **deterministic**: there is no AI and no API key. It:

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

## AI explanation (optional, Phase 5)

The deterministic engine never requires AI and never needs an API key. As an
optional layer, DEDoc can ask an AI provider to explain the top diagnosis. AI
only runs when you explicitly opt in:

```bash
$ export DEDOC_AI_PROVIDER=ollama
$ export DEDOC_AI_MODEL=llama3.2
$ dedoc diagnose spark-failure.log --ai
```

Providers and their environment variables:

| Provider | `--provider` | Required environment | Notes |
| --- | --- | --- | --- |
| No AI (default) | `none` | — | Fully deterministic. |
| OpenAI | `openai` | `DEDOC_OPENAI_API_KEY` | |
| OpenAI-compatible | `openai_compatible` | `DEDOC_AI_BASE_URL` (optional `DEDOC_OPENAI_API_KEY`) | vLLM, LM Studio, local gateways. |
| Ollama (local) | `ollama` | none | No API key needed; `model` points at a pulled model. |
| Azure OpenAI | `azure_openai` | `DEDOC_AZURE_OPENAI_API_KEY`, `DEDOC_AZURE_OPENAI_ENDPOINT` | `--ai-model` is the deployment name. |
| Anthropic | `anthropic` | `DEDOC_ANTHROPIC_API_KEY` | |

`DEDOC_AI_PROVIDER`, `DEDOC_AI_MODEL`, and `DEDOC_AI_BASE_URL` configure the
defaults; the `--provider`, `--ai-model`, and `--ai-base-url` flags override
them per run. API keys are **never** accepted as CLI arguments or in config
files.

Privacy guarantees:

- Outside AI is never contacted unless `--ai` (or `ai=True` in the SDK) is set.
- Before anything is sent, log content is re-redacted and bounded to a few
  thousand characters. Secrets cannot survive into the bytes that leave your
  machine.
- The explanation is appended as an **AI explanation** section in text/markdown
  output and as an `ai_explanation` object in JSON (`provider`, `model`,
  `text`). If the provider is unavailable (missing key, no model), AI is simply
  skipped — the deterministic report still succeeds.

What leaves the machine in AI mode: the redacted report summary (status, top
diagnosis, matched signals, evidence descriptions and excerpts, recommendations)
plus a bounded, redacted excerpt of the input — and the API key in a request
header to the provider only.