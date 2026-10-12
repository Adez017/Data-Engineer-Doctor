# Versioning & compatibility

## Summary

Compatibility expectations for runtime, outputs, and upgrades.

## Runtime compatibility

- Supported Python versions: 3.11 and 3.12
- Current release line: 0.1.x

## Output compatibility

- JSON reports include version metadata (`dedoc_version`, `report_schema_version`)
- Stable diagnosis IDs are treated as public API

## Upgrade notes

- Review `CHANGELOG.md` for behavior changes
- Validate downstream JSON consumers against schema/version fields
- Re-run representative fixture logs before production rollout

!!! tip "See also"
    - [Production adoption checklist](../operations/production-adoption-checklist.md)
    - [CLI reference](../reference/cli.md)
