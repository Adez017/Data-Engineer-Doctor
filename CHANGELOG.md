# Changelog

All notable changes to this project are documented in this file.
Versioning follows [Semantic Versioning](https://semver.org/).

The format is adapted from [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

## [0.1.4] - 2026-10-13

### Fixed

- **Evidence citations pointed at the wrong line.** Excerpts were numbered over
  the synthetic `events_to_text` concatenation (message + stack trace + payload)
  and the text formatter showed the preceding context line, so reports cited an
  offset line number and the wrong content. Excerpts now cite the real input
  line on the matched line.
- **Catastrophic regex backtracking in the `driver_oom` signal.** The pattern
  used `re.DOTALL` with leading `(?=.*...)` lookaheads, which is O(n^2) on logs
  that lack `OutOfMemoryError`; a 9 MiB log went from hanging indefinitely to
  ~44 s. Rewritten as an equivalent, order-independent pattern.

### Added

- **Missing-column signal coverage.** `resolved_column_not_found` now matches
  the classic Spark wording `cannot resolve '<col>' given input columns: [...]`,
  in addition to the bracket error classes, with positive and negative fixtures.

### Performance

- **Cached diagnosis loading.** `load_diagnoses` now parses and validates the
  YAML set once per resolved directory for the life of a process (returning an
  isolated copy), so batch callers no longer re-read ~40 definitions per input:
  in-process corpus throughput rose from 1.2 to 15.4 files/s (per-file mean
  ~850 ms -> ~65 ms).
- **Deferred CLI imports.** The `diagnose` and `list-diagnoses` commands import
  the pipeline, loader, and formatters lazily, so `dedoc --version`/`--help`
  no longer pay to load them.

## [0.1.3] - 2026-10-13

### Added

- **Claude Code development system** (`.claude/`): specialist agents
  (`architect`, `backend-engineer`, `diagnosis-engineer`, `ai-agent-engineer`,
  `test-engineer`, `security-reviewer`, `documentation-engineer`,
  `oss-maintainer`), workflow skills (`add-diagnosis`, `add-platform`,
  `run-evals`, `security-review`, `release`), and `settings.json` permissions.

### Changed

- The publish workflow now passes `skip-existing`, so re-publishing an
  already-uploaded version (for example when a GitHub Release also triggers it)
  is a no-op instead of a failure.
- GitHub Action branding color updated.

## [0.1.1] - 2026-10-12

### Added

- **PyPI publishing via Trusted Publishing**: a new
  `.github/workflows/publish.yml` builds, `twine check`s, and publishes to
  TestPyPI or PyPI using OIDC — no stored API tokens. Adds `RELEASING.md`, PyPI
  `Project-URL`s, and PEP 639 license metadata (`Apache-2.0`).
- **Examples and benchmark scaffolding**: `examples/logs/` ships runnable sample
  inputs (Spark, Delta, Schema, ADF, and a benign log) with a documented
  expected outcome each, plus `make examples` to diagnose them all.
  `benchmarks/README.md` documents the graded `fixtures/` corpus, the metrics,
  and how `baseline.json` / `results.json` are regenerated and published.
- **Azure Data Factory platform adapter (Phase 7)**: six new deterministic
  diagnoses (`DEDOC-ADF-001` … `DEDOC-ADF-006`) covering linked-service
  connection failures, integration-runtime unavailability, missing datasets or
  paths, activity timeouts, missing/invalid pipeline parameters, and store
  throttling. Adds ADF signals and platform detection, positive/negative
  fixtures, and reference docs. The knowledge base is now **39 diagnoses**.
- **Reusable GitHub Action (Phase 6)**: `uses: Adez017/Data-Engineer-Doctor@main`
  diagnoses a log, directory, or glob (`path`), writes a `text`/`markdown`/`json`
  report to the job summary or a file, and can fail the job when a failure is
  diagnosed (`fail-on: diagnosed`), on unparseable input (`error`), or never
  (default). No AI key required. See
  [Use DEDoc in CI](docs/how-to/github-action.md).
- **Evaluation framework (§19)**: `python -m dedoc.evaluation` (`make evaluate`)
  grades the pipeline against the `fixtures/` corpus and reports diagnosis
  accuracy, precision, recall, abstention quality, confidence calibration,
  evidence coverage, unsupported-claim rate, remediation coverage and
  regression rate. It is wired into `make verify` as a strict CI gate with a
  committed regression baseline (`benchmarks/baseline.json`) and a published
  `benchmarks/results.json`. See the new
  [Evaluation & benchmarks](docs/reference/evaluation.md) reference.
- **Batch diagnosis loading**: `dedoc.core.pipeline.diagnose_file` accepts
  pre-loaded `diagnoses`, so callers grading many inputs (the evaluation harness)
  load the knowledge base once instead of per file.
- **Conclusion-first Markdown reports**: `--format markdown` now mirrors the text
  layout — diagnosis, severity/platforms, confidence, plain-language signals and
  possible causes, deduplicated evidence (`### Evidence:`), then
  `### What to do next` and `### References` per match.
- **Grouped `list-diagnoses` output**: the default text listing groups diagnoses
  by human-readable category (e.g. `Schema (6)`, `Data quality (5)`) with a total
  count; `--format json` is unchanged.
- **Conclusion-first text reports**: the text format now reads *What we found* →
  *Evidence* → *What to do next* → *Other candidates considered*, so the most
  actionable information comes first.
- **Plain-language details**: matched signals and hypotheses (e.g.
  `executor_oom`, `data_skew_caused_oom`) are translated into everyday terms in
  the text report; raw keys remain in the JSON output for machines.
- **Deduplicated evidence excerpts**: when multiple evidence items cite the same
  log lines, the long excerpt is shown once and later items reference it as
  "(same lines as evidence item N)".
- **`--color` CLI flag** for `dedoc diagnose`: `auto` (default; color only on a
  terminal), `always`, or `never`. The status line and confidence band are
  green/yellow/red on a terminal.
- **AI Provider Layer (Phase 5)**: optional AI explanation of the top
  diagnosis, fully isolated from the deterministic core (§13). No AI runs and
  no API key is needed unless the user explicitly opts in.
- **Provider abstraction** (`dedoc/providers/`): `ProviderConfig` (secret-free),
  a `No AI`/`NullProvider` default, OpenAI, any OpenAI-compatible endpoint
  (vLLM/LM Studio/gateways), local Ollama (no key), Azure OpenAI (deployment
  URL + `api-key` header), and Anthropic (`/v1/messages`). All built on the
  standard library — no runtime SDK dependencies.
- **Environment-based configuration only**: `DEDOC_AI_PROVIDER`,
  `DEDOC_AI_MODEL`, `DEDOC_AI_BASE_URL`, `DEDOC_OPENAI_API_KEY`,
  `DEDOC_AZURE_OPENAI_API_KEY`/`DEDOC_AZURE_OPENAI_ENDPOINT`,
  `DEDOC_ANTHROPIC_API_KEY`. API keys are never accepted as CLI arguments.
- **Redaction before every external call**: prompt construction
  (`dedoc/providers/prompt.py`) re-redacts and bounds the input excerpt; tests
  prove secrets cannot survive into the bytes sent to a provider.
- **Report schema v4** (`report_schema_version: "4"`): adds an `ai_explanation`
  object (`provider`, `model`, `text`) rendered in text/markdown/JSON formats.
- **CLI**: `dedoc diagnose --ai` plus `--provider`, `--ai-model`,
  `--ai-base-url` overrides.
- **SDK**: `dedoc.diagnose(..., ai=True)` and explicit
  `ProviderConfig`; `ProviderConfig` and `AIExplanation` are public API.
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

- **Documentation restructure and expansion**: removed the duplicated orphan
  pages and merged their content into the canonical ones (`usage.md` → CLI
  reference, `sdk.md` → SDK reference, security + privacy → a single
  **Security & privacy** page), moved the full diagnosis reference under
  `reference/`, and added a **Contributing** section. The home, architecture,
  confidence, security, and versioning pages were rewritten with more depth and
  **Mermaid diagrams**. The CLI reference was corrected (`list-diagnoses` has no
  `markdown`/`--color`; the `--ai` help now points at a real page).
- **FastAPI-inspired docs theme**: clean, minimal Material for MkDocs styling
  with FastAPI's teal/amber palette, a three-way auto/light/dark toggle, Roboto +
  Roboto Mono typography, theme-following code blocks, and a slim plain-language
  homepage (badge pills, short example, features list) replacing the heavier
  n8n-style hero, button, and card layout.
- **Report schema** moved from `"2"` to `"3"` (adds `investigation`).
- **Report schema** moved from `"3"` to `"4"` (adds `ai_explanation`).
- **Security guide** documents exactly what leaves the local environment when
  optional AI is enabled.
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

## [0.1.0] - 2026-10-08

Initial deterministic MVP: evidence-driven diagnosis for Spark/Databricks
failures with no AI/LLM dependency.