"""Bounded investigation agent — first prototype (BUILD_PLAN.md §26 step 11).

The deterministic diagnostic path was proven first; this agent is the
investigation layer that inspects *structured context* through the bounded,
read-only tool layer. It is fully deterministic: the planner emits probes, the
verifier challenges the top explanation, and hard limits (iterations, tool
calls, wall-clock deadline) bound every run. There is no AI or LLM here — AI is
an optional later layer (§11).
"""

from __future__ import annotations

import time

from dedoc.models.diagnosis import Diagnosis
from dedoc.tools.context import InvestigationContext
from dedoc.tools.registry import DEFAULT_TOOLKIT, call_tool

from .config import AgentConfig
from .models import (
    AgentFinding,
    AgentStatus,
    Contradiction,
    FindingKind,
    InvestigationRecord,
    ToolCall,
    ToolCallStatus,
)
from .planner import target_probes
from .verification import contradiction_from_result, supporting_from_result


def run_investigation(
    target: Diagnosis | None,
    context: InvestigationContext,
    *,
    config: AgentConfig | None = None,
    allowlist: frozenset[str] | None = None,
) -> InvestigationRecord:
    """Run one bounded investigation, returning a serializable record.

    ``target`` is the top hypothesis to challenge; ``config`` supplies the hard
    limits; ``allowlist`` (when not None) restricts which tools may run.
    """
    config = config or AgentConfig()
    effective_allowlist = config.allowlist if config.allowlist is not None else allowlist

    if target is None:
        return InvestigationRecord(
            status=AgentStatus.INSUFFICIENT_CONTEXT,
            iterations=0,
            tool_calls=0,
            max_iterations=config.max_iterations,
            max_tool_calls=config.max_tool_calls,
            reason="no diagnosis to investigate",
        )
    if not context.has_external_data():
        return InvestigationRecord(
            status=AgentStatus.INSUFFICIENT_CONTEXT,
            iterations=0,
            tool_calls=0,
            max_iterations=config.max_iterations,
            max_tool_calls=config.max_tool_calls,
            reason=(
                "no structured context (runs/schemas/metrics/query plan/logs) "
                "was provided beyond the input file"
            ),
        )

    tools = {tool.name: tool for tool in DEFAULT_TOOLKIT}
    probes = target_probes(target, context)
    start = time.monotonic()

    findings: list[AgentFinding] = []
    contradictions: list[Contradiction] = []
    calls: list[ToolCall] = []
    observed_support: set[str] = set()
    iterations = 0

    status = AgentStatus.SUCCESS
    reason = (
        "investigation of the available structured context completed; "
        "no contradictory evidence found"
    )

    for name, params in probes:
        if iterations >= config.max_iterations:
            status = AgentStatus.LIMIT_REACHED
            reason = f"investigation stopped after {config.max_iterations} iteration(s)"
            break
        if len(calls) >= config.max_tool_calls:
            status = AgentStatus.LIMIT_REACHED
            reason = f"investigation stopped after {config.max_tool_calls} tool call(s)"
            break
        if time.monotonic() - start >= config.timeout_seconds:
            status = AgentStatus.LIMIT_REACHED
            reason = f"investigation stopped at the {config.timeout_seconds}s deadline"
            break

        tool = tools.get(name)
        if tool is None:
            continue
        if effective_allowlist is not None and name not in effective_allowlist:
            continue

        iterations += 1
        result = call_tool(tool, context, params, allowlist=effective_allowlist)
        calls.append(
            ToolCall(
                tool=name,
                params=params,
                status=ToolCallStatus(result.status.value),
                summary=result.summary,
                detail=result.detail,
            )
        )

        contradiction = contradiction_from_result(result, target, name)
        if contradiction is not None:
            contradictions.append(contradiction)
            status = AgentStatus.SUCCESS
            reason = (
                f"investigation found evidence contradicting {target.id}; "
                "the top explanation is challenged"
            )
            break

        supporting = supporting_from_result(result, target, observed_support)
        if supporting is not None:
            observed_support.add(supporting)
            findings.append(
                AgentFinding(
                    kind=FindingKind.SUPPORTING,
                    tool=name,
                    description=(
                        f"signal '{supporting}' observed in structured context "
                        f"via '{name}', corroborating {target.id}"
                    ),
                    evidence=result.detail[:160],
                )
            )

    return InvestigationRecord(
        status=status,
        iterations=iterations,
        tool_calls=len(calls),
        max_iterations=config.max_iterations,
        max_tool_calls=config.max_tool_calls,
        reason=reason,
        findings=findings,
        contradictions=contradictions,
        calls=calls,
    )


__all__ = ["run_investigation"]
