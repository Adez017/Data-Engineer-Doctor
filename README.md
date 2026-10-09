# Data Engineer Doctor (DEDoc)

![License](https://img.shields.io/github/license/Adez017/Data-Engineer-Doctor)
![CI](https://github.com/Adez017/Data-Engineer-Doctor/actions/workflows/verify.yml/badge.svg)
![Docs](https://github.com/Adez017/Data-Engineer-Doctor/actions/workflows/docs.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue)

Evidence-driven diagnosis for data engineering failures, with no AI required.

## What is DEDoc?

DEDoc turns messy failure logs into actionable, evidence-backed reports. Point
it at a Spark executor crash, a Delta table conflict, a schema mismatch, or a
connectivity timeout, and it tells you what went wrong, how confident it is,
and what to try next. Every claim is grounded in evidence from your input, so
you can trust the answer and explain it to your team in a meeting, not just to
a machine.

The engine is fully deterministic. It does not call an LLM, never needs an API key,
and never sends your logs anywhere. The same input always produces the same
report, which makes debugging, testing, and auditing straightforward.

## Highlights

- **33 deterministic diagnoses** across schema, data quality, Spark, Delta,
  connectivity, and performance, each with enforced fixture coverage.
- **Confidence scoring**: every match is scored 0-100 and labeled with a
  confidence band (HIGH, MEDIUM, or LOW) so you know how much weight to give it.
- **Ranked results**: when several rules match, DEDoc shows a scoreboard of
  candidates, full evidence and actions for the top one, and a compact summary
  for the alternatives.
- **Bounded investigation agent (optional)**: the `--investigate` flag inspects
  structured context (pipeline runs, schema snapshots, metrics, query plans,
  extra logs) through read-only, allowlisted tools. It corroborates the top
  diagnosis or reports a contradiction, respects hard time and step limits, and
  abstains when it has too little context instead of guessing.
- **No vendor lock-in**: plain logs and structured JSON events work out of the
  box, with a small Python SDK on top.
- **Professional toolkit**: MkDocs documentation site, GitHub Actions CI on
  Python 3.11 and 3.12, a code of conduct, issue/PR templates, and a
  prepare-only release workflow.

## Diagnosis coverage

| Category | IDs | Focus |
| --- | --- | --- |
| Spark | `DEDOC-SPARK-001` to `DEDOC-SPARK-008` | Executor and driver OOM, lost executors, task failures, data skew, shuffle and broadcast failures, stage failures |
| Delta | `DEDOC-DELTA-001` to `DEDOC-DELTA-005` | Concurrent modifications, schema mismatch, missing tables, invalid partition columns, transaction conflicts |
| Schema | `DEDOC-SCHEMA-001` to `DEDOC-SCHEMA-006` | Missing columns, type mismatches, duplicates, evolution failures, nested mismatches |
| Data quality | `DEDOC-QUALITY-001` to `DEDOC-QUALITY-005` | Null violations, duplicate keys, invalid dates, invalid numerics, referential issues |
| Connectivity | `DEDOC-CONN-001` to `DEDOC-CONN-005` | Authentication failures, timeouts, DNS issues, permission problems, unavailable endpoints |
| Performance | `DEDOC-PERF-001` to `DEDOC-PERF-004` | Small files, excessive shuffle, missing partition pruning, oversized broadcasts |

The full reference lives in [docs/diagnosis-reference.md](docs/diagnosis-reference.md).

## Quick start

**Requirements:** Python 3.11 or newer, GNU Make (for the verification workflow).

```bash
pip install -e ".[dev]"
```

**First diagnosis:**

```bash
dedoc diagnose logs/executor-oom.log
```

```
Data Engineer Doctor
Input:     logs/executor-oom.log
Platform:  spark
Status:    diagnosed
Confidence: HIGH
Events:    1
Version:   0.1.0

DEDOC-SPARK-001 selected with HIGH confidence (80/100) based on 3 evidence item(s).
...
```

Output formats: `text` (default), `json` for programmatic use, and `markdown`
for embedding in issue reports or dashboards.

**Structured investigation:**

```bash
dedoc diagnose spark-failure.log --investigate --context context.yaml
```

See [docs/usage.md](docs/usage.md) for the full CLI reference and the context
file format.

## Python SDK

```python
from dedoc import diagnose, list_diagnoses

for d in list_diagnoses():
    print(d.id, d.name, d.severity.default)

report = diagnose("logs/executor-oom.log", investigate=True)
print(report.status, report.top_confidence_band)
for match in report.matches:
    print(match.id, match.score, match.confidence_band, match.hypotheses)
```

The public API is deliberately tiny: `diagnose`, `list_diagnoses`,
`Diagnosis`, `DiagnosisReport`, `AgentConfig`, `InvestigationContext`, and
`InvestigationRecord`. See [docs/sdk.md](docs/sdk.md) for details.

## Development

```bash
make verify
```

`make verify` is the single source of truth for local and CI validation. It
runs formatting, linting, strict type checking, the full test suite, diagnosis
validation, documentation link checks and build, dependency audit, and a
package build. A change is not complete until it passes.

## Documentation

The MkDocs site in [`docs/`](docs/) covers usage, the Python SDK, the complete
diagnosis reference, contributing, and security. Also useful:

- [BUILD_PLAN.md](BUILD_PLAN.md): the master build and implementation plan
- [CONTRIBUTING.md](CONTRIBUTING.md): how to contribute
- [CHANGELOG.md](CHANGELOG.md): version history
- [SECURITY.md](SECURITY.md): how to report vulnerabilities

## Project status

DEDoc is an actively developed, production-minded open-source project.
The deterministic core is complete and exercised by integration tests on every
fixture. Future phases are planned, and optional AI-provider integration is a
deliberately separate, later layer as described in `BUILD_PLAN.md`. Nothing in
the deterministic path depends on it.

## Contributing

Found a gap in the rules or a new failure mode? Open an issue with a redacted,
representative log, or submit a pull request. Fixture coverage is enforced, so
new diagnostics ship with tests that prove they work. Please read
[CONTRIBUTING.md](CONTRIBUTING.md) first.

## License

Apache-2.0. See [LICENSE](LICENSE).