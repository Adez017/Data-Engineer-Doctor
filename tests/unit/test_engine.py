"""Unit tests for the deterministic rule engine (§9 steps 4-5)."""

from __future__ import annotations

import re
from pathlib import Path

from dedoc.diagnosis.engine import match_rules, resolve_platform
from dedoc.diagnosis.loader import load_diagnoses
from dedoc.evidence import score_match
from dedoc.evidence.models import ConfidenceBand, EvidenceType
from dedoc.models.diagnosis import Diagnosis
from dedoc.parser.input_parser import parse_input


def _diagnoses() -> dict[str, Diagnosis]:
    return load_diagnoses()


def _text(events: list[object]) -> str:
    return "\n".join(str(getattr(e, "raw_payload", "")) for e in events)


def test_positive_resolved_column(fixtures_dir: Path) -> None:
    fixture = fixtures_dir / "positive" / "spark-schema-mismatch-resolved-column" / "input.log"
    events = parse_input(fixture)
    text = _text(events)
    platform = resolve_platform(events, text)  # type: ignore[arg-type]
    assert platform == "spark"
    rules = match_rules(events, _diagnoses(), platform)  # type: ignore[arg-type]
    assert [r.diagnosis.id for r in rules] == ["DEDOC-SCHEMA-001"]
    rule = rules[0]
    assert "AnalysisException" in rule.matched_exception_types
    assert "resolved_column_not_found" in rule.matched_signals
    assert rule.exact_signals == ["resolved_column_not_found"]
    assert rule.platform_match
    assert rule.signal_excerpt is not None
    assert re.match(r"line \d+: ", rule.signal_excerpt)
    assert "RESOLVED_COLUMN_NOT_FOUND" in rule.signal_excerpt

    bundle = score_match(rule)
    assert bundle.confidence_band is ConfidenceBand.HIGH
    types = {item.type for item in bundle.evidence}
    assert EvidenceType.ERROR_SIGNATURE in types
    assert EvidenceType.PLATFORM_MATCH in types
    assert EvidenceType.STACKTRACE in types


def test_positive_datatype_mismatch(fixtures_dir: Path) -> None:
    fixture = fixtures_dir / "positive" / "spark-schema-mismatch-datatype" / "input.log"
    events = parse_input(fixture)
    text = _text(events)
    rules = match_rules(events, _diagnoses(), resolve_platform(events, text))  # type: ignore[arg-type]
    assert [r.diagnosis.id for r in rules] == ["DEDOC-SCHEMA-002"]
    assert "datatype_mismatch" in rules[0].matched_signals
    assert score_match(rules[0]).confidence_band in (ConfidenceBand.HIGH, ConfidenceBand.MEDIUM)


def test_table_not_found_matches_delta(fixtures_dir: Path) -> None:
    """Table-not-found shares AnalysisException with schema errors but maps to DEDOC-DELTA-003."""
    fixture = fixtures_dir / "positive" / "delta-table-not-found" / "input.log"
    events = parse_input(fixture)
    text = _text(events)
    rules = match_rules(events, _diagnoses(), resolve_platform(events, text))  # type: ignore[arg-type]
    assert [r.diagnosis.id for r in rules] == ["DEDOC-DELTA-003"]
    assert "schema" not in {r.diagnosis.category for r in rules}


def test_negative_unrelated_error(fixtures_dir: Path) -> None:
    fixture = fixtures_dir / "negative" / "unrelated-python-error" / "input.log"
    events = parse_input(fixture)
    text = _text(events)
    rules = match_rules(events, _diagnoses(), resolve_platform(events, text))  # type: ignore[arg-type]
    assert rules == []


def test_platform_gating(fixtures_dir: Path) -> None:
    fixture = fixtures_dir / "positive" / "spark-schema-mismatch-resolved-column" / "input.log"
    events = parse_input(fixture)
    rules = match_rules(events, _diagnoses(), "airflow")  # type: ignore[arg-type]
    assert rules == []


def test_platform_from_event_fields(fixtures_dir: Path) -> None:
    fixture = fixtures_dir / "positive" / "spark-schema-mismatch-resolved-column" / "input.log"
    events = parse_input(fixture)
    for event in events:
        event.raw_payload = ""
        event.error_message = "boom"
        event.stacktrace = None
        event.platform = "unknown"
    text = "something with no platform markers"
    assert resolve_platform(events, text) == "unknown"  # type: ignore[arg-type]
    events[0].platform = "databricks"  # type: ignore[index]
    assert resolve_platform(events, text) == "databricks"  # type: ignore[arg-type]


def test_bare_exception_without_signal_does_not_match(fixtures_dir: Path, tmp_path: Path) -> None:
    """Precision rule: declared signals are required when a diagnosis declares them."""
    log = tmp_path / "ambiguous.log"
    log.write_text(
        "org.apache.spark.sql.AnalysisException: Ambiguous reference to slot 'x'\n"
        "    at org.apache.spark.sql.catalyst.analysis.Analyzer.check(Analyzer.scala:1)\n",
        encoding="utf-8",
    )
    events = parse_input(log)
    text = _text(events)
    rules = match_rules(events, _diagnoses(), resolve_platform(events, text))  # type: ignore[arg-type]
    assert rules == []


def test_negative_signal_disqualifies(fixtures_dir: Path, tmp_path: Path) -> None:
    """A log with a diagnosis-positive AND its negative signal must not match that diagnosis."""
    log = tmp_path / "conflicted.log"
    log.write_text(
        "pyspark.sql.utils.AnalysisException: [RESOLVED_COLUMN_NOT_FOUND] "
        "Column 'a' cannot be resolved.\n"
        "Also: Table or view 't' not found\n",
        encoding="utf-8",
    )
    events = parse_input(log)
    text = _text(events)
    rules = match_rules(events, _diagnoses(), resolve_platform(events, text))  # type: ignore[arg-type]
    matched_ids = {r.diagnosis.id for r in rules}
    assert "DEDOC-SCHEMA-001" not in matched_ids  # disqualified by table_or_view_not_found negative
    assert "DEDOC-DELTA-003" in matched_ids  # table-not-found still matches its own diagnosis


def test_excerpt_includes_surrounding_context() -> None:
    """Evidence excerpts show the matched line plus one line of context each side."""
    from dedoc.models.failure import FailureEvent

    event = FailureEvent(
        source="log",
        raw_payload=(
            "line one of context\n"
            "AnalysisException: Column 'b' cannot be resolved [RESOLVED_COLUMN_NOT_FOUND]\n"
            "line three of context\n"
        ),
    )
    rules = match_rules([event], _diagnoses(), "unknown")
    matched = [rule for rule in rules if rule.diagnosis.id == "DEDOC-SCHEMA-001"]
    assert matched
    excerpt = matched[0].signal_excerpt
    assert excerpt is not None
    assert "line 1: line one of context" in excerpt
    assert "line 2: AnalysisException" in excerpt
    assert "line 3: line three of context" in excerpt


def test_exception_excerpt_skips_stack_frames_when_picking_target() -> None:
    """The excerpt target is the exception message line, not the first `at ...` frame."""
    from dedoc.models.failure import FailureEvent

    event = FailureEvent(
        source="log",
        raw_payload=(
            "    at org.apache.spark.sql.catalyst.analysis.Analyzer.check(Analyzer.scala:1)\n"
            "    at org.apache.spark.sql.catalyst.analysis.Analyzer.resolve(Analyzer.scala:2)\n"
            "org.apache.spark.sql.AnalysisException: [RESOLVED_COLUMN_NOT_FOUND] "
            "Column 'c' cannot be resolved.\n"
            "    at org.apache.spark.sql.catalyst.analysis.Analyzer.execute(Analyzer.scala:190)\n"
        ),
    )
    rules = match_rules([event], _diagnoses(), "unknown")
    matched = [rule for rule in rules if rule.diagnosis.id == "DEDOC-SCHEMA-001"]
    assert matched
    excerpt = matched[0].exception_excerpt
    assert excerpt is not None
    assert "line 3: org.apache.spark.sql.AnalysisException" in excerpt
    assert not excerpt.startswith("line 1:")
