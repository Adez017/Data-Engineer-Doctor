# Data handling & privacy at a glance

## Summary

Quick answer: deterministic mode keeps processing local; external transfer happens
only when AI explanation mode is explicitly enabled.

## What stays local

- Raw input logs (deterministic and investigation modes)
- Diagnosis ranking logic
- Redaction pipeline execution

## What may leave the machine (AI explanation mode only)

- Redacted report summary
- Bounded, re-redacted excerpt
- Provider API key in request header

## What never happens by default

- No AI calls unless `--ai` is set
- No raw secret values in report excerpts

!!! tip "See also"
    - [Security model](security-model.md)
    - [Configuration](../how-to/configuration.md)
