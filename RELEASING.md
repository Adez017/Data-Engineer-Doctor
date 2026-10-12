# Releasing

This project publishes to [PyPI](https://pypi.org/) as `data-engineer-doctor`
using **Trusted Publishing** — no API tokens are stored anywhere. GitHub
Actions authenticates to PyPI with a short-lived OpenID Connect (OIDC) token.

Two workflows are involved:

| Workflow | Purpose |
| --- | --- |
| `.github/workflows/release.yml` | Prepare-only: builds artifacts and drafts a GitHub Release on a new tag. |
| `.github/workflows/publish.yml` | Builds, `twine check`s, and publishes to TestPyPI or PyPI. |

## One-time setup (maintainer)

1. Create a [PyPI](https://pypi.org/account/register/) account (and a
   [TestPyPI](https://test.pypi.org/account/register/) account) and enable 2FA.
2. Add a **pending publisher** for the yet-unpublished project.

   On https://pypi.org/manage/account/publishing/ and
   https://test.pypi.org/manage/account/publishing/, both with:

   | Field | Value |
   | --- | --- |
   | PyPI project name | `data-engineer-doctor` |
   | Owner | `Adez017` |
   | Repository name | `Data-Engineer-Doctor` |
   | Workflow name | `publish.yml` |
   | Environment name | `pypi` (PyPI) / `testpypi` (TestPyPI) |

3. (Optional) Create the matching `pypi` and `testpypi`
   [GitHub environments](https://docs.github.com/actions/deployment/targeting-different-environments/using-environments-for-deployment)
   if you want manual approval before publishing.

The workflow name and environment name must match exactly, or PyPI will reject
the upload.

## Publish flow

Always test on TestPyPI first:

1. Ensure `main` is green (`make verify`) and the version in `pyproject.toml` is
   set for the release.
2. Run the **publish** workflow manually → target `testpypi`.
3. Verify the install from TestPyPI:

   ```bash
   pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ data-engineer-doctor
   dedoc --version
   ```

4. Run the **publish** workflow manually → target `pypi`, **or** publish a
   GitHub Release (the `release` trigger publishes to PyPI automatically).
5. Verify: https://pypi.org/project/data-engineer-doctor/

!!! warning "A version can be uploaded only once"
    PyPI does not allow re-uploading the same version. To fix a bad release,
    bump the version and publish again; use a `.devN`/`.postN` or yank the
    release on PyPI.

## Versioning

- The version lives in `pyproject.toml` (`[project].version`).
- Bump it, update `CHANGELOG.md`, and land the change on `main` before
  publishing.
- The git tag (e.g. `v0.1.0`) and the package version should match.
- Diagnosis IDs are additive and never reused, independent of the version.

## Manual fallback

If you need to publish without Actions, with an API token from
https://pypi.org/manage/account/token/ :

```bash
pip install ".[dev]"
python -m build
python -m twine check dist/*
TWINE_USERNAME=__token__ TWINE_PASSWORD=pypi-... python -m twine upload dist/*
```

For TestPyPI, add `--repository-url https://test.pypi.org/legacy/`.
