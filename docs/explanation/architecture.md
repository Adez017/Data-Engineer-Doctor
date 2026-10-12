# Architecture overview

## Summary

DEDoc is layered for deterministic diagnosis first, with optional extensions.

## Core layers

1. Input ingestion and normalization
2. Signal extraction and exception detection
3. Evidence scoring and candidate ranking
4. Report rendering (text/json/markdown)

## Optional layers

- Investigation mode: bounded, read-only context probes
- AI explanation mode: provider-based plain-language explanation

## Mode terminology

- **Deterministic mode**: default path, no AI dependency
- **Investigation mode**: optional context corroboration/contradiction checks
- **AI explanation mode**: optional narrative explanation only

!!! tip "See also"
    - [Confidence model](confidence-model.md)
    - [Security model](security-model.md)
