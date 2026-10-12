# When to use (and not use) DEDoc

## Summary

Choose DEDoc when deterministic, evidence-backed diagnosis is needed.

## Use DEDoc when

- You need repeatable diagnosis of pipeline failures
- You must justify conclusions with evidence and confidence
- You want CLI/JSON outputs for team workflows and automation
- You want optional investigation or AI explanation layers without changing core behavior

## Do not use DEDoc alone when

- You need live remediation execution (DEDoc is diagnostic, not orchestration)
- You need unsupported domain-specific failure catalogs not yet encoded
- You require full observability replacement (DEDoc complements, not replaces, monitoring)

## Decision table

| Situation | Recommendation |
| --- | --- |
| Triage unknown ETL failure log | Use DEDoc deterministic mode first |
| Need deeper runtime corroboration | Add investigation mode |
| Need explainable narrative for stakeholders | Add optional AI explanation mode |
| Need auto-fix execution | Use DEDoc + orchestration platform |

!!! tip "See also"
    - [Tutorial: first diagnosis](../tutorial/first-diagnosis.md)
    - [Recipes](recipes.md)
    - [Production adoption checklist](../operations/production-adoption-checklist.md)
