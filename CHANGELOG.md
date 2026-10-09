# Changelog

All notable changes to this project are documented in this file.
Versioning follows [Semantic Versioning](https://semver.org/).

The format is adapted from [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added

- **Bounded investigation agent (Phase 4)**: optional, deterministic inspection
  of structured runtime context (runs, schemas, metrics, query plan, logs)
  through a read-only allowlisted tool layer, with independent contradiction
  and corroboration detection. No AI, no API key.
- **12 read-only investigation tools** (`dedoc/tools/library.py`): get/search
  logs, pipeline runs and comparisons, schema inspect/compare, metrics and
  stage/executor metrics, query-plan inspection, and knowledge-base search.
- **Hard limits enforcement**: tool timeouts, allowlist deny, and agent budgets
  (default 8 iterations / 20 tool calls / 10 s deadline), all configurable via
  `AgentConfig`; abstention (`insufficient_context`) instead of guessing.
- **CLI**: `dedoc diagnose --investigate --context <file>` accepts YAML/JSON
  structured context.
- **Report schema v3** (`report_schema_version: "3"`): adds an `investigation`
  section rendered in text/markdown/JSON formats.
- **Readable text reports**: when multiple diagnosis rules match, the text
  report leads with a ranked candidate scoreboard and renders full evidence and
  actions for the top candidate, with compact one-liners for the alternatives.
- **MkDocs site on Material for MkDocs**: modern navigation tabs, instant search
  with highlighting, code-copy buttons, and a light/dark theme toggle.
- **n8n-inspired docs theme**: Inter + IBM Plex Mono typography, orange-red
  accent, dark rounded code blocks, a launcher-style card grid on the homepage,
  and a creator attribution block in the footer and homepage.
- **GitHub Pages hosting**: a `docs` workflow builds the strict MkDocs site and
  deploys it to https://Adez017.github.io/Data-Engineer-Doctor/.
- **Contextual evidence excerpts**: each excerpt shows the matched line plus one
  line of surrounding context (redacted, clamped, labeled `line A-B`).
- **Per-evidence excerpts**: signature evidence cites the signal line and
  stacktrace evidence cites the exception message line, instead of one shared
  excerpt; platform/metadata evidence reuse the most relevant citation.
- **Severity-aware ranking**: report matches are ordered by score, then severity
  (critical first), then stable diagnosis id.

### Changed

- **Report schema** moved from `"2"` to `"3"` (adds `investigation`).
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