"""Bounded investigation agent (BUILD_PLAN.md §11, §26 step 11).

Deterministic planner + bounded read-only tools + independent verification.
No AI provider is required; the deterministic core remains fully usable with
investigation disabled.

Note: the package entrypoint intentionally does not import the orchestrator,
so importing DEDoc models never pulls in the tool layer (no import cycles).
Use ``dedoc.agents.orchestrator.run_investigation`` directly.
"""

from dedoc.agents.config import AgentConfig
from dedoc.agents.models import (
    AgentFinding,
    AgentStatus,
    Contradiction,
    FindingKind,
    InvestigationRecord,
    ToolCall,
    ToolCallStatus,
)

__all__ = [
    "AgentConfig",
    "AgentFinding",
    "AgentStatus",
    "Contradiction",
    "FindingKind",
    "InvestigationRecord",
    "ToolCall",
    "ToolCallStatus",
]
