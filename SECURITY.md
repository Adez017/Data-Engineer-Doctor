# Security Policy

## Reporting a vulnerability

Please report security vulnerabilities privately via GitHub Security Advisories
(preferred) or by contacting the maintainers. Do **not** open a public issue
for a suspected vulnerability.

Include:

- A description of the issue and its impact.
- Steps to reproduce, or a proof of concept.
- Affected versions, if known.

## Security design principles

The following principles are mandated by BUILD_PLAN.md and are non-negotiable:

- Default to local parsing and deterministic analysis; no mandatory cloud upload.
- Redact secrets and credentials before any external AI call (Phase 5).
- Treat log content as untrusted input.
- Never execute arbitrary commands suggested by an LLM recommendation.
- Never allow an agent to mutate production resources.
- Use explicit tool allowlists for any agentic capability.
- Never expose raw logs in telemetry or analytics by default.
- Pin and audit dependencies; run dependency and static security checks in CI.

## Supported versions

This project is pre-1.0. Security fixes are applied to the latest release only.
