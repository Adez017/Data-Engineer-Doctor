# Data Engineer Doctor

<div class="dedoc-hero">
  <img src="assets/logowithtext.png" alt="Data Engineer Doctor" class="dedoc-hero-wordmark" />
  <p class="dedoc-tagline">Evidence-driven diagnosis for data engineering failures.</p>
  <div class="dedoc-hero-actions">
    <a class="dedoc-cta dedoc-cta-primary" href="tutorial/first-diagnosis/">Get started</a>
    <a class="dedoc-cta dedoc-cta-secondary" href="reference/cli/">CLI reference</a>
  </div>
</div>

<div class="dedoc-grid dedoc-grid-feature">
  <div class="dedoc-card">
    <h3>Fast to diagnose</h3>
    <p>Turn failure logs into deterministic root-cause signals in one command.</p>
  </div>
  <div class="dedoc-card">
    <h3>Easy to adopt</h3>
    <p>Start with CLI defaults and add investigation or AI explanation only when needed.</p>
  </div>
  <div class="dedoc-card">
    <h3>Production-ready outputs</h3>
    <p>Use text, JSON, and Markdown reports to plug directly into runbooks and workflows.</p>
  </div>
</div>

<div class="dedoc-grid dedoc-grid-metrics">
  <div class="dedoc-card dedoc-metric">
    <h3>39</h3>
    <p>bundled diagnoses</p>
  </div>
  <div class="dedoc-card dedoc-metric">
    <h3>Deterministic</h3>
    <p>by default</p>
  </div>
  <div class="dedoc-card dedoc-metric">
    <h3>Python</h3>
    <p>3.11 / 3.12</p>
  </div>
</div>

## Installation

```bash
pip install -e ".[dev]"
```

## First diagnosis

```bash
dedoc diagnose path/to/error.log
```

Expected result:

- `Status: diagnosed` or `Status: insufficient_evidence`
- Top confidence band and recommended next actions

## Learn more

- [Tutorial: first diagnosis](tutorial/first-diagnosis.md)
- [How-to guides](how-to/installation.md)
- [Reference docs](reference/cli.md)
- [Troubleshooting](how-to/troubleshooting.md)

!!! tip "See also"
    - [When to use DEDoc](how-to/when-to-use.md)
    - [Top 25 user queries map](reference/top-25-queries.md)
    - [Data handling & privacy at a glance](explanation/privacy-at-a-glance.md)
