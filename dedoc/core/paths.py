"""Filesystem locations for diagnosis knowledge and fixtures.

Resolution order for diagnoses (documented in README/CONTRIBUTING):

1. ``DEDOC_DIAGNOSES_PATH`` environment variable (explicit override),
2. repository checkout: ``<repo root>/diagnoses`` (development),
3. packaged copy: ``<site-packages>/dedoc/diagnoses`` (installed wheel).
"""

from __future__ import annotations

import os
from pathlib import Path

from dedoc.core.errors import DiagnosisLoadError

ENV_DIAGNOSES_PATH = "DEDOC_DIAGNOSES_PATH"


def package_root() -> Path:
    """The installed/packaged ``dedoc`` directory."""
    return Path(__file__).resolve().parents[1]


def repo_root() -> Path:
    """Best-effort repository root (two levels above ``dedoc/core``)."""
    return Path(__file__).resolve().parents[2]


def resolve_diagnoses_path(explicit: str | Path | None = None) -> Path:
    """Locate the diagnoses directory, raising a user-facing error if absent."""
    candidates: list[Path] = []
    if explicit is not None:
        candidates.append(Path(explicit))
    env_value = os.environ.get(ENV_DIAGNOSES_PATH)
    if env_value:
        candidates.append(Path(env_value))
    candidates.append(repo_root() / "diagnoses")
    candidates.append(package_root() / "diagnoses")

    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    searched = ", ".join(str(c) for c in candidates)
    raise DiagnosisLoadError(f"no diagnoses directory found (searched: {searched})")


def fixtures_root() -> Path:
    """Repository fixtures directory (development checkout only)."""
    return repo_root() / "fixtures"
