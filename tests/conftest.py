"""Shared test fixtures."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner, Result

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    return REPO_ROOT / "fixtures"


@pytest.fixture(scope="session")
def cli() -> CliRunner:
    return CliRunner()


def all_output(result: Result) -> str:
    """Combine stdout and stderr across click/typer versions."""
    chunks = [result.output]
    try:
        stderr = result.stderr
    except (AttributeError, ValueError):
        stderr = ""
    if stderr and stderr not in chunks[0]:
        chunks.append(stderr)
    return "\n".join(chunks)


def load_fixture_meta(fixture_dir: Path) -> dict[str, Any]:
    import yaml

    meta_path = fixture_dir / "meta.yaml"
    data = yaml.safe_load(meta_path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), f"meta.yaml must be a mapping: {meta_path}"
    return data


def iter_fixture_dirs(fixtures_dir: Path) -> list[Path]:
    dirs = sorted(path.parent for path in fixtures_dir.rglob("input.*") if path.is_file())
    return dirs
