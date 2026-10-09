"""Tool contract (BUILD_PLAN.md §12).

Every tool must declare its input schema, output schema, read/write behavior,
security classification, timeout, and the execution environments it is
permitted in before the agent may invoke it. All tools in the MVP toolkit are
strictly read-only and redact log-derived text before returning it.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, Any

from dedoc.core.errors import ToolError

if TYPE_CHECKING:
    from dedoc.tools.context import InvestigationContext


class SecurityClass(StrEnum):
    READ_ONLY = "read_only"


class ExecutionEnv(StrEnum):
    LOCAL = "local"
    CI = "ci"
    CLOUD = "cloud"


class ToolStatus(StrEnum):
    SUCCESS = "success"
    UNAVAILABLE = "unavailable"
    DENIED = "denied"
    TIMEOUT = "timeout"
    ERROR = "error"


class ParamKind(StrEnum):
    STR = "str"
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"


@dataclass(frozen=True)
class Param:
    """One declared input parameter with its coercion kind."""

    name: str
    kind: ParamKind = ParamKind.STR
    description: str = ""
    required: bool = False
    default: Any = None


@dataclass(frozen=True)
class ToolResult:
    """Structured, redacted outcome of one tool invocation."""

    status: ToolStatus
    summary: str
    detail: str = ""
    data: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Tool:
    """A declared investigation capability with enforcement metadata."""

    name: str
    description: str
    params: tuple[Param, ...]
    output_schema: str
    impl: Callable[[InvestigationContext, dict[str, Any]], ToolResult] = field(
        compare=False, repr=False
    )
    read_only: bool = True
    security: SecurityClass = SecurityClass.READ_ONLY
    timeout_seconds: int = 5
    environments: frozenset[ExecutionEnv] = field(
        default_factory=lambda: frozenset({ExecutionEnv.LOCAL, ExecutionEnv.CI})
    )


def coerce_param(kind: ParamKind, raw: Any) -> Any:
    """Coerce a raw parameter value to its declared kind, raising on garbage."""
    if kind is ParamKind.INT:
        return int(raw)
    if kind is ParamKind.FLOAT:
        return float(raw)
    if kind is ParamKind.BOOL:
        if isinstance(raw, str):
            lowered = raw.strip().lower()
            if lowered in {"1", "true", "yes", "on"}:
                return True
            if lowered in {"0", "false", "no", "off"}:
                return False
        return bool(raw)
    return str(raw)


def validate_params(declared: tuple[Param, ...], supplied: dict[str, Any]) -> dict[str, Any]:
    """Validate and coerce supplied parameters against the declared schema.

    Raises:
        ToolError: on unknown, missing, or invalid parameters.
    """
    known = {param.name for param in declared}
    extra = [name for name in supplied if name not in known]
    if extra:
        raise ToolError(f"unexpected parameter(s): {', '.join(sorted(extra))}")
    values: dict[str, Any] = {}
    for param in declared:
        raw = supplied.get(param.name, param.default)
        if raw is None:
            if param.required:
                raise ToolError(f"missing required parameter: {param.name}")
            continue
        try:
            values[param.name] = coerce_param(param.kind, raw)
        except (TypeError, ValueError) as exc:
            raise ToolError(f"invalid value for parameter '{param.name}': {exc}") from exc
    return values


__all__ = [
    "ExecutionEnv",
    "Param",
    "ParamKind",
    "SecurityClass",
    "Tool",
    "ToolResult",
    "ToolStatus",
    "coerce_param",
    "validate_params",
]
