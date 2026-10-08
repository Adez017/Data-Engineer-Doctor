"""End-to-end CLI integration tests (milestone M1: diagnose works, JSON is valid)."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from dedoc.cli.main import app
from tests.conftest import all_output, iter_fixture_dirs, load_fixture_meta


def test_version(cli: CliRunner) -> None:
    result = cli.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "dedoc" in result.output


def test_help(cli: CliRunner) -> None:
    result = cli.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "diagnose" in result.output


def test_diagnose_missing_file(cli: CliRunner, tmp_path: Path) -> None:
    result = cli.invoke(app, ["diagnose", str(tmp_path / "nope.log")])
    assert result.exit_code == 1
    combined = all_output(result)
    assert "error:" in combined
    assert "Traceback" not in combined


def test_all_fixtures_via_cli(cli: CliRunner, fixtures_dir: Path) -> None:
    problems: list[str] = []
    for fixture_dir in iter_fixture_dirs(fixtures_dir):
        meta = load_fixture_meta(fixture_dir)
        expected = meta["expected"]
        input_file = next(fixture_dir.glob("input.*"))
        result = cli.invoke(
            app,
            ["diagnose", str(input_file), "--format", "json"],
        )
        label = str(fixture_dir.relative_to(fixtures_dir))
        if result.exit_code != expected["exit_code"]:
            problems.append(
                f"{label}: exit {result.exit_code}, expected {expected['exit_code']}; "
                f"output: {all_output(result)!r}"
            )
            continue
        if expected["exit_code"] == 1:
            combined = all_output(result)
            if "error:" not in combined or "Traceback" in combined:
                problems.append(f"{label}: expected clean error without traceback")
            continue
        try:
            payload = json.loads(result.output)
        except json.JSONDecodeError as exc:
            problems.append(f"{label}: stdout is not valid JSON: {exc}")
            continue
        if payload["status"] != expected["status"]:
            problems.append(f"{label}: status {payload['status']} != {expected['status']}")
        matched_ids = [m["id"] for m in payload["matches"]]
        if matched_ids != expected["diagnosis_ids"]:
            problems.append(f"{label}: matches {matched_ids} != {expected['diagnosis_ids']}")
    assert not problems, "\n".join(problems)


def test_markdown_output(cli: CliRunner, fixtures_dir: Path) -> None:
    input_file = fixtures_dir / "positive" / "spark-schema-mismatch-resolved-column" / "input.log"
    result = cli.invoke(app, ["diagnose", str(input_file), "--format", "markdown"])
    assert result.exit_code == 0
    assert "# Data Engineer Doctor Report" in result.output
    assert "DEDOC-SCHEMA-001" in result.output


def test_text_output(cli: CliRunner, fixtures_dir: Path) -> None:
    input_file = fixtures_dir / "negative" / "table-not-found" / "input.log"
    result = cli.invoke(app, ["diagnose", str(input_file)])
    assert result.exit_code == 0
    assert "insufficient_evidence" in result.output


def test_custom_diagnoses_path(cli: CliRunner, fixtures_dir: Path, tmp_path: Path) -> None:
    empty = tmp_path / "empty-diagnoses"
    empty.mkdir()
    input_file = fixtures_dir / "negative" / "table-not-found" / "input.log"
    result = cli.invoke(
        app,
        ["diagnose", str(input_file), "--diagnoses-path", str(empty), "--format", "json"],
    )
    assert result.exit_code == 1
    assert "no diagnosis YAML files" in all_output(result)
