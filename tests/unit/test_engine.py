"""Unit tests for the deterministic rule engine (§9 steps 4-5)."""

from __future__ import annotations

from pathlib import Path

from dedoc.diagnosis.engine import match_diagnoses, resolve_platform
from dedoc.diagnosis.loader import load_diagnoses
from dedoc.models.diagnosis import Diagnosis
from dedoc.parser.input_parser import parse_input


def _diagnoses() -> dict[str, Diagnosis]:
    return load_diagnoses()


def _events(fixture: Path):
    return parse_input(fixture)


def test_positive_resolved_column(fixtures_dir: Path) -> None:
    fixture = fixtures_dir / "positive" / "spark-schema-mismatch-resolved-column" / "input.log"
    events = _events(fixture)
    text = "\n".join(str(e.raw_payload) for e in events)
    platform = resolve_platform(events, text)
    assert platform == "spark"
    matches = match_diagnoses(events, _diagnoses(), platform)
    assert [m.id for m in matches] == ["DEDOC-SCHEMA-001"]
    match = matches[0]
    assert "AnalysisException" in match.matched_exception_types
    assert "resolved_column_not_found" in match.matched_signals
    assert match.hypotheses


def test_positive_datatype_mismatch(fixtures_dir: Path) -> None:
    fixture = fixtures_dir / "positive" / "spark-schema-mismatch-datatype" / "input.log"
    events = _events(fixture)
    text = "\n".join(str(e.raw_payload) for e in events)
    matches = match_diagnoses(events, _diagnoses(), resolve_platform(events, text))
    assert [m.id for m in matches] == ["DEDOC-SCHEMA-001"]
    assert "datatype_mismatch" in matches[0].matched_signals


def test_negative_table_not_found_is_disqualified(fixtures_dir: Path) -> None:
    fixture = fixtures_dir / "negative" / "table-not-found" / "input.log"
    events = _events(fixture)
    text = "\n".join(str(e.raw_payload) for e in events)
    matches = match_diagnoses(events, _diagnoses(), resolve_platform(events, text))
    assert matches == []


def test_negative_unrelated_error(fixtures_dir: Path) -> None:
    fixture = fixtures_dir / "negative" / "unrelated-python-error" / "input.log"
    events = _events(fixture)
    text = "\n".join(str(e.raw_payload) for e in events)
    matches = match_diagnoses(events, _diagnoses(), resolve_platform(events, text))
    assert matches == []


def test_platform_gating(fixtures_dir: Path) -> None:
    fixture = fixtures_dir / "positive" / "spark-schema-mismatch-resolved-column" / "input.log"
    events = _events(fixture)
    matches = match_diagnoses(events, _diagnoses(), platform="airflow")
    assert matches == []


def test_platform_from_event_fields(fixtures_dir: Path) -> None:
    fixture = fixtures_dir / "positive" / "spark-schema-mismatch-resolved-column" / "input.log"
    events = _events(fixture)
    for event in events:
        event.raw_payload = ""
        event.error_message = "boom"
        event.stacktrace = None
        event.platform = "unknown"
    text = "something with no platform markers"
    assert resolve_platform(events, text) == "unknown"
    events[0].platform = "databricks"
    assert resolve_platform(events, text) == "databricks"
