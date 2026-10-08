"""Regression: known failures must keep producing the expected diagnosis (§20)."""

from __future__ import annotations

from pathlib import Path

from dedoc.core.pipeline import diagnose_file
from dedoc.models.report import ReportStatus
from tests.conftest import iter_fixture_dirs, load_fixture_meta


def test_positive_fixtures_remain_diagnosed(fixtures_dir: Path) -> None:
    problems: list[str] = []
    positive = fixtures_dir / "positive"
    for fixture_dir in iter_fixture_dirs(positive):
        meta = load_fixture_meta(fixture_dir)
        input_file = next(fixture_dir.glob("input.*"))
        report = diagnose_file(input_file)
        label = str(fixture_dir.relative_to(fixtures_dir))
        if report.status is not ReportStatus.DIAGNOSED:
            problems.append(f"{label}: status {report.status.value}, expected diagnosed")
        matched_ids = [m.id for m in report.matches]
        if matched_ids != meta["expected"]["diagnosis_ids"]:
            problems.append(
                f"{label}: matches {matched_ids} != {meta['expected']['diagnosis_ids']}"
            )
    assert not problems, "\n".join(problems)


def test_negative_fixtures_never_diagnosed(fixtures_dir: Path) -> None:
    problems: list[str] = []
    negative = fixtures_dir / "negative"
    for fixture_dir in iter_fixture_dirs(negative):
        input_file = next(fixture_dir.glob("input.*"))
        report = diagnose_file(input_file)
        label = str(fixture_dir.relative_to(fixtures_dir))
        if report.status is not ReportStatus.INSUFFICIENT_EVIDENCE:
            problems.append(
                f"{label}: status {report.status.value}, expected insufficient_evidence"
            )
        if report.matches:
            problems.append(f"{label}: unexpected matches {[m.id for m in report.matches]}")
    assert not problems, "\n".join(problems)


def test_diagnosis_ids_are_stable(fixtures_dir: Path) -> None:
    """Public diagnosis IDs are a stable API (BUILD_PLAN.md §5)."""
    from dedoc.diagnosis.loader import load_diagnoses

    diagnoses = load_diagnoses()
    assert "DEDOC-SCHEMA-001" in diagnoses
    assert diagnoses["DEDOC-SCHEMA-001"].name == "Spark Schema Mismatch"
