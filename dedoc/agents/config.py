"""Investigation agent configuration: explicit hard limits (§11).

Initial defaults per BUILD_PLAN.md §11: at most 8 investigation iterations,
at most 20 tool calls, and a bounded wall-clock deadline. ``allowlist=None``
permits every bundled tool; otherwise only listed tool names may execute.
"""

from __future__ import annotations

from dataclasses import dataclass

from dedoc.core.errors import AgentConfigError


@dataclass(frozen=True)
class AgentConfig:
    max_iterations: int = 8
    max_tool_calls: int = 20
    timeout_seconds: float = 10.0
    allowlist: frozenset[str] | None = None

    def __post_init__(self) -> None:
        if self.max_iterations < 1:
            raise AgentConfigError("max_iterations must be >= 1")
        if self.max_tool_calls < 1:
            raise AgentConfigError("max_tool_calls must be >= 1")
        if self.timeout_seconds <= 0:
            raise AgentConfigError("timeout_seconds must be > 0")


__all__ = ["AgentConfig"]
