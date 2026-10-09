# DEDoc — Data Engineer Doctor

<div class="dedoc-hero">
  <span class="dedoc-hero__kicker">Booted · Deterministic · No LLM</span>
  <p class="dedoc-hero__lead">Evidence-driven diagnosis for <mark>data engineering failures</mark>.</p>
  <p class="dedoc-hero__sub">
    DEDoc accepts failure logs, error messages, and structured events; normalizes them into a
    canonical failure model; applies deterministic diagnostic rules; scores the evidence; and
    produces an actionable, evidence-backed report.
  </p>
  <div class="dedoc-badges">
    <span class="dedoc-badge"><span class="dedoc-badge__dot"></span>33 diagnoses</span>
    <span class="dedoc-badge"><span class="dedoc-badge__dot"></span>Apache-2.0</span>
    <span class="dedoc-badge"><span class="dedoc-badge__dot"></span>Python 3.11 / 3.12</span>
    <span class="dedoc-badge"><span class="dedoc-badge__dot"></span>Explainable scoring</span>
  </div>
  <div class="dedoc-buttons">
    <a class="dedoc-btn dedoc-btn--primary" href="usage/">Quick start<span class="dedoc-btn__arrow">&rarr;</span></a>
    <a class="dedoc-btn" href="diagnosis-reference/">Diagnosis reference</a>
    <a class="dedoc-btn" href="https://github.com/Adez017/Data-Engineer-Doctor">GitHub</a>
  </div>
</div>

It works today **without any AI or LLM** — no API keys, no external model calls.
Every conclusion is repeatable, explainable, and auditable.

## Find your way around

<div class="dedoc-grid">
  <a class="dedoc-card" href="usage/">
    <span class="dedoc-card__icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/></svg></span>
    <span class="dedoc-card__title">Usage</span>
    <span class="dedoc-card__desc">CLI commands, output formats, exit codes, and report walkthroughs.</span>
  </a>
  <a class="dedoc-card" href="diagnosis-reference/">
    <span class="dedoc-card__icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg></span>
    <span class="dedoc-card__title">Diagnosis reference</span>
    <span class="dedoc-card__desc">Every bundled diagnosis, its signals, hypotheses, and scoring.</span>
  </a>
  <a class="dedoc-card" href="sdk/">
    <span class="dedoc-card__icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg></span>
    <span class="dedoc-card__title">Python SDK</span>
    <span class="dedoc-card__desc">Use DEDoc as a library inside your own pipeline and tooling.</span>
  </a>
  <a class="dedoc-card" href="contributing/">
    <span class="dedoc-card__icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg></span>
    <span class="dedoc-card__title">Contributing</span>
    <span class="dedoc-card__desc">How to add a diagnosis, fixtures, verification, and documentation.</span>
  </a>
  <a class="dedoc-card" href="security/">
    <span class="dedoc-card__icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg></span>
    <span class="dedoc-card__title">Security</span>
    <span class="dedoc-card__desc">Secret redaction guarantees and the vulnerability reporting process.</span>
  </a>
  <a class="dedoc-card" href="https://github.com/Adez017/Data-Engineer-Doctor">
    <span class="dedoc-card__icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/></svg></span>
    <span class="dedoc-card__title">Open source</span>
    <span class="dedoc-card__desc">Source code, issues, and releases on GitHub.</span>
  </a>
</div>

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

## Creator

<div class="dedoc-creator">
  <span class="dedoc-creator__avatar">AS</span>
  <span>
    <span class="dedoc-creator__name">Aditya Singh Rathore</span><br/>
    <span class="dedoc-creator__role">Creator &amp; maintainer — Data Engineer Doctor</span><br/>
    <span class="dedoc-creator__links">
      <a href="https://github.com/Adez017">GitHub</a> ·
      <a href="mailto:rathoreadityasingh40@gmail.com">Email</a>
    </span>
  </span>
</div>

## License

Apache-2.0