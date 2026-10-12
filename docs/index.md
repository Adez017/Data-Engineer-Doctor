# Data Engineer Doctor (DEDoc)

Open-source, evidence-driven diagnosis for data engineering failures.

<div class="dedoc-hero">
  <img src="assets/logo.svg" alt="Data Engineer Doctor logo" class="dedoc-hero-logo" />
  <div class="dedoc-badges">
    <span class="dedoc-badge"><strong>Deterministic</strong> by default</span>
    <span class="dedoc-badge"><strong>33</strong> bundled diagnoses</span>
    <span class="dedoc-badge"><strong>Python</strong> 3.11 / 3.12</span>
  </div>
</div>

## What it is

DEDoc reads failure logs and returns deterministic, explainable diagnoses with
confidence scoring and concrete next steps.

- Deterministic mode (default): no AI, no API key, same input -> same output
- Investigation mode (optional): read-only context probes for extra evidence
- AI explanation mode (optional): provider-based plain-language explanation

## Install

```bash
pip install -e ".[dev]"
```

## First successful diagnosis

```bash
dedoc diagnose path/to/error.log
```

Expected result:

- `Status: diagnosed` or `Status: insufficient_evidence`
- Top confidence band and recommended next actions

## Next actions

- New here? Start with [Tutorial: first diagnosis](tutorial/first-diagnosis.md)
- Need commands? Use [CLI reference](reference/cli.md)
- Want practical scenarios? Go to [Recipes](how-to/recipes.md)
- Running into issues? Open [Troubleshooting](how-to/troubleshooting.md)


## Search tips

Common terms users search for: `spark oom`, `schema mismatch`, `delta conflict`,
`insufficient evidence`, `dedoc json output`, `dedoc ai mode`, `inputerror`.

!!! tip "See also"
    - [When to use DEDoc](how-to/when-to-use.md)
    - [Top 25 user queries map](reference/top-25-queries.md)
    - [Data handling & privacy at a glance](explanation/privacy-at-a-glance.md)
