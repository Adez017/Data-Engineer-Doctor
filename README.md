# Data Engineer Doctor (DEDoc)

Open-source, evidence-driven diagnosis for modern data engineering failures.

DEDoc accepts logs, error messages, and structured events; normalizes them into a
canonical failure model; applies deterministic diagnostic rules; scores the
evidence; and produces an actionable, evidence-backed report — **without any AI
or LLM** (no API key required).

## Status

Deterministic MVP **v0.1** — active:

- **33 deterministic diagnoses** across schema, data quality, Spark, Delta,
  connectivity, and performance, with enforced fixture coverage.
- Deterministic pipeline: platform detection → exception/signal extraction →
  rule matching → evidence scoring → confidence bands (HIGH/MEDIUM).
- **Bounded investigation agent**: optional `--investigate` mode that inspects
  structured context (runs, schema, metrics, query plan, logs) through
  read-only allowlisted tools, enforces hard limits, and either corroborates
  the top diagnosis or reports a contradiction — fully deterministic, no AI.
- CLI + Python SDK + GitHub Actions CI on Python 3.11 and 3.12.
- Apache-2.0 licensed with a full open-source toolkit (docs, code of conduct,
  templates, changelog) and a prepare-only release workflow.

AI providers are a later, optional layer per [BUILD_PLAN.md](BUILD_PLAN.md).

## Requirements

- Python 3.11+
- GNU Make (for the verification workflow)

## Installation

```bash
pip install -e ".[dev]"
```

## Usage

```bash
dedoc diagnose path/to/error.log
dedoc diagnose path/to/error.log --format json
dedoc diagnose path/to/error.log --format markdown
dedoc diagnose path/to/error.log --investigate --context context.yaml
dedoc list-diagnoses            # every bundled diagnosis definition
```

As a library:

```python
from dedoc import diagnose, list_diagnoses

report = diagnose("path/to/error.log")
print(report.status, report.top_confidence_band)
for m in report.matches:
    print(m.id, m.score, m.confidence_band, m.hypotheses)
```

## Development

```bash
make verify   # format, lint, types, tests, diagnosis validation, link checks,
              # docs build, dependency audit, package build
```

`make verify` is the single source of truth for local and CI validation.
A change is not complete until it passes.

## Documentation

MkDocs site in [`docs/`](docs/): usage, Python SDK, the full diagnosis
reference, contributing, and security. Plus:

- [BUILD_PLAN.md](BUILD_PLAN.md) — master build & implementation plan (source of truth)
- [CONTRIBUTING.md](CONTRIBUTING.md) — how to contribute
- [CHANGELOG.md](CHANGELOG.md) — version history
- [SECURITY.md](SECURITY.md) — how to report vulnerabilities

## License

Apache-2.0 — see [LICENSE](LICENSE).