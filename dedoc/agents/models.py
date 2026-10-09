"""Investigation agent models (BUILD_PLAN.md §11)."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class AgentStatus(StrEnum):
    SUCCESS = "success"
    INSUFFICIENT_CONTEXT = "insufficient_context"
    LIMIT_REACHED = "limit_reached"


class ToolCallStatus(StrEnum):
    SUCCESS = "success"
    UNAVAILABLE = "unavailable"
    DENIED = "denied"
    TIMEOUT = "timeout"
    ERROR = "error"


class FindingKind(StrEnum):
    SUPPORTING = "supporting"
    CONTRADICTING = "contradicting"
    NEUTRAL = "neutral"


class ToolCall(BaseModel):
    """One recorded tool invocation within an investigation."""

    tool: str
    params: dict[str, object] = Field(default_factory=dict)
    status: ToolCallStatus
    summary: str = ""
    detail: str = ""


class AgentFinding(BaseModel):
    """A deterministically classified observation from a tool result."""

    kind: FindingKind
    tool: str
    description: str
    evidence: str = ""


class Contradiction(BaseModel):
    """A negative-signal observation that challenges the top explanation."""

    description: str
    evidence: str = ""


class InvestigationRecord(BaseModel):
    """Outcome of one bounded investigation run, embedded in the report."""

    status: AgentStatus
    iterations: int
    tool_calls: int
    max_iterations: int
    max_tool_calls: int
    reason: str = ""
    findings: list[AgentFinding] = Field(default_factory=list)
    contradictions: list[Contradiction] = Field(default_factory=list)
    calls: list[ToolCall] = Field(default_factory=list)


__all__ = [
    "AgentFinding",
    "AgentStatus",
    "Contradiction",
    "FindingKind",
    "InvestigationRecord",
    "ToolCall",
    "ToolCallStatus",
]
