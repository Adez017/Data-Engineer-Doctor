# Confidence model

## Summary

Confidence is derived from weighted evidence, not guesswork.

## Weights

- Exact error signature: **40**
- Correlated runtime signal: **15**
- Declared exception observed: **20**
- Platform match: **20**
- Runtime metadata: **5**

## Thresholds

- Minimum score to report top candidate: **40**
- `HIGH`: **>= 70**
- `MEDIUM`: **>= 40**
- Lower scores: low/insufficient confidence

## Expected output

- Ranked candidates when multiple rules match
- Evidence list with type, weight, and source excerpt

!!! tip "See also"
    - [Diagnosis catalog](../reference/diagnosis-catalog.md)
    - [CLI reference](../reference/cli.md)
