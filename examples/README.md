# Examples

Runnable sample inputs that show what DEDoc does with no configuration and no
AI key. Each file under `logs/` is a self-contained failure (or a benign log,
to show abstention).

## Run them all

```bash
make examples
```

Or diagnose a single file:

```bash
dedoc diagnose examples/logs/spark-executor-oom.log
dedoc diagnose examples/logs/adf-linked-service.json --format markdown
```

## What is in here

| File | Platform | Expected result |
| --- | --- | --- |
| `logs/spark-executor-oom.log` | Spark | `DEDOC-SPARK-001` — Executor Out of Memory (HIGH) |
| `logs/schema-missing-column.json` | Spark | `DEDOC-SCHEMA-001` — Missing Column (HIGH) |
| `logs/delta-concurrent-write.log` | Spark / Delta | `DEDOC-DELTA-001` — Concurrent Modification (HIGH) |
| `logs/adf-linked-service.json` | Azure Data Factory | `DEDOC-ADF-001` — Linked Service Connection Failure (MEDIUM) |
| `logs/no-signal-app.log` | — | `insufficient_evidence` (DEDoc abstains) |

Expected results are asserted in the test suite; `examples/` is a convenience
for trying the tool, while `fixtures/` is the graded evaluation corpus.

## Structured input

Input can be plain text (`.log`), a JSON object, or JSONL — one event per line.
For JSON/JSONL, DEDoc reads common aliases such as `message`, `errorType`,
`stackTrace`, plus `platform`, `service`, `job`, `stage`, and `task` for runtime
metadata (`examples/logs/*.json` show the shape).
