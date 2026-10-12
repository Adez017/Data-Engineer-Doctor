# Installation

## Summary

Set up DEDoc for local development, CI, or minimal runtime usage.

## Prerequisites

- Python 3.11 or 3.12
- `pip` (or `uv` if preferred)

## Steps

### Option A: development install (recommended)

```bash
pip install -e ".[dev]"
```

### Option B: runtime-only install

```bash
pip install -e .
```

### Option C: repository bootstrap with Makefile

```bash
make setup
```

## Expected output

- `dedoc` command available on your shell path
- `dedoc --help` prints CLI usage

## Common errors

| Problem | Likely cause | Fix |
| --- | --- | --- |
| `dedoc: command not found` | Environment not activated | Activate venv or reinstall |
| Dependency resolution fails | Old pip or network issue | Upgrade pip, retry install |
| Wrong Python version | Python <3.11 | Use 3.11/3.12 |

!!! tip "Decision table"
    | I need to... | Recommended setup |
    | --- | --- |
    | Develop and contribute | `pip install -e ".[dev]"` |
    | Just run diagnoses | `pip install -e .` |
    | Use repo defaults | `make setup` |

!!! tip "See also"
    - [Tutorial: first diagnosis](../tutorial/first-diagnosis.md)
    - [Versioning & compatibility](../explanation/versioning-compatibility.md)
