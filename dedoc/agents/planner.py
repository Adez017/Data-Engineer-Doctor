"""Deterministic probe selection for the investigation agent (§11).

The planner turns the Observe -> Hypothesize step into a fixed, ordered list of
(tool, params) probes. A probe is only emitted when the target explanation
could plausibly be confirmed or refuted by the structured data already present
in the context; nothing is invented and no AI is involved.
"""

from __future__ import annotations

from dedoc.models.diagnosis import Diagnosis
from dedoc.tools.context import InvestigationContext


def target_probes(
    target: Diagnosis, context: InvestigationContext
) -> list[tuple[str, dict[str, object]]]:
    """Return the ordered, deduplicated probe plan for the target explanation."""
    category = target.category
    probes: list[tuple[str, dict[str, object]]] = []

    if context.query_plan and (category.startswith("spark") or category.startswith("performance")):
        probes.append(("inspect_query_plan", {}))

    if context.schemas and (
        category.startswith("schema")
        or category.startswith("delta")
        or category.startswith("quality")
    ):
        tables = list(context.schemas)
        if len(tables) >= 2:
            probes.append(("get_schema", {"table": tables[0]}))
            probes.append(("get_schema", {"table": tables[1]}))
            probes.append(("compare_schema", {"table1": tables[0], "table2": tables[1]}))
        elif tables:
            probes.append(("get_schema", {"table": tables[0]}))

    if context.metrics and (
        category.startswith("spark")
        or category.startswith("performance")
        or category.startswith("connectivity")
    ):
        probes.append(("get_metrics", {}))
        if "spark" in target.platforms:
            probes.append(("get_executor_metrics", {}))
        stage = context.current_run.stage if context.current_run else None
        if stage:
            probes.append(("get_stage_metrics", {"stage": stage}))

    if (context.current_run or context.previous_runs) and (
        category.startswith("spark")
        or category.startswith("delta")
        or category.startswith("connectivity")
    ):
        probes.append(("get_pipeline_run", {}))
        if context.previous_runs:
            probes.append(("get_previous_runs", {}))
            probes.append(("compare_runs", {}))

    if context.log_lines:
        for signal_name in target.signals.positive[:2]:
            probes.append(("search_logs", {"query": signal_name.replace("_", " ")}))

    if category.startswith("spark") or category.startswith("delta"):
        probes.append(("search_knowledge_base", {"query": category}))

    seen: set[tuple[str, tuple[tuple[str, object], ...]]] = set()
    unique: list[tuple[str, dict[str, object]]] = []
    for name, params in probes:
        key = (name, tuple(sorted(params.items())))
        if key in seen:
            continue
        seen.add(key)
        unique.append((name, params))
    return unique


__all__ = ["target_probes"]
