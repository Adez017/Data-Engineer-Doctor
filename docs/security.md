# Security

DEDoc processes potentially untrusted failure logs. Security is a first-class
design constraint (see the security baseline in `BUILD_PLAN.md`).

## Redaction

Before anything is printed as a report or excerpt, log content passes through a
redaction layer (`dedoc/core/redaction.py`) that:

- masks URLs with credentials, tokens, and password-style parameters;
- masks common secret names (`secret`, `token`, `password`, `api_key`, ...);
- masks email addresses and IPv4 addresses;
- clamps excerpts to a bounded length.

Excerpts included in evidence are always the redacted form.

## Trust boundaries

- Input parsing is tolerant and never crashes on malformed input.
- Large inputs (over 10 MiB) are rejected.
- The diagnostic engine only reads files and prints reports: it never writes
  to user data locations, runs other programs, or mutates production resources.
- The deterministic MVP performs **no** network calls except the
  link-check used by `make verify` (which only validates documentation URLs).

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