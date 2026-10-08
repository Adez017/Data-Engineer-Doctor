"""Unit tests for report formatters."""

from __future__ import annotations

import json
from pathlib import Path

from dedoc.core.pipeline import diagnose_file
from dedoc.formatters import format_json, format_markdown, format_text, render
from dedoc.models.report import DiagnosisReport, ReportStatus


def test_json_round_trip(fixtures_dir: Path) -> None:
    fixture = fixtures_dir / "positive" / "spark-schema-mismatch-resolved-column" / "input.log"
    report = diagnose_file(fixture)
    parsed = json.loads(format_json(report))
    assert parsed["status"] == "diagnosed"
    assert parsed["matches"][0]["id"] == "DEDOC-SCHEMA-001"
    DiagnosisReport.model_validate(parsed)


def test_markdown_contains_diagnosis(fixtures_dir: Path) -> None:
    fixture = fixtures_dir / "positive" / "spark-schema-mismatch-resolved-column" / "input.log"
    markdown = format_markdown(diagnose_file(fixture))
    assert "# Data Engineer Doctor Report" in markdown
    assert "DEDOC-SCHEMA-001" in markdown
    assert "Matched signals" in markdown
    assert "References" in markdown


def test_text_contains_diagnosis(fixtures_dir: Path) -> None:
    fixture = fixtures_dir / "positive" / "spark-schema-mismatch-resolved-column" / "input.log"
    text = format_text(diagnose_file(fixture))
    assert "Data Engineer Doctor" in text
    assert "DEDOC-SCHEMA-001" in text


def test_abstention_output(fixtures_dir: Path) -> None:
    fixture = fixtures_dir / "negative" / "unrelated-python-error" / "input.log"
    report = diagnose_file(fixture)
    assert report.status is ReportStatus.INSUFFICIENT_EVIDENCE
    assert report.matches == []
    for rendered in (format_json(report), format_markdown(report), format_text(report)):
        assert "insufficient_evidence" in rendered
        assert "insufficient evidence" in rendered.lower()


def test_render_dispatch() -> None:
    fixture_report = DiagnosisReport(
        dedoc_version="0.1.0",
        input_source="x.log",
        platform="unknown",
        status=ReportStatus.INSUFFICIENT_EVIDENCE,
        event_count=0,
        message="No diagnosis matched the available evidence.",
    )
    assert render(fixture_report, "json").startswith("{")
    assert render(fixture_report, "markdown").startswith("#")
    assert render(fixture_report, "text").startswith("Data Engineer Doctor")
