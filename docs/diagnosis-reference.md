# Diagnosis reference

The deterministic knowledge base ships as versioned YAML definitions under `diagnoses/`. Each definition carries stable IDs, exception
patterns, registered signals, hypotheses, evidence-backed recommendations, and
links to official documentation. Coverage is enforced: every diagnosis must be
exercised by at least one positive fixture (`fixtures/`).

## How evidence becomes confidence

- An **exact error signature** (a known, verified error token) scores **40/100**.
- A **correlated runtime signal** (behavioral indicator) scores **15/100**.
- A **declared exception observed** in a stack trace scores **20/100**.
- A **platform match** scores **20/100**; runtime **metadata** scores **5/100**.
- A diagnosis is only reported when its top candidate **reaches 40/100**.
- Confidence bands: **HIGH ≥ 70**, **MEDIUM ≥ 40**, otherwise low / insufficient.

The weights and versioned thresholds live in `dedoc/evidence/` and are derived
from BUILD_PLAN.md §10.

## Definitions

| ID | Name | Category | Severity | Positive signals |
| --- | --- | --- | --- | --- |
| DEDOC-CONN-001 | Authentication Failure | `connectivity.authentication` | high | `authentication_failure` |
| DEDOC-CONN-002 | Connection Timeout | `connectivity.connection_timeout` | high | `connection_timeout` |
| DEDOC-CONN-003 | DNS Failure | `connectivity.dns_failure` | high | `dns_failure` |
| DEDOC-CONN-004 | Permission Denied | `connectivity.permission_denied` | high | `permission_denied` |
| DEDOC-CONN-005 | Endpoint Unavailable | `connectivity.endpoint_unavailable` | high | `endpoint_unavailable` |
| DEDOC-DELTA-001 | Concurrent Modification | `delta.concurrent_modification` | high | `delta_concurrent_conflict` |
| DEDOC-DELTA-002 | Delta Schema Mismatch | `delta.schema_mismatch` | high | `delta_merge_fields_failed` |
| DEDOC-DELTA-003 | Table Not Found | `delta.table_not_found` | high | `table_or_view_not_found`, `delta_not_a_table` |
| DEDOC-DELTA-004 | Invalid Partition Column | `delta.invalid_partition` | medium | `invalid_partition` |
| DEDOC-DELTA-005 | Transaction Conflict | `delta.transaction_conflict` | medium | `delta_concurrent_transaction`, `delta_metadata_changed`, `delta_protocol_changed` |
| DEDOC-PERF-001 | Small Files Problem | `performance.small_files` | low | `small_files` |
| DEDOC-PERF-002 | Excessive Shuffle | `performance.excessive_shuffle` | low | `excessive_shuffle` |
| DEDOC-PERF-003 | Missing Partition Pruning | `performance.partition_pruning` | low | `missing_partition_pruning` |
| DEDOC-PERF-004 | Oversized Broadcast | `performance.oversized_broadcast` | low | `broadcast_size_exceeded` |
| DEDOC-QUALITY-001 | Null Constraint Violation | `quality.null_violation` | high | `null_constraint_violated` |
| DEDOC-QUALITY-002 | Duplicate Keys | `quality.duplicates` | high | `duplicate_keys` |
| DEDOC-QUALITY-003 | Invalid Date Value | `quality.invalid_date` | medium | `date_parse_failure` |
| DEDOC-QUALITY-004 | Invalid Numeric Value | `quality.invalid_numeric` | medium | `invalid_numeric_value` |
| DEDOC-QUALITY-005 | Referential Integrity Issue | `quality.referential_integrity` | high | `merge_cardinality_violation` |
| DEDOC-SCHEMA-001 | Missing Column | `schema.missing_column` | medium | `resolved_column_not_found` |
| DEDOC-SCHEMA-002 | Data Type Mismatch | `schema.type_mismatch` | medium | `datatype_mismatch` |
| DEDOC-SCHEMA-003 | Unexpected Column | `schema.unexpected_column` | medium | `unexpected_column` |
| DEDOC-SCHEMA-004 | Duplicate Column | `schema.duplicate_column` | medium | `ambiguous_reference` |
| DEDOC-SCHEMA-005 | Schema Evolution Failure | `schema.evolution_failure` | high | `schema_evolution_blocked` |
| DEDOC-SCHEMA-006 | Nested Schema Mismatch | `schema.nested_mismatch` | medium | `nested_schema_field_unresolved` |
| DEDOC-SPARK-001 | Executor Out of Memory | `spark.executor_oom` | critical | `executor_oom` |
| DEDOC-SPARK-002 | Driver Out of Memory | `spark.driver_oom` | critical | `driver_oom` |
| DEDOC-SPARK-003 | Executor Lost | `spark.executor_lost` | high | `executor_lost` |
| DEDOC-SPARK-004 | Repeated Task Failure | `spark.repeated_task_failure` | high | `task_failure_repeated` |
| DEDOC-SPARK-005 | Data Skew | `spark.data_skew` | medium | `data_skew` |
| DEDOC-SPARK-006 | Shuffle Fetch Failure | `spark.shuffle` | high | `shuffle_fetch_failed` |
| DEDOC-SPARK-007 | Broadcast Failure | `spark.broadcast` | high | `broadcast_timeout`, `broadcast_oom` |
| DEDOC-SPARK-008 | Stage Failure | `spark.stage_failure` | high | `stage_failure` |


## Counts

- **33** deterministic diagnoses across six categories:
- `connectivity`: **5**
- `delta`: **5**
- `performance`: **4**
- `quality`: **5**
- `schema`: **6**
- `spark`: **8**


Positive signals are the v0.1 precision rule: a diagnosis with declared signals
only matches when **at least one** of them is observed. A bare exception type is
corroborating evidence, never sufficient on its own. Negative signals
disqualify a diagnosis entirely.
