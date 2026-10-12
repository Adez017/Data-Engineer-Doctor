# Recipes

## Summary

Practical workflows for common real-world diagnosis tasks.

## Prerequisites

- DEDoc installed
- Access to relevant logs/context files

## Steps

## 1) Spark executor OOM

```bash
dedoc diagnose logs/executor-oom.log
```

Expected: `DEDOC-SPARK-001` as top candidate with memory-related actions.

## 2) Schema mismatch

```bash
dedoc diagnose logs/schema-error.log --format markdown
```

Expected: schema-oriented diagnosis (`DEDOC-SCHEMA-*`) and remediation guidance.

## 3) Delta conflict

```bash
dedoc diagnose logs/delta-conflict.log --format json
```

Expected: delta conflict diagnosis with ranked alternatives when relevant.

## 4) CI usage

```bash
dedoc diagnose artifacts/failure.log --format json > diagnosis.json
```

Expected: machine-readable output suitable for pipeline artifacts and alerts.

## 5) JSON automation

```bash
dedoc diagnose event.json --input-format json --format json
```

Expected: structured report including `status`, `matches`, and confidence metadata.

## Common errors

| Problem | Likely cause | Fix |
| --- | --- | --- |
| Wrong diagnosis family | Log is partial/noisy | Provide fuller stack trace or context |
| `insufficient_evidence` | Signal threshold not reached | Add complete event log and rerun |
| CI artifact unreadable | Unsupported file encoding | Re-export UTF-8/valid JSON |

!!! tip "Decision table"
    | I have this problem | Use this command |
    | --- | --- |
    | Spark crash from OOM | `dedoc diagnose logs/executor-oom.log` |
    | Need automation output | `dedoc diagnose ... --format json` |
    | Need richer context validation | `dedoc diagnose ... --investigate --context ...` |

!!! tip "See also"
    - [Troubleshooting](troubleshooting.md)
    - [Diagnosis catalog](../reference/diagnosis-catalog.md)
