# Security model

## Summary

DEDoc is designed to process untrusted logs with redaction-first handling.

## Security principles

- Redaction before rendering excerpts
- Tolerant input parsing
- Size limits on input
- Read-only operation for diagnosis flow
- Optional network usage only in AI explanation mode

## Investigation mode guarantees

- Read-only probes only
- Allowlisted tool surface
- Hard limits on iterations, calls, and timeout

## AI explanation mode guarantees

- Off by default
- Redacted and bounded prompt payload
- API keys from environment variables only

!!! tip "See also"
    - [Privacy at a glance](privacy-at-a-glance.md)
    - [Troubleshooting](../how-to/troubleshooting.md)
