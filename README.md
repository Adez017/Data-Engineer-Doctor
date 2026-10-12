# Data Engineer Doctor (DEDoc)

![License](https://img.shields.io/github/license/Adez017/Data-Engineer-Doctor)
![CI](https://github.com/Adez017/Data-Engineer-Doctor/actions/workflows/verify.yml/badge.svg)
![Docs](https://github.com/Adez017/Data-Engineer-Doctor/actions/workflows/docs.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue)

Evidence-driven diagnosis for data engineering failures.

## What is DEDoc?

DEDoc turns failure logs into deterministic, explainable diagnosis reports with
confidence scoring and concrete next steps.

- **Deterministic mode (default):** no AI, no API keys required.
- **Investigation mode (optional):** bounded, read-only context probing.
- **AI explanation mode (optional):** provider-based narrative explanation.

## Quick start

```bash
pip install -e ".[dev]"
dedoc diagnose path/to/error.log
```

Run it in CI with the reusable GitHub Action (`fail-on: diagnosed` turns a
diagnosed failure into a failed check):

```yaml
- uses: Adez017/Data-Engineer-Doctor@main
  with:
    path: logs/*.log
    fail-on: diagnosed
```

## Documentation

The full documentation site is the source of truth and follows a task-first
layout inspired by clean API docs:

- [Home](docs/index.md)
- [Tutorial: first diagnosis](docs/tutorial/first-diagnosis.md)
- [How-to guides](docs/how-to/installation.md)
- [Use in GitHub Actions](docs/how-to/github-action.md)
- [CLI reference](docs/reference/cli.md)
- [Python SDK reference](docs/reference/sdk.md)
- [Evaluation & benchmarks](docs/reference/evaluation.md)
- [Troubleshooting](docs/how-to/troubleshooting.md)
- [Top 25 user queries map](docs/reference/top-25-queries.md)

## Coverage snapshot

- 39 deterministic diagnoses across Spark, Delta, Schema, Data Quality,
  Connectivity, Performance, and Azure Data Factory domains.
- Structured outputs for text, JSON, and Markdown workflows.
- A first-class evaluation framework (`make evaluate`) with a committed
  regression baseline and published benchmark results.

## Development

```bash
make verify
```

## Security

See [docs/explanation/privacy-at-a-glance.md](docs/explanation/privacy-at-a-glance.md)
and [SECURITY.md](SECURITY.md).

## License

Apache-2.0. See [LICENSE](LICENSE).
