"""Unit tests for the investigation tool layer (§12): contracts, redaction,
allowlist, timeout, and abstention."""

from __future__ import annotations

import time
from dataclasses import replace

import pytest

from dedoc.core.errors import InputError
from dedoc.tools import (
    InvestigationContext,
    MetricsSample,
    SchemaSnapshot,
    ToolResult,
    ToolStatus,
    call_tool,
    context_from_mapping,
    get_tool,
    list_tools,
)

EXPECTED_TOOLS = {
    "get_logs",
    "search_logs",
    "get_pipeline_run",
    "get_previous_runs",
    "compare_runs",
    "get_schema",
    "compare_schema",
    "get_metrics",
    "get_stage_metrics",
    "get_executor_metrics",
    "inspect_query_plan",
    "search_knowledge_base",
}


def _context(**kwargs: object) -> InvestigationContext:
    return InvestigationContext.model_validate(kwargs)


def test_toolkit_has_twelve_declared_tools() -> None:
    tools = list_tools()
    assert len(tools) == 12
    assert {tool.name for tool in tools} == EXPECTED_TOOLS
    tool = next(tool for tool in tools if tool.name == "search_logs")
    assert tool.read_only is True
    assert tool.security.value == "read_only"
    assert tool.timeout_seconds > 0
    assert tool.environments
    assert tool.output_schema
    assert any(param.name == "query" and param.required for param in tool.params)


def test_search_logs_redacts_secrets() -> None:
    context = _context(
        log_lines=["12:28:03 INFO Connecting to jdbc:postgresql://db with password=hunter2hunter2"]
    )
    result = call_tool(get_tool("search_logs"), context, {"query": "jdbc"})
    assert result.status is ToolStatus.SUCCESS
    assert "[REDACTED]" in result.detail
    assert "hunter2hunter2" not in result.detail


def test_missing_data_reports_unavailable() -> None:
    result = call_tool(get_tool("get_metrics"), _context(), {})
    assert result.status is ToolStatus.UNAVAILABLE


def test_get_pipeline_run_unavailable_without_runs() -> None:
    result = call_tool(get_tool("get_pipeline_run"), _context(), {})
    assert result.status is ToolStatus.UNAVAILABLE


def test_allowlist_denies_unlisted_tool() -> None:
    result = call_tool(
        get_tool("get_logs"),
        _context(log_lines=["one"]),
        {},
        allowlist=frozenset({"get_metrics"}),
    )
    assert result.status is ToolStatus.DENIED
    assert result.detail == ""


def test_required_param_enforced() -> None:
    result = call_tool(get_tool("search_logs"), _context(log_lines=["x"]), {})
    assert result.status is ToolStatus.ERROR
    assert "missing required parameter" in result.summary


def test_unknown_param_rejected() -> None:
    result = call_tool(get_tool("get_logs"), _context(log_lines=["x"]), {"nope": 1})
    assert result.status is ToolStatus.ERROR


def test_tool_timeout_enforced() -> None:
    def sleepy(context: InvestigationContext, params: dict[str, object]) -> ToolResult:
        del context, params
        time.sleep(2)
        return ToolResult(status=ToolStatus.SUCCESS, summary="too late")

    slow = replace(get_tool("get_metrics"), impl=sleepy, timeout_seconds=1)
    assert call_tool(slow, _context(), {}).status is ToolStatus.TIMEOUT


def test_compare_schema_reports_differences() -> None:
    context = _context(
        schemas={
            "customer_v1": SchemaSnapshot(
                table="customer_v1", columns=["id", "name"], data_types={"name": "string"}
            ),
            "customer_v2": SchemaSnapshot(
                table="customer_v2", columns=["id", "email"], data_types={"name": "string"}
            ),
        }
    )
    result = call_tool(get_tool("compare_schema"), context, {})
    assert result.status is ToolStatus.SUCCESS
    assert result.data["removed"] == ["name"]
    assert result.data["added"] == ["email"]


def test_compare_schema_unavailable_with_one_schema() -> None:
    context = _context(schemas={"t1": {"table": "t1", "columns": ["a"]}})
    result = call_tool(get_tool("compare_schema"), context, {})
    assert result.status is ToolStatus.UNAVAILABLE


def test_get_stage_metrics_filters_by_stage() -> None:
    context = _context(
        metrics={
            "stage.duration": {
                "name": "stage.duration",
                "value": 120.0,
                "labels": {"stage": "stage-7"},
            },
            "shuffle_bytes": {"name": "shuffle_bytes", "value": 9.0},
        }
    )
    result = call_tool(get_tool("get_stage_metrics"), context, {"stage": "stage-7"})
    assert result.status is ToolStatus.SUCCESS
    assert result.data["metrics"] == ["stage.duration"]


def test_metric_value_coerced_from_number() -> None:
    ctx = context_from_mapping({"metrics": {"executor.memory.used": 0.9}})
    sample = ctx.metrics["executor.memory.used"]
    assert isinstance(sample, MetricsSample)
    assert sample.value == 0.9


def test_context_from_mapping_aliases() -> None:
    ctx = context_from_mapping(
        {
            "runs": [{"run_id": "r1", "status": "failed"}],
            "logs": ["line one"],
            "schemas": {"t": {"columns": ["a"]}},
            "metrics": {"m": {"value": 1.0}},
            "query_plan": "*BroadcastHashJoin",
            "current_run": "run-current",
        }
    )
    assert ctx.current_run is not None
    assert ctx.current_run.run_id == "run-current"
    assert ctx.previous_runs[0].run_id == "r1"
    assert ctx.schemas["t"].table == "t"
    assert ctx.log_lines == ["line one"]
    assert ctx.query_plan is not None
    assert ctx.has_external_data()


def test_context_from_mapping_rejects_garbage() -> None:
    with pytest.raises(InputError):
        context_from_mapping({"schemas": {"t": "not-a-mapping"}})
