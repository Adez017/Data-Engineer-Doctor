# Data Engineer Doctor (DEDoc)

<small>Open-source, evidence-driven diagnosis for modern data engineering failures.</small>

<div class="dedoc-badges">
  <span class="dedoc-badge"><strong>33</strong> diagnoses</span>
  <span class="dedoc-badge"><strong>Apache-2.0</strong></span>
  <span class="dedoc-badge"><strong>Python 3.11 / 3.12</strong></span>
  <span class="dedoc-badge"><strong>no</strong> AI or API keys required</span>
</div>

DEDoc turns failure logs into actionable, evidence-backed reports. It detects the
data engineering platform, extracts exception types and error signatures, matches
them against a versioned knowledge base of **33 deterministic diagnoses**, and
scores the evidence into a confidence band — with concrete next steps.

It works today **without any required AI or LLM**: no API keys, no external model
calls, nothing leaves your machine. Every conclusion is repeatable, explainable,
and auditable. An optional AI layer can explain the top diagnosis when you
explicitly opt in.

## Quick start

```bash
pip install -e ".[dev]"

# Diagnose a Spark failure log
dedoc diagnose path/to/executor-oom.log

# Machine-readable output
dedoc diagnose path/to/error.json --format json

# List every bundled diagnosis
dedoc list-diagnoses --format json
```

## Example

```text
$ dedoc diagnose logs/executor-oom.log

What we found:
  DEDOC-SPARK-001 Executor Out of Memory
  Severity: critical | Platforms: spark, databricks
  Confidence: HIGH (80/100)
  Matched exception types: OutOfMemoryError
  Possible causes: Executor Memory Exhausted; Data Skew Caused OOM

Evidence:
  1. Exact error signature matched: executor_oom (+40)
      > line 6: 24/10/08 13:10:12 INFO TaskSetManager: Starting task 42.0 ...

What to do next:
  Immediate:
    - Identify the failing task and stage; a single large partition or a skew often causes the failure.
  Prevention:
    - Enable and review AQE skew join optimization for joins on skewed keys.
```

## Features

* **Deterministic core** — no AI dependency; identical input always produces the
  same report.
* **Explainable scoring** — every conclusion cites the evidence, its weight, and
  a confidence band (HIGH / MEDIUM / insufficient evidence).
* **Plain-language reports** — conclusion-first text output with color-coded
  confidence; JSON and Markdown for machines and issue trackers.
* **Secret redaction** — passwords, tokens, and keys are redacted from any report
  output before it leaves the machine.
* **Optional AI**, fully isolated — OpenAI, local Ollama, Azure OpenAI, and
  Anthropic providers explain a diagnosis only when asked; keys are read only
  from environment variables.
* **Bounded investigation** — an optional, read-only tool layer probes structured
  runtime context (runs, schemas, metrics, query plans) without AI.
* **CLI + SDK + CI** — a `dedoc` command, a typed Python API, and GitHub Actions
  running the single `make verify` gate.

## Find your way around

* [Usage](usage.md) — CLI commands, output formats, exit codes, and report walkthroughs.
* [Diagnosis reference](diagnosis-reference.md) — every bundled diagnosis, its signals, hypotheses, and scoring.
* [Python SDK](sdk.md) — use DEDoc as a library inside your own pipeline and tooling.
* [Contributing](contributing.md) — how to add a diagnosis, fixtures, verification, and documentation.
* [Security](security.md) — secret redaction guarantees and the vulnerability reporting process.
* [GitHub](https://github.com/Adez017/Data-Engineer-Doctor) — source code, issues, and releases.

## Status

The deterministic core is complete and exercised by integration tests on every
fixture. The current build contains:

* **Phase 2: knowledge base**. 33 diagnoses with fixtures, scoring, coverage.
* **Phase 3: deterministic pipeline**. Analysis, evidence, reports.
* **Phase 4: bounded investigation agent**. Read-only, allowlisted tools that
  probe structured runtime context without AI.
* **Phase 5: optional AI provider layer**. Isolated providers (OpenAI, local
  Ollama, Azure OpenAI, Anthropic) that explain a diagnosis only when you opt
  in; the deterministic path never requires a key.
* **Phase 6: integrations**. CLI, Python SDK, CI (GitHub Actions).
* **Phase 8: public launch (partial)**. Docs, contribution toolkit,
  prepare-only release workflow.

AI and agentic investigation are optional layers; no current feature depends on
them.

## Requirements

* Python 3.11 or 3.12
* GNU Make (for the verification workflow)

## Development

```bash
make verify
```

`make verify` is the single source of truth for local and CI validation:
formatting, linting, strict type checking, the full test suite, diagnosis
validation, reference-URL checks, MkDocs build, a dependency audit, and a
packaged build. A change is not complete until it passes.

## Creator

<span class="dedoc-creator">Aditya Singh Rathore — [GitHub](https://github.com/Adez017) · [Email](mailto:rathoreadityasingh40@gmail.com)</span>

## License

Apache-2.0