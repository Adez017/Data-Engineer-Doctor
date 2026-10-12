# Versioning & compatibility

DEDoc follows [Semantic Versioning](https://semver.org/) (`MAJOR.MINOR.PATCH`).
The project is pre-1.0 (`0.x`), so minor releases may add or refine behavior,
but the interfaces below are treated as stable contracts.

## Compatibility at a glance

| Surface | Status | Notes |
| --- | --- | --- |
| Python runtime | Stable | 3.11 and 3.12 are supported and tested in CI. |
| Public diagnosis IDs | Stable | Treated as public API; never renamed or repurposed. |
| CLI commands & flags | Stable | Adding flags is non-breaking; removals follow deprecation. |
| JSON report fields | Stable | Additive changes only within a major line. See `report_schema_version`. |
| Python SDK surface | Stable | The names listed in the [SDK reference](../reference/sdk.md#public-api). |
| Internal `dedoc.*` modules | Unstable | Implementation detail; may change between releases. |

## The report schema

Every JSON report carries `dedoc_version` (the release that produced it) and
`report_schema_version` (the shape of the payload, currently `4`). Consumers
should key off `report_schema_version`, not `dedoc_version`, and tolerate new
fields.

```json
{
  "dedoc_version": "0.1.0",
  "report_schema_version": "4",
  "status": "diagnosed",
  "top_confidence_band": "HIGH",
  "matches": [ ... ]
}
```

## Deprecation policy

- A removed CLI flag, SDK name, or report field is deprecated for at least one
  minor release first, with a changelog note and a warning where practical.
- Diagnosis IDs are additive. A retired diagnosis ID is never reused.
- Internal modules may change at any time without notice.

## Upgrading

1. Read the [changelog](https://github.com/Adez017/Data-Engineer-Doctor/blob/main/CHANGELOG.md)
   for the target release.
2. Check the [evaluation results](https://github.com/Adez017/Data-Engineer-Doctor/blob/main/benchmarks/results.json)
   for accuracy changes versus the previous baseline.
3. Run your own representative logs and confirm the output shape.

!!! tip "See also"
    - [Installation](../how-to/installation.md)
    - [Python SDK reference](../reference/sdk.md)
    - [Production adoption checklist](../operations/production-adoption-checklist.md)
