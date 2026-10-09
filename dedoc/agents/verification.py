"""Verification: challenge the top explanation with structured evidence (§11).

The verification step is deliberately independent of the planner: it scans
every redacted tool output for the target explanation's *negative signals*
(contradictory evidence) and for its positive signals that were not observed
by the deterministic engine (corroborating evidence). Both are classified
deterministically — no self-reported confidence anywhere.
"""

from __future__ import annotations

from dedoc.analyzer.signals import extract_signals
from dedoc.core.redaction import redact
from dedoc.models.diagnosis import Diagnosis
from dedoc.tools.base import ToolResult, ToolStatus

from .models import Contradiction


def _observed_from(result: ToolResult) -> set[str]:
    text = redact(f"{result.summary}\n{result.detail}")
    return extract_signals(text)


def contradiction_from_result(
    result: ToolResult, target: Diagnosis, tool_name: str
) -> Contradiction | None:
    """Return a contradiction when a negative signal of ``target`` appears.

    Negative signals disqualify a diagnosis in the deterministic engine
    (BUILD_PLAN.md §6); observing one in structured context challenges the
    explanation the same way.
    """
    if result.status is not ToolStatus.SUCCESS:
        return None
    observed = _observed_from(result)
    for negative in target.signals.negative:
        if negative in observed:
            return Contradiction(
                description=(f"negative signal '{negative}' observed in '{tool_name}' output"),
                evidence=_clamp(redact(result.detail)),
            )
    return None


def supporting_from_result(result: ToolResult, target: Diagnosis, already: set[str]) -> str | None:
    """Return a positive signal of ``target`` newly corroborated by this result."""
    if result.status is not ToolStatus.SUCCESS:
        return None
    observed = _observed_from(result)
    for positive in target.signals.positive:
        if positive in observed and positive not in already:
            return positive
    return None


def _clamp(text: str, limit: int = 180) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


__all__ = ["contradiction_from_result", "supporting_from_result"]
