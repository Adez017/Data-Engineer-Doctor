# Security

DEDoc processes potentially untrusted failure logs. Security is a first-class
design constraint (see the security baseline in `BUILD_PLAN.md`).

## Redaction

Before anything is printed as a report or excerpt, log content passes through a
redaction layer (`dedoc/core/redaction.py`) that:

- masks URLs with credentials and secret-bearing query parameters (SAS, tokens,
  signatures);
- masks common secret names and assignments (`secret`, `token`, `password`,
  `api_key`, `client_secret`, `sas_key`, ...);
- masks authorization headers, bearer tokens, AWS access-key ids, and
  Databricks PAT-style tokens, plus entire private-key blocks;
- clamps excerpts to a bounded length.

Excerpts included in evidence are always the redacted form.

## Trust boundaries

- Input parsing is tolerant and never crashes on malformed input.
- Large inputs (over 10 MiB) are rejected.
- The diagnostic engine only reads files and prints reports: it never writes
  to user data locations, runs other programs, or mutates production resources.
- The deterministic MVP performs **no** network calls except the
  link-check used by `make verify` (which only validates documentation URLs).

## Optional AI and data that leaves the machine (Phase 5)

AI is a strictly optional layer; the default path never contacts a network.
When you enable it (`--ai` or `ai=True`) with a configured provider
(`DEDOC_AI_PROVIDER`), the only data sent out is:

- the **redacted** report summary (status, top diagnosis, matched signals,
  evidence descriptions and redacted excerpts, recommendations);
- a bounded (few thousand characters), **re-redacted** excerpt of the input;
- the API key in a request **header** to the configured provider only.

Guarantees enforced by tests:

- Secrets in the raw log cannot survive into the bytes sent to a provider.
- API keys are only ever read from the environment; `ProviderConfig` and
  reports never contain them.
- If a provider is unavailable, AI is skipped and the deterministic report
  still succeeds.
- Providers never receive raw logs in telemetry; the provider layer performs
  no logging at all.

## Reporting a vulnerability

Do **not** open a public issue for security problems. Email the maintainers
via the contact published in `SECURITY.md` at the repository root, including a
minimal reproduction and any proposed patch. Coordinated disclosure is
appreciated; the project aims to respond within seven days.

## Supply chain

- Dependencies are pinned by `uv.lock` and audited with `pip-audit` in CI and
  in `make verify`.
- Ruff, mypy (strict), and the full test suite gate every change.
- The reference-URL check prevents dead or invented links in diagnosis YAMLs.