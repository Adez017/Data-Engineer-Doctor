"""Unit tests for the bounded investigation agent (§11): abstention, hard
limits, contradiction detection, corroboration, and pipeline integration."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from typer.testing import CliRunner

from dedoc.agents import AgentConfig, AgentStatus, FindingKind
from dedoc.agents.orchestrator import run_investigation
from dedoc.cli.main import app
from dedoc.core.errors import AgentConfigError
from dedoc.diagnosis.loader import load_diagnoses
from dedoc.models.diagnosis import Diagnosis
from dedoc.tools import InvestigationContext
from tests.conftest import all_output


def _target(diagnosis_id: str) -> Diagnosis:
    return load_diagnoses()[diagnosis_id]


def _rich_spark_context() -> InvestigationContext:
    return InvestigationContext(
        current_run={"run_id": "run-latest", "status": "failed", "stage": "stage-7"},
        previous_runs=[
            {"run_id": "run-prev", "status": "succeeded"},
            {"run_id": "run-old", "status": "succeeded"},
        ],
        query_plan="Exchange LogSink: output row count 1200",
        metrics={
            "executor.memory.used": {
                "name": "executor.memory.used",
                "value": 0.9,
                "labels": {"executor": "exec5"},
            },
            "stage.duration": {
                "name": "stage.duration",
                "value": 300.0,
                "labels": {"stage": "stage-7"},
            },
        },
    )


def test_invalid_configuration_rejected() -> None:
    with pytest.raises(AgentConfigError):
        AgentConfig(max_iterations=0)
    with pytest.raises(AgentConfigError):
        AgentConfig(timeout_seconds=0)


def test_empty_context_abstains() -> None:
    record = run_investigation(_target("DEDOC-SPARK-001"), InvestigationContext())
    assert record.status is AgentStatus.INSUFFICIENT_CONTEXT
    assert record.tool_calls == 0
    assert record.iterations == 0


def test_missing_target_abstains() -> None:
    record = run_investigation(None, _rich_spark_context())
    assert record.status is AgentStatus.INSUFFICIENT_CONTEXT


def test_iteration_budget_enforced() -> None:
    record = run_investigation(
        _target("DEDOC-SPARK-001"),
        _rich_spark_context(),
        config=AgentConfig(max_iterations=2, max_tool_calls=50, timeout_seconds=30),
    )
    assert record.status is AgentStatus.LIMIT_REACHED
    assert record.iterations == 2
    assert record.tool_calls == 2


def test_tool_call_budget_enforced() -> None:
    record = run_investigation(
        _target("DEDOC-SPARK-001"),
        _rich_spark_context(),
        config=AgentConfig(max_iterations=50, max_tool_calls=1, timeout_seconds=30),
    )
    assert record.status is AgentStatus.LIMIT_REACHED
    assert record.tool_calls == 1


def test_deadline_enforced() -> None:
    record = run_investigation(
        _target("DEDOC-SPARK-001"),
        _rich_spark_context(),
        config=AgentConfig(max_iterations=50, max_tool_calls=50, timeout_seconds=1e-9),
    )
    assert record.status is AgentStatus.LIMIT_REACHED
    assert record.iterations <= 2


def test_contradiction_challenges_top_explanation() -> None:
    context = InvestigationContext(
        query_plan="Exchange adapter: AuthenticationException while contacting S3"
    )
    record = run_investigation(
        _target("DEDOC-SPARK-001"),
        context,
        allowlist=frozenset({"inspect_query_plan"}),
    )
    assert record.status is AgentStatus.SUCCESS
    assert len(record.contradictions) == 1
    assert "authentication_failure" in record.contradictions[0].description
    assert record.reason.startswith("investigation found evidence contradicting")
    assert record.tool_calls == 1


def test_corroborating_signal_classified_as_supporting() -> None:
    context = InvestigationContext(
        query_plan="Exchange reduce: Missing an output location for shuffle"
    )
    record = run_investigation(
        _target("DEDOC-SPARK-006"),
        context,
        allowlist=frozenset({"inspect_query_plan"}),
    )
    assert record.status is AgentStatus.SUCCESS
    assert not record.contradictions
    assert len(record.findings) == 1
    assert record.findings[0].kind is FindingKind.SUPPORTING
    assert "shuffle_fetch_failed" in record.findings[0].description


def test_pipeline_attaches_investigation(fixtures_dir: Path) -> None:
    from dedoc.core.pipeline import diagnose_file
    from dedoc.models.report import DiagnosisReport

    fixture = fixtures_dir / "positive" / "spark-executor-oom" / "input.log"
    report = diagnose_file(
        fixture,
        investigate=True,
        context=InvestigationContext(
            log_lines=[
                "WARN Adding partitioning column for full scan",
            ]
        ),
    )
    assert isinstance(report, DiagnosisReport)
    assert report.investigation is not None
    assert report.investigation.tool_calls >= 1


def test_cli_investigate_flag(tmp_path: Path, fixtures_dir: Path, cli: CliRunner) -> None:
    log = tmp_path / "input.log"
    shutil.copy(fixtures_dir / "positive" / "spark-executor-oom" / "input.log", log)
    context_file = tmp_path / "context.yaml"
    context_file.write_text(
        'query_plan: "Exchange LogSink: output row count 1200"\n',
        encoding="utf-8",
    )
    result = cli.invoke(
        app,
        ["diagnose", str(log), "--investigate", "--context", str(context_file), "--format", "text"],
    )
    assert result.exit_code == 0, all_output(result)
    output = all_output(result)
    assert "Investigation:" in output
    assert "Tool calls:" in output
