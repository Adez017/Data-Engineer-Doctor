"""The MVP investigation toolkit: 12 read-only tools (BUILD_PLAN.md §12).

Each tool consumes only ``InvestigationContext`` data it is given, redacts any
log-derived text it returns, and reports ``unavailable`` instead of guessing when
the required data is absent. No tool performs writes or network calls.
"""

from __future__ import annotations

from typing import Any

from dedoc.core.redaction import redact

from .base import Param, ParamKind, Tool, ToolResult, ToolStatus
from .context import InvestigationContext


def _numbered_lines(context: InvestigationContext) -> list[tuple[int, str]]:
    """Combine context log lines and the failure text into numbered lines."""
    lines = list(context.log_lines)
    if context.text:
        lines.extend(context.text.splitlines())
    return [(number, line) for number, line in enumerate(lines, start=1) if line.strip()]


def _dump_knowledge(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": entry["id"],
        "name": entry["name"],
        "category": entry["category"],
        "severity": entry["severity"],
        "platforms": entry["platforms"],
        "hypotheses": entry["hypotheses"],
    }


def get_logs(context: InvestigationContext, params: dict[str, Any]) -> ToolResult:
    lines = _numbered_lines(context)
    if not lines:
        return ToolResult(
            status=ToolStatus.UNAVAILABLE,
            summary="no log lines available in the supplied context",
        )
    limit = int(params.get("limit") or len(lines))
    selected = lines[: max(limit, 0)]
    detail = "\n".join(f"{number}: {redact(line)}" for number, line in selected)
    return ToolResult(
        status=ToolStatus.SUCCESS,
        summary=f"returned {len(selected)} log line(s)",
        detail=detail,
        data={"lines": [line for _, line in selected]},
    )


def search_logs(context: InvestigationContext, params: dict[str, Any]) -> ToolResult:
    query = str(params.get("query") or "").strip()
    if not query:
        return ToolResult(
            status=ToolStatus.ERROR,
            summary="search_logs requires a non-empty 'query' parameter",
        )
    lines = _numbered_lines(context)
    if not lines:
        return ToolResult(
            status=ToolStatus.UNAVAILABLE,
            summary="no log lines available in the supplied context",
        )
    lowered = query.lower()
    matches = [(n, line) for n, line in lines if lowered in line.lower()]
    limit = int(params.get("limit") or len(matches))
    selected = matches[: max(limit, 0)]
    detail = "\n".join(f"{number}: {redact(line)}" for number, line in selected)
    return ToolResult(
        status=ToolStatus.SUCCESS,
        summary=f"{len(selected)}/{len(matches)} line(s) matched '{query}'",
        detail=detail,
        data={"matches": len(matches), "numbers": [n for n, _ in selected]},
    )


def _run_payload(run: Any) -> dict[str, Any]:
    return {
        "run_id": run.run_id,
        "status": run.status,
        "job": run.job,
        "stage": run.stage,
        "error": redact(run.error) if run.error else None,
    }


def get_pipeline_run(context: InvestigationContext, params: dict[str, Any]) -> ToolResult:
    run_id = str(params.get("run_id") or "").strip()
    run = context.current_run
    if run_id:
        run = next(
            (item for item in context.previous_runs if item.run_id == run_id),
            None,
        )
        if run is None and context.current_run and context.current_run.run_id == run_id:
            run = context.current_run
    if run is None:
        return ToolResult(
            status=ToolStatus.UNAVAILABLE,
            summary="no pipeline run available in the supplied context",
        )
    return ToolResult(
        status=ToolStatus.SUCCESS,
        summary=f"pipeline run {run.run_id} status={run.status}",
        detail=redact(f"run_id={run.run_id}\nstatus={run.status}")
        + (f"\nerror={redact(run.error)}" if run.error else ""),
        data={"run": _run_payload(run)},
    )


def get_previous_runs(context: InvestigationContext, params: dict[str, Any]) -> ToolResult:
    if not context.previous_runs:
        return ToolResult(
            status=ToolStatus.UNAVAILABLE,
            summary="no previous runs available in the supplied context",
        )
    limit = int(params.get("limit") or len(context.previous_runs))
    selected = context.previous_runs[: max(limit, 0)]
    runs = [_run_payload(item) for item in selected]
    return ToolResult(
        status=ToolStatus.SUCCESS,
        summary=f"returned {len(selected)} previous run(s)",
        detail="\n".join(
            f"{item.run_id} status={item.status}"
            + (f" error={redact(item.error)}" if item.error else "")
            for item in selected
        ),
        data={"runs": runs},
    )


def compare_runs(context: InvestigationContext, params: dict[str, Any]) -> ToolResult:
    base_id = str(params.get("base") or "").strip()
    other_id = str(params.get("other") or "").strip()
    base: Any = context.current_run
    other: Any = None
    if base_id:
        base = next(
            (item for item in context.previous_runs if item.run_id == base_id),
            None,
        )
    if other_id:
        other = next(
            (item for item in context.previous_runs if item.run_id == other_id),
            None,
        )
    elif context.previous_runs:
        other = context.previous_runs[0]
    if base is None or other is None:
        return ToolResult(
            status=ToolStatus.UNAVAILABLE,
            summary="compare_runs needs two runs (current + a previous run) in the context",
        )
    differences: dict[str, Any] = {
        "base_run": base.run_id,
        "other_run": other.run_id,
        "status": {"base": base.status, "other": other.status},
        "stage": {"base": base.stage, "other": other.stage},
    }
    detail = redact(
        f"compare base={base.run_id} (other={other.run_id})\n"
        f"status: {base.status} -> {other.status}"
    )
    return ToolResult(
        status=ToolStatus.SUCCESS,
        summary=f"compared {base.run_id} with {other.run_id}",
        detail=detail,
        data={"differences": differences},
    )


def get_schema(context: InvestigationContext, params: dict[str, Any]) -> ToolResult:
    table = str(params.get("table") or "").strip()
    if table:
        snapshot = context.schemas.get(table)
    else:
        snapshot = next(iter(context.schemas.values()), None)
    if snapshot is None:
        return ToolResult(
            status=ToolStatus.UNAVAILABLE,
            summary="no schema snapshot available in the supplied context",
        )
    return ToolResult(
        status=ToolStatus.SUCCESS,
        summary=f"schema for {snapshot.table}: {len(snapshot.columns)} column(s)",
        detail="\n".join(snapshot.columns),
        data={
            "table": snapshot.table,
            "columns": list(snapshot.columns),
            "data_types": dict(snapshot.data_types),
        },
    )


def compare_schema(context: InvestigationContext, params: dict[str, Any]) -> ToolResult:
    first = str(params.get("table1") or "").strip()
    second = str(params.get("table2") or "").strip()
    tables = list(context.schemas)
    if first or second:
        snap_a = context.schemas.get(first or "")
        snap_b = context.schemas.get(second or "")
    elif len(tables) >= 2:
        snap_a, snap_b = context.schemas[tables[0]], context.schemas[tables[1]]
    else:
        snap_a = snap_b = None
    if snap_a is None or snap_b is None:
        return ToolResult(
            status=ToolStatus.UNAVAILABLE,
            summary="compare_schema needs two schema snapshots in the context",
        )
    cols_a, cols_b = set(snap_a.columns), set(snap_b.columns)
    added = sorted(cols_b - cols_a)
    removed = sorted(cols_a - cols_b)
    common = cols_a & cols_b
    changed_types = {
        col: (snap_a.data_types.get(col), snap_b.data_types.get(col))
        for col in common
        if snap_a.data_types.get(col) != snap_b.data_types.get(col)
    }
    detail = "\n".join(
        [
            f"added: {', '.join(added) or 'none'}",
            f"removed: {', '.join(removed) or 'none'}",
        ]
    )
    return ToolResult(
        status=ToolStatus.SUCCESS,
        summary=f"compared schemas {snap_a.table} vs {snap_b.table}",
        detail=detail,
        data={
            "table1": snap_a.table,
            "table2": snap_b.table,
            "added": added,
            "removed": removed,
            "changed_types": {
                col: {"from": tuple_, "to": tuple_[1]} for col, tuple_ in changed_types.items()
            },
        },
    )


def _metric_line(sample: Any) -> str:
    return (
        f"{sample.name}={sample.value}"
        + (f" {sample.unit}" if sample.unit else "")
        + (f" [{sample.window}]" if sample.window else "")
    )


def get_metrics(context: InvestigationContext, params: dict[str, Any]) -> ToolResult:
    raw = str(params.get("names") or "").strip()
    wanted = {token.strip() for token in raw.split(",") if token.strip()}
    if wanted:
        samples = [s for name, s in context.metrics.items() if name in wanted]
    else:
        samples = list(context.metrics.values())
    if not samples:
        return ToolResult(
            status=ToolStatus.UNAVAILABLE,
            summary="no metrics available in the supplied context",
        )
    return ToolResult(
        status=ToolStatus.SUCCESS,
        summary=f"returned {len(samples)} metric sample(s)",
        detail="\n".join(_metric_line(sample) for sample in samples),
        data={"metrics": [{**sample.model_dump(), "name": sample.name} for sample in samples]},
    )


def _filtered_metrics(context: InvestigationContext, label: str, expected: str | None) -> list[Any]:
    samples = list(context.metrics.values())
    if not expected:
        return samples
    return [sample for sample in samples if sample.labels.get(label) == expected]


def get_stage_metrics(context: InvestigationContext, params: dict[str, Any]) -> ToolResult:
    stage = (
        str(params.get("stage") or "").strip()
        or (context.current_run.stage if context.current_run else None)
        or ""
    )
    samples = _filtered_metrics(context, "stage", stage or None)
    if not samples:
        return ToolResult(
            status=ToolStatus.UNAVAILABLE,
            summary="no stage-scoped metrics available in the supplied context",
        )
    return ToolResult(
        status=ToolStatus.SUCCESS,
        summary=f"returned {len(samples)} metric(s) for stage={stage or 'any'}",
        detail="\n".join(_metric_line(sample) for sample in samples),
        data={"metrics": [sample.name for sample in samples]},
    )


def get_executor_metrics(context: InvestigationContext, params: dict[str, Any]) -> ToolResult:
    executor_id = str(params.get("executor_id") or "").strip() or None
    samples = []
    for sample in context.metrics.values():
        value = sample.labels.get("executor") or sample.labels.get("executor_id")
        if executor_id is None or value == executor_id:
            samples.append(sample)
    if not samples:
        return ToolResult(
            status=ToolStatus.UNAVAILABLE,
            summary="no executor-scoped metrics available in the supplied context",
        )
    return ToolResult(
        status=ToolStatus.SUCCESS,
        summary=f"returned {len(samples)} executor metric(s)",
        detail="\n".join(_metric_line(sample) for sample in samples),
        data={"metrics": [sample.name for sample in samples]},
    )


def inspect_query_plan(context: InvestigationContext, params: dict[str, Any]) -> ToolResult:
    del params
    plan = context.query_plan
    if not plan:
        return ToolResult(
            status=ToolStatus.UNAVAILABLE,
            summary="no query plan available in the supplied context",
        )
    clamped = redact(plan)[:2000]
    return ToolResult(
        status=ToolStatus.SUCCESS,
        summary=f"inspected query plan ({len(plan)} characters)",
        detail=clamped,
        data={"plan_preview": clamped},
    )


def search_knowledge_base(context: InvestigationContext, params: dict[str, Any]) -> ToolResult:
    del context
    query = str(params.get("query") or "").strip().lower()
    from dedoc.diagnosis.loader import load_diagnoses

    diagnoses = list(load_diagnoses().values())
    if not diagnoses:
        return ToolResult(
            status=ToolStatus.UNAVAILABLE,
            summary="no diagnosis knowledge base available",
        )
    if query:
        matches = [
            diagnosis
            for diagnosis in diagnoses
            if query in diagnosis.id.lower()
            or query in diagnosis.category.lower()
            or query in diagnosis.name.lower()
        ]
    else:
        matches = diagnoses
    results = [
        _dump_knowledge(
            {
                "id": d.id,
                "name": d.name,
                "category": d.category,
                "severity": d.severity.default.value,
                "platforms": list(d.platforms),
                "hypotheses": list(d.hypotheses),
            }
        )
        for d in matches[:10]
    ]
    return ToolResult(
        status=ToolStatus.SUCCESS,
        summary=f"{len(results)} knowledge base entrie(s) matched '{query}'",
        detail="\n".join(
            f"{entry['id']} {entry['name']} [{entry['category']}]" for entry in results
        ),
        data={"entries": results},
    )


def build_library() -> tuple[Tool, ...]:
    """Construct the ordered MVP toolkit (12 tools)."""
    tools = [
        Tool(
            name="get_logs",
            description="Return the first N redacted log lines from the supplied context.",
            params=(Param("limit", ParamKind.INT, "Maximum number of lines to return."),),
            output_schema="ToolResult.data.lines: list[str] of redacted lines",
            impl=get_logs,
        ),
        Tool(
            name="search_logs",
            description="Search supplied log lines for a keyword and return redacted matches.",
            params=(
                Param(
                    "query",
                    ParamKind.STR,
                    "Keyword (case-insensitive) to search for.",
                    required=True,
                ),
                Param("limit", ParamKind.INT, "Maximum number of matching lines to return."),
            ),
            output_schema="ToolResult.data: {matches: int, numbers: list[int]}",
            impl=search_logs,
        ),
        Tool(
            name="get_pipeline_run",
            description="Inspect the current (or a named) pipeline run summary.",
            params=(
                Param("run_id", ParamKind.STR, "Optional run id; defaults to the current run."),
            ),
            output_schema="ToolResult.data.run: {run_id, status, job, stage, error}",
            impl=get_pipeline_run,
        ),
        Tool(
            name="get_previous_runs",
            description="List recent pipeline runs available in the context.",
            params=(Param("limit", ParamKind.INT, "Maximum number of runs to return."),),
            output_schema="ToolResult.data.runs: list of run summaries",
            impl=get_previous_runs,
        ),
        Tool(
            name="compare_runs",
            description="Compare the current run against a previous run.",
            params=(
                Param("base", ParamKind.STR, "Optional base run id (defaults to current run)."),
                Param(
                    "other", ParamKind.STR, "Optional other run id (defaults to latest previous)."
                ),
            ),
            output_schema="ToolResult.data.differences: {status, stage, ...}",
            impl=compare_runs,
        ),
        Tool(
            name="get_schema",
            description="Return a schema snapshot (columns) for a table.",
            params=(
                Param(
                    "table", ParamKind.STR, "Optional table name; defaults to the first snapshot."
                ),
            ),
            output_schema="ToolResult.data: {table, columns, data_types}",
            impl=get_schema,
        ),
        Tool(
            name="compare_schema",
            description="Diff two schema snapshots (added/removed columns, type changes).",
            params=(
                Param("table1", ParamKind.STR, "Optional first table."),
                Param("table2", ParamKind.STR, "Optional second table."),
            ),
            output_schema="ToolResult.data: {table1, table2, added, removed, changed_types}",
            impl=compare_schema,
        ),
        Tool(
            name="get_metrics",
            description="Return metric samples, optionally filtered by comma-separated names.",
            params=(Param("names", ParamKind.STR, "Comma-separated metric names to select."),),
            output_schema="ToolResult.data.metrics: list of metric samples",
            impl=get_metrics,
        ),
        Tool(
            name="get_stage_metrics",
            description="Return metric samples scoped to a stage.",
            params=(
                Param("stage", ParamKind.STR, "Optional stage; defaults to the current run stage."),
            ),
            output_schema="ToolResult.data.metrics: list[str]",
            impl=get_stage_metrics,
        ),
        Tool(
            name="get_executor_metrics",
            description="Return metric samples scoped to an executor.",
            params=(Param("executor_id", ParamKind.STR, "Optional executor id."),),
            output_schema="ToolResult.data.metrics: list[str]",
            impl=get_executor_metrics,
        ),
        Tool(
            name="inspect_query_plan",
            description="Return the redacted physical/catalyst query plan preview.",
            params=(),
            output_schema="ToolResult.data.plan_preview: str",
            impl=inspect_query_plan,
        ),
        Tool(
            name="search_knowledge_base",
            description="Search the bundled diagnosis knowledge base (id/category/name).",
            params=(
                Param(
                    "query", ParamKind.STR, "Optional keyword; returns all entries when omitted."
                ),
            ),
            output_schema="ToolResult.data.entries: list of diagnosis summaries",
            impl=search_knowledge_base,
        ),
    ]
    return tuple(tools)


__all__ = ["build_library"]
