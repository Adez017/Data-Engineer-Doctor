# Changelog

All notable changes to this project are documented in this file.
Versioning follows [Semantic Versioning](https://semver.org/).

The format is adapted from [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added

- **Diagnostic knowledge base (33 diagnoses)** across six categories:
  - Schema (`DEDOC-SCHEMA-001`–`006`): missing column, data type mismatch,
    unexpected column, duplicate column, schema evolution failure, nested
    schema mismatch.
  - Data quality (`DEDOC-QUALITY-001`–`005`): null violation, duplicate keys,
    invalid date, invalid numeric value, referential integrity issue.
  - Spark (`DEDOC-SPARK-001`–`008`): executor OOM, driver OOM, executor lost,
    repeated task failure, data skew, shuffle fetch failure, broadcast failure,
    stage failure.
  - Delta (`DEDOC-DELTA-001`–`005`): concurrent modification, schema mismatch,
    table not found, invalid partition column, transaction conflict.
  - Connectivity (`DEDOC-CONN-001`–`005`): authentication failure, connection
    timeout, DNS failure, permission denied, endpoint unavailable.
  - Performance (`DEDOC-PERF-001`–`004`): small files, excessive shuffle,
    missing partition pruning, oversized broadcast.
- **Fixtures**: 34 positive, 2 negative, 3 malformed, covering every diagnosis
  with enforced coverage and confidence-band assertions.
- **Signature registry** (`dedoc/analyzer/signals.py`) with explicit
  `exact`/correlated classification for every signal.
- **Public Python SDK**: `dedoc.diagnose()` and `dedoc.list_diagnoses()`.
- **CLI**: `dedoc diagnose` (text/json/markdown) and `dedoc list-diagnoses`.
- **CI** (GitHub Actions, Python 3.11 + 3.12) running the authoritative
  `make verify` gate.
- **Prepare-only release workflow** (builds + verifies; publishing is
  intentionally not wired to credentials).
- **Documentation**: MkDocs site with usage, SDK, diagnosis reference,
  contributing, and security guides.
- **OSS toolkit**: Apache-2.0 license, code of conduct, issue templates,
  pull-request template, security policy, changelog.

## [0.1.0] - unreleased

Initial deterministic MVP: evidence-driven diagnosis for Spark/Databricks
failures with no AI/LLM dependency.