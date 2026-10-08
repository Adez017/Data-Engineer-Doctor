"""Data Engineer Doctor (DEDoc) — evidence-driven diagnosis for data engineering failures."""

__all__ = ["__version__"]


def _read_version() -> str:
    from importlib.metadata import PackageNotFoundError, version

    try:
        return version("data-engineer-doctor")
    except PackageNotFoundError:
        return "0.0.0+local"


__version__ = _read_version()
