---
name: release
description: This skill should be used when cutting a release, bumping the version, updating the changelog, tagging, publishing to PyPI/TestPyPI, or listing the GitHub Action on the Marketplace. Trigger phrases include "release", "bump version", "tag", "publish to PyPI", "marketplace".
version: 0.1.0
---

# Release

Publishing is automated via **Trusted Publishing** (OIDC, no stored tokens).
Full detail lives in `RELEASING.md`; this is the checklist.

## Preconditions

- `main` is green: `make verify` passes.
- You have the user's explicit approval to push (see `AGENTS.md`).

## Steps

1. **Bump the version** in `pyproject.toml` (`[project].version`).
2. **Update `CHANGELOG.md`**: move content from `[Unreleased]` into a dated
   `## [X.Y.Z] - YYYY-MM-DD` section; leave `[Unreleased]` empty.
3. **Refresh lock/benchmarks** if dependencies or the corpus changed:
   `uv lock` (or `make setup`) and `make benchmark`; ensure `dedoc --version`
   reflects the new version (re-run `uv sync` so the editable metadata updates).
4. **Verify**: `make verify`.
5. **Commit and push** `main` — only with explicit approval.
6. **Tag**: `git tag -a vX.Y.Z -m "..." && git push origin vX.Y.Z`. The git tag
   and package version must match. **Never recreate `v0.1.0`.**
7. **Publish**:
   - Actions -> `publish` -> Run workflow -> `testpypi`; smoke-test:
     `pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ data-engineer-doctor`
   - Then Actions -> `publish` -> `pypi`, or publish a **GitHub Release** for
     the tag (auto-triggers the PyPI job). `skip-existing` makes re-runs a no-op.
8. **GitHub Action / Marketplace**: publish a Release to list that version on
   the Marketplace. This also triggers the PyPI job; if the package version is
   unchanged, `skip-existing` prevents a failure.

## Guardrails

- A PyPI version can only be uploaded once; to fix a mistake, bump the version
  (or yank on PyPI).
- Never force-push or move a published tag.
