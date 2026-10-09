"""Tool registry with allowlist and timeout enforcement (§12).

``call_tool`` is the single gate through which the agent invokes tools. It
enforces: declared parameter schemas, the caller's allowlist, the per-tool
timeout (via a bounded worker thread), and a safety net that turns any
unexpected failure into an ``ERROR`` outcome instead of letting it escape.
"""

from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any

from dedoc.core.errors import ToolError

from .base import Tool, ToolResult, ToolStatus, validate_params
from .context import InvestigationContext
from .library import build_library

#: The ordered MVP toolkit shared by the CLI, SDK, and agent.
DEFAULT_TOOLKIT: tuple[Tool, ...] = build_library()


def list_tools() -> list[Tool]:
    """Return all bundled tools."""
    return list(DEFAULT_TOOLKIT)


def get_tool(name: str) -> Tool | None:
    """Return a tool by name, or None when unknown."""
    return next((tool for tool in DEFAULT_TOOLKIT if tool.name == name), None)


def is_allowed(tool: Tool, allowlist: frozenset[str] | None) -> bool:
    """A None allowlist permits every bundled tool."""
    return tool.name in allowlist if allowlist is not None else True


def call_tool(
    tool: Tool,
    context: InvestigationContext,
    params: dict[str, Any],
    *,
    allowlist: frozenset[str] | None = None,
) -> ToolResult:
    """Validate, allowlist-check, and execute one tool call within its timeout.

    The outcome is always a ``ToolResult`` (never a raised exception): parameter
    or allowlist violations produce ``DENIED`` / ``ERROR``; a call that exceeds
    the tool's declared timeout produces ``TIMEOUT``.
    """
    if not is_allowed(tool, allowlist):
        return ToolResult(
            status=ToolStatus.DENIED,
            summary=f"tool '{tool.name}' is not in the allowlist",
        )
    try:
        values = validate_params(tool.params, params)
    except ToolError as exc:
        return ToolResult(status=ToolStatus.ERROR, summary=f"invalid parameters: {exc}")

    pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="dedoc-tool")
    try:
        future: Future[ToolResult] = pool.submit(tool.impl, context, values)
    except Exception as exc:
        pool.shutdown(wait=False, cancel_futures=True)
        return ToolResult(status=ToolStatus.ERROR, summary=f"tool '{tool.name}' failed: {exc}")

    try:
        result = future.result(timeout=tool.timeout_seconds)
    except TimeoutError:
        pool.shutdown(wait=False, cancel_futures=True)
        return ToolResult(
            status=ToolStatus.TIMEOUT,
            summary=f"tool '{tool.name}' exceeded its {tool.timeout_seconds}s timeout",
        )
    except Exception as exc:
        pool.shutdown(wait=False, cancel_futures=True)
        return ToolResult(status=ToolStatus.ERROR, summary=f"tool '{tool.name}' failed: {exc}")
    pool.shutdown(wait=True)
    return result


__all__ = [
    "DEFAULT_TOOLKIT",
    "call_tool",
    "get_tool",
    "is_allowed",
    "list_tools",
]
