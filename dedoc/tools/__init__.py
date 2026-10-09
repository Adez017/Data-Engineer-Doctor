"""Investigation tool layer (BUILD_PLAN.md §12): read-only, bounded, declared.

Exposes the tool registry (with allowlist + timeout enforcement) and the
structured investigation context that tools read from. Everything here is
deterministic and requires no AI provider.
"""

from dedoc.tools.base import (
    ExecutionEnv,
    Param,
    ParamKind,
    SecurityClass,
    Tool,
    ToolResult,
    ToolStatus,
    coerce_param,
    validate_params,
)
from dedoc.tools.context import (
    InvestigationContext,
    MetricsSample,
    PipelineRun,
    SchemaSnapshot,
    context_from_mapping,
)
from dedoc.tools.registry import (
    DEFAULT_TOOLKIT,
    call_tool,
    get_tool,
    is_allowed,
    list_tools,
)

__all__ = [
    "DEFAULT_TOOLKIT",
    "ExecutionEnv",
    "InvestigationContext",
    "MetricsSample",
    "Param",
    "ParamKind",
    "PipelineRun",
    "SchemaSnapshot",
    "SecurityClass",
    "Tool",
    "ToolResult",
    "ToolStatus",
    "call_tool",
    "coerce_param",
    "context_from_mapping",
    "get_tool",
    "is_allowed",
    "list_tools",
    "validate_params",
]
