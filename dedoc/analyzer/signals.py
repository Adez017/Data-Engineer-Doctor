"""Signal and platform extraction from failure text (§9 steps 2-3).

Every named signal used by diagnosis YAML must be registered here; the
diagnosis validator enforces the contract so no signal is silently dead.
"""

from __future__ import annotations

import re

from dedoc.models.failure import FailureEvent

#: Full dotted or short exception/error class names (e.g. pyspark.sql.utils.AnalysisException).
EXCEPTION_PATTERN = re.compile(r"\b([A-Za-z_][\w]*(?:\.[A-Za-z_][\w]*)*(?:Exception|Error))\b")

#: Named signal -> pattern. Patterns are case-insensitive.
SIGNAL_PATTERNS: dict[str, re.Pattern[str]] = {
    "resolved_column_not_found": re.compile(
        r"\[RESOLVED_COLUMN_NOT_FOUND\]"
        r"|column\s+'[^']*'\s+cannot\s+be\s+resolved"
        r"|cannot\s+resolve\s+'[^']+'\s+in\s+given\s+schema",
        re.IGNORECASE,
    ),
    "datatype_mismatch": re.compile(
        r"\[DATATYPE_MISMATCH\]|data\s+type\s+mismatch",
        re.IGNORECASE,
    ),
    "table_or_view_not_found": re.compile(
        r"\[TABLE_OR_VIEW_NOT_FOUND\]|table\s+or\s+view\s+'[^']*'\s+not\s+found",
        re.IGNORECASE,
    ),
    "authentication_failure": re.compile(
        r"authentication\s+failed|authentication\s+error|authentication\s+exception"
        r"|unauthorized|permission\s+denied|access\s+denied"
        r"|AuthenticationException",
        re.IGNORECASE,
    ),
    "dns_failure": re.compile(
        r"UnknownHostException|name\s+or\s+service\s+not\s+known"
        r"|nodename\s+nor\s+servname|dns\s+lookup\s+failed",
        re.IGNORECASE,
    ),
    "executor_oom": re.compile(
        r"java\.lang\.OutOfMemoryError|insufficient\s+memory"
        r"|exceeding\s+memory\s+limits",
        re.IGNORECASE,
    ),
    "stacktrace_present": re.compile(
        r"(?m)^\s+at\s+.+\(.+:\d+\)|Traceback \(most recent call last\)",
    ),
}

_DATABRICKS_MARKERS = ("databricks", "dbr/", "com.databricks")
_SPARK_MARKERS = (
    "org.apache.spark",
    "pyspark",
    "sparkexception",
    "sparkcontext",
    "sparksession",
    "analysisexception",
)


def extract_exception_types(text: str) -> list[str]:
    """Extract exception/error class names, full dotted form and short form."""
    found: list[str] = []
    for match in EXCEPTION_PATTERN.finditer(text):
        full = match.group(1)
        found.append(full)
        short = full.rsplit(".", 1)[-1]
        if short != full:
            found.append(short)
    return list(dict.fromkeys(found))


def detect_platform(text: str) -> str:
    """Detect the platform/engine from failure text (§9 step 2)."""
    lowered = text.lower()
    if any(marker in lowered for marker in _DATABRICKS_MARKERS):
        return "databricks"
    if any(marker in lowered for marker in _SPARK_MARKERS):
        return "spark"
    return "unknown"


def extract_signals(text: str) -> set[str]:
    """Return the set of named signals present in the text."""
    return {name for name, pattern in SIGNAL_PATTERNS.items() if pattern.search(text)}


def events_to_text(events: list[FailureEvent]) -> str:
    """Concatenate human-readable failure content from events."""
    parts: list[str] = []
    for event in events:
        if event.error_message:
            parts.append(event.error_message)
        if event.stacktrace:
            parts.append(event.stacktrace)
        if isinstance(event.raw_payload, str):
            parts.append(event.raw_payload)
    return "\n".join(parts)
