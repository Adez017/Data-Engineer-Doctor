# Contributing to Data Engineer Doctor

Thank you for your interest in contributing.

## Source of truth

[BUILD_PLAN.md](BUILD_PLAN.md) is the implementation source of truth.
Read it before contributing. Do not implement future phases unless explicitly
asked to advance.

## Ground rules

- Inspect existing code, tests, and documentation before editing.
- Prefer small, vertical slices that produce a working, tested capability.
- Never declare completion without running the required verification command:

  ```bash
  make verify
  ```

- Every new diagnosis must include positive, negative, and regression fixtures.
- If a requirement is ambiguous, document the ambiguity and stop rather than
  inventing behavior.
- Public diagnosis IDs (for example `DEDOC-SCHEMA-001`) are part of the public
  API and must not be casually renamed.

## Development setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
make verify
```

## Adding a diagnosis (Phase 2+)

A diagnosis PR must contain:

1. A YAML definition under `diagnoses/<category>/`.
2. Positive, negative, and regression fixtures under `fixtures/`.
3. Tests wiring those fixtures into the diagnosis loader and rule engine.
4. Documentation, including official references where available.

## Pull requests

- Keep PRs small and focused.
- Ensure `make verify` passes locally before opening a PR.
- Update documentation with every behavior change.
