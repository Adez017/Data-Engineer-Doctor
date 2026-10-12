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
and auditable.

## Start in 60 seconds

```bash
pip install -e ".[dev]"

# Diagnose a failure log
dedoc diagnose path/to/executor-oom.log

# Machine-readable output
dedoc diagnose path/to/error.json --format json

# List bundled diagnoses
dedoc list-diagnoses --format json
```

## Common workflows

```bash
# Include structured runtime context
dedoc diagnose spark-failure.log --investigate --context context.yaml

# Add an optional AI explanation (explicit opt-in)
export DEDOC_AI_PROVIDER=ollama
export DEDOC_AI_MODEL=llama3.2
dedoc diagnose spark-failure.log --ai
```

## Why teams use DEDoc

* **Deterministic by default** — same input, same result; no AI dependency.
* **Explainable confidence** — every match is backed by weighted evidence.
* **Operationally safe** — built-in secret redaction before report output.
* **Flexible output** — text for humans, JSON/Markdown for automation.
* **Optional extensions** — bounded investigation and AI explanation when you opt in.

## Documentation map

| You want to... | Go here |
| --- | --- |
| Run DEDoc from the CLI | [Usage](usage.md) |
| Understand all diagnosis rules | [Diagnosis reference](diagnosis-reference.md) |
| Integrate with Python code | [Python SDK](sdk.md) |
| Contribute fixes or new diagnoses | [Contributing](contributing.md) |
| Review privacy and disclosure policy | [Security](security.md) |
| Browse source and releases | [GitHub](https://github.com/Adez017/Data-Engineer-Doctor) |

## Current release snapshot

The deterministic core is complete and exercised by integration tests on every
fixture. This release includes:

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

AI and investigation are optional layers; no core diagnosis path depends on them.

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

## License

Apache-2.0