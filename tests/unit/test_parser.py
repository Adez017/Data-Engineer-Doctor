"""Unit tests for input parsing (TXT / JSON / JSONL, malformed input)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from dedoc.core.errors import InputError
from dedoc.parser import input_parser
from dedoc.parser.input_parser import InputFormat, parse_input


def test_text_parsing(tmp_path: Path) -> None:
    path = tmp_path / "error.log"
    path.write_text(
        "12:00:00 ERROR Job failed\n"
        "pyspark.sql.utils.AnalysisException: boom\n"
        "\tat org.apache.spark.sql.AnalysisException.run(AnalysisException.scala:1)\n",
        encoding="utf-8",
    )
    events = parse_input(path)
    assert len(events) == 1
    event = events[0]
    assert event.error_message == "12:00:00 ERROR Job failed"
    assert event.stacktrace is not None and "at org.apache.spark" in event.stacktrace
    assert isinstance(event.raw_payload, str)
    assert event.source == str(path)


def test_empty_text_returns_no_events(tmp_path: Path) -> None:
    path = tmp_path / "empty.log"
    path.write_text("", encoding="utf-8")
    assert parse_input(path) == []


def test_json_object(tmp_path: Path) -> None:
    path = tmp_path / "event.json"
    path.write_text(
        json.dumps(
            {
                "platform": "spark",
                "errorMessage": "boom",
                "errorType": "AnalysisException",
                "resourceAttributes": {"job.name": "etl"},
                "timestamp": 1728390896,
            }
        ),
        encoding="utf-8",
    )
    (event,) = parse_input(path)
    assert event.platform == "spark"
    assert event.error_message == "boom"
    assert event.error_type == "AnalysisException"
    assert event.resource_attributes == {"job.name": "etl"}
    assert event.timestamp.year == 2024


def test_json_array(tmp_path: Path) -> None:
    path = tmp_path / "events.json"
    path.write_text(
        json.dumps([{"message": "one"}, {"message": "two"}]),
        encoding="utf-8",
    )
    events = parse_input(path)
    assert [e.error_message for e in events] == ["one", "two"]


def test_jsonl(tmp_path: Path) -> None:
    path = tmp_path / "events.jsonl"
    path.write_text('{"message": "one"}\n\n{"message": "two"}\n', encoding="utf-8")
    events = parse_input(path)
    assert [e.error_message for e in events] == ["one", "two"]


def test_jsonl_bad_line_reports_line_number(tmp_path: Path) -> None:
    path = tmp_path / "events.jsonl"
    path.write_text('{"message": "one"}\n{oops\n', encoding="utf-8")
    with pytest.raises(InputError, match="line 2"):
        parse_input(path)


def test_truncated_json(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text('{"platform": "spark"', encoding="utf-8")
    with pytest.raises(InputError, match="invalid JSON"):
        parse_input(path)


def test_json_wrong_top_level(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text('"just a string"', encoding="utf-8")
    with pytest.raises(InputError, match="expected an object"):
        parse_input(path)


def test_missing_file(tmp_path: Path) -> None:
    with pytest.raises(InputError, match="not found"):
        parse_input(tmp_path / "missing.log")


def test_directory_rejected(tmp_path: Path) -> None:
    with pytest.raises(InputError, match="not a file"):
        parse_input(tmp_path)


def test_non_utf8_is_tolerated(tmp_path: Path) -> None:
    path = tmp_path / "binary.log"
    path.write_bytes(b"\xff\xfe\x00valid text\x80")
    events = parse_input(path)
    assert len(events) == 1


def test_size_limit_enforced(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(input_parser, "MAX_INPUT_BYTES", 8)
    path = tmp_path / "big.log"
    path.write_text("x" * 100, encoding="utf-8")
    with pytest.raises(InputError, match="exceeds"):
        parse_input(path)


def test_input_format_override(tmp_path: Path) -> None:
    path = tmp_path / "misnamed.log"
    path.write_text('{"message": "one"}', encoding="utf-8")
    (event,) = parse_input(path, InputFormat.JSON)
    assert event.error_message == "one"


def test_detect_format(tmp_path: Path) -> None:
    assert input_parser.detect_format(tmp_path / "a.json") is InputFormat.JSON
    assert input_parser.detect_format(tmp_path / "a.jsonl") is InputFormat.JSONL
    assert input_parser.detect_format(tmp_path / "a.log") is InputFormat.TEXT
