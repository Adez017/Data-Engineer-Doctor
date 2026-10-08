# Data Engineer Doctor (DEDoc)

Open-source, evidence-driven diagnosis for modern data engineering failures.

DEDoc accepts logs, error messages, and structured events; normalizes them into a
canonical failure model; applies deterministic diagnostic rules; and produces an
actionable, evidence-backed report — without requiring an AI API key.

## Status

**Phase 1 (Foundation)** — early and under active development.
The deterministic diagnostic path is being built first, exactly as specified in
[BUILD_PLAN.md](BUILD_PLAN.md). AI/agentic investigation is a later, optional layer.

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
```

## Development

```bash
make verify   # authoritative check: format, lint, types, tests, schema validation, build
```

`make verify` is the single source of truth for local and CI validation.
A change is not complete until it passes.

## Documentation

- [BUILD_PLAN.md](BUILD_PLAN.md) — master build & implementation plan (source of truth)
- [CONTRIBUTING.md](CONTRIBUTING.md) — how to contribute
- [SECURITY.md](SECURITY.md) — how to report vulnerabilities

## License

Apache-2.0 — see [LICENSE](LICENSE).
