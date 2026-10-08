"""Public Python SDK surface tests (BUILD_PLAN.md §26 step 4)."""

from __future__ import annotations

from pathlib import Path

import pytest

import dedoc
from dedoc import diagnose, list_diagnoses
from dedoc.models.report import ReportStatus


def test_version_is_str() -> None:
    assert isinstance(dedoc.__version__, str)
    assert dedoc.__version__


def test_list_diagnoses_returns_all_sorted(fixtures_dir: Path) -> None:
    diagnoses = list_diagnoses()
    ids = [d.id for d in diagnoses]
    assert ids == sorted(ids)
    assert len(ids) == 33
    # every diagnosis ships its own positive fixture; the contact is enforced
    assert any(d.id == "DEDOC-PERF-004" for d in diagnoses)


def test_diagnose_returns_report(fixtures_dir: Path) -> None:
    report = diagnose(fixtures_dir / "positive" / "spark-executor-oom" / "input.log")
    assert report.status is ReportStatus.DIAGNOSED
    assert report.matches[0].id == "DEDOC-SPARK-001"
    assert report.matches[0].confidence_band.value == "HIGH"


def test_diagnose_python_api_preserves_message(fixtures_dir: Path) -> None:

    report = diagnose(fixtures_dir / "positive" / "spark-executor-oom" / "input.log")
    assert report.message.startswith("DEDOC-SPARK-001")


def test_diagnose_missing_file_raises(fixtures_dir: Path) -> None:
    from dedoc.core.errors import InputError

    with pytest.raises(InputError):
        diagnose(fixtures_dir / "positive" / "does-not-exist" / "input.log")
