# Data Engineer Doctor (DEDoc)

Open-source, evidence-driven diagnosis for modern data engineering failures.

DEDoc accepts failure logs, error messages, and structured events; normalizes
them into a canonical failure model; applies deterministic diagnostic rules;
scores the evidence; and produces an actionable, evidence-backed report.

It works today **without any AI or LLM** — no API keys, no external model calls.
Every conclusion is repeatable, explainable, and auditable.

## What it does

- Detects the data engineering platform from raw failure text
  (`spark`, `databricks`, or unknown).
- Extracts exception types, error signatures, and correlated runtime signals.
- Matches against a versioned, YAML-based diagnostic knowledge base
  (**33 deterministic diagnoses** across schema, data quality, Spark, Delta,
  connectivity, and performance).
- Ranks hypotheses with an explicit, documented scoring model and a confidence
  band (HIGH / MEDIUM / insufficient evidence).
- Redacts secrets from any report output before it leaves the machine.

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

The report singles out a top candidate with its score, the evidence that drove
it, the competing diagnoses considered, and concrete next steps.

## Status

The deterministic MVP (v0.1) is the active build target:

- **Phase 2 — knowledge base**: 33 diagnoses with fixtures, scoring, coverage.
- **Phase 3 — deterministic pipeline**: analysis, evidence, reports.
- **Phase 6 — integrations**: CLI, Python SDK, CI (GitHub Actions).
- **Phase 8 — public launch**: docs, contribution toolkit, prepare-only release.

Agentic/AI investigation is a **later, optional** layer and is not required for
any current feature.

## Requirements

- Python 3.11 or 3.12
- GNU Make (for the verification workflow)

## Development

```bash
make verify
```

`make verify` is the single source of truth for local and CI validation:
formatting, linting, strict type checking, the full test suite, diagnosis
validation, reference-URL checks, MkDocs build, a dependency audit, and a
packaged build. A change is not complete until it passes.

## Documentation

- [Usage](usage.md) — CLI commands, formats, and exit codes
- [Python SDK](sdk.md) — using DEDoc as a library
- [Diagnosis reference](diagnosis-reference.md) — every bundled diagnosis
- [Contributing](contributing.md) — how to add a diagnosis
- [Security](security.md) — redaction and vulnerability reporting

## License

Apache-2.0