"""Signal and platform extraction from failure text (§9 steps 2-3).

Every named signal used by diagnosis YAML must be registered here; the
diagnosis validator enforces the contract so no signal is silently dead.

``exact=True`` marks signals that correspond to a known, precise error
signature (for example an error-code token); these score as an *exact known
error signature* (weight 40) in the evidence model (§10). Behavioral or
heuristic signals score as *correlated runtime signals* (weight 15).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from dedoc.models.failure import FailureEvent


@dataclass(frozen=True)
class SignalDef:
    pattern: re.Pattern[str]
    exact: bool = False


#: Full dotted or short exception/error class names (e.g. pyspark.sql.utils.AnalysisException).
#: The suffix set includes Failure so engine classes such as ExecutorLostFailure are captured.
EXCEPTION_PATTERN = re.compile(
    r"\b([A-Za-z_][\w]*(?:\.[A-Za-z_][\w]*)*(?:Exception|Error|Failure))\b"
)


def _sig(pattern: str, *, exact: bool, flags: int = re.IGNORECASE) -> SignalDef:
    return SignalDef(pattern=re.compile(pattern, flags), exact=exact)


#: Named signal -> definition. Patterns are case-insensitive unless noted.
SIGNAL_REGISTRY: dict[str, SignalDef] = {
    # -- schema ------------------------------------------------------------
    "resolved_column_not_found": _sig(
        r"\[RESOLVED_COLUMN_NOT_FOUND\]"
        r"|\[UNRESOLVED_COLUMN"
        r"|column\s+[`'\"][^`'\"]+[`'\"]\s+cannot\s+be\s+resolved"
        r"|cannot\s+resolve\s+[`'\"][^`'\"]+[`'\"]\s+in\s+given\s+schema",
        exact=True,
    ),
    "datatype_mismatch": _sig(
        r"\[DATATYPE_MISMATCH\]|data\s+type\s+mismatch",
        exact=True,
    ),
    "unexpected_column": _sig(
        r"\[TOO_MANY_DATA_COLUMNS\]"
        r"|too\s+many\s+data\s+columns"
        r"|\[EXTRA_COLUMNS\]"
        r"|cannot\s+write\s+extra\s+columns",
        exact=True,
    ),
    "ambiguous_reference": _sig(
        r"\[AMBIGUOUS_REFERENCE"
        r"|reference\s+[`'\"][^`'\"]+[`'\"]\s+is\s+ambiguous"
        r"|column\s+[`'\"][^`'\"]+[`'\"]\s+is\s+ambiguous"
        r"|ambiguous\s+reference\s+to\s+the\s+field"
        r"|ambiguous\s+column\s+name\s+in\s+the\s+input\s+data",
        exact=True,
    ),
    "schema_evolution_blocked": _sig(
        r"a\s+schema\s+mismatch\s+detected\s+when\s+writing",
        exact=True,
    ),
    "nested_schema_field_unresolved": _sig(
        r"\[UNRESOLVED_FIELD"
        r"|cannot\s+be\s+resolved\s+with\s+the\s+struct-type\s+column",
        exact=True,
    ),
    # -- data quality ------------------------------------------------------
    "null_constraint_violated": _sig(
        r"\[NOT_NULL_CONSTRAINT_VIOLATION\]"
        r"|assigning\s+a\s+NULL\s+is\s+not\s+allowed\s+here",
        exact=True,
    ),
    "duplicate_keys": _sig(
        r"found\s+duplicate\s+keys",
        exact=True,
    ),
    "date_parse_failure": _sig(
        r"cannot\s+be\s+(cast|converted)\s+to\s+(date|timestamp)\b",
        exact=True,
    ),
    "invalid_numeric_value": _sig(
        r"cannot\s+be\s+(cast|converted)\s+to\s+(tinyint|smallint|integer|int|bigint"
        r"|float|double|real|decimal|numeric)"
        r"|cannot\s+be\s+cast\s+to\s+[^\n]+\s+due\s+to\s+an\s+overflow"
        r"|\[CAST_OVERFLOW\]"
        r"|\[ARITHMETIC_OVERFLOW\]",
        exact=True,
    ),
    "merge_cardinality_violation": _sig(
        r"\[MERGE_CARDINALITY_VIOLATION\]"
        r"|matched\s+a\s+single\s+row\s+from\s+the\s+target\s+table",
        exact=True,
    ),
    # -- connectivity ------------------------------------------------------
    "table_or_view_not_found": _sig(
        r"\[TABLE_OR_VIEW_NOT_FOUND\]"
        r"|table\s+or\s+view\s+[`'\"][^`'\"]+[`'\"]\s+not\s+found"
        r"|the\s+table\s+or\s+view\s+[^\n]+\s+cannot\s+be\s+found",
        exact=True,
    ),
    "authentication_failure": _sig(
        r"authentication\s+failed|authentication\s+error|authentication\s+exception"
        r"|unauthorized|AuthenticationException"
        r"|invalid[_ ]authentication|access\s+token.*(expired|invalid)"
        r"|HTTP\s+401|401\s+[Uu]nauthorized",
        exact=True,
    ),
    "dns_failure": _sig(
        r"UnknownHostException|name\s+or\s+service\s+not\s+known"
        r"|nodename\s+nor\s+servname|dns\s+lookup\s+failed",
        exact=True,
    ),
    "permission_denied": _sig(
        r"permission\s+denied|access\s+denied|\[ACCESS_DENIED\]"
        r"|authori[sz]ation\s+permission\s+denied",
        exact=True,
    ),
    "connection_timeout": _sig(
        r"connect\s+timed\s+out|connection\s+timed\s+out"
        r"|ConnectTimeoutException|read\s+timed\s+out",
        exact=True,
    ),
    "endpoint_unavailable": _sig(
        r"connection\s+refused|remote\s+end\s+(closed|reset)"
        r"|service\s+unavailable|\[ENDPOINT_UNAVAILABLE\]",
        exact=True,
    ),
    # -- spark runtime -----------------------------------------------------
    "executor_oom": _sig(
        r"java\.lang\.OutOfMemoryError|insufficient\s+memory"
        r"|exceeding\s+memory\s+limits",
        exact=True,
    ),
    "driver_oom": _sig(
        r"(?=.*OutOfMemoryError)"
        r"(?=.*(?:call\s+to\s+\S+\.collect|\btoPandas\b|spark\.driver\.memory"
        r"|driver\s+stack\s+trace|driver\s+(node|process|oom|out\s+of\s+memory)"
        r"|out\s+of\s+memory\s+on\s+the\s+driver))",
        exact=False,
        flags=re.IGNORECASE | re.DOTALL,
    ),
    "executor_lost": _sig(
        r"ExecutorLostFailure"
        r"|Lost\s+executor\s+\d+"
        r"|executor\s+heartbeat\s+timed\s+out",
        exact=True,
    ),
    "task_failure_repeated": _sig(
        r"failed\s+\d+\s+times,\s+most\s+recent\s+failure"
        r"|failed\s+\d+\s+times;\s+aborting\s+job",
        exact=True,
    ),
    "shuffle_fetch_failed": _sig(
        r"FetchFailedException"
        r"|Missing\s+an\s+output\s+location\s+for\s+shuffle",
        exact=True,
    ),
    "broadcast_timeout": _sig(
        r"BroadcastTimeoutException|broadcast\s+(channel\s+)?timed?\s+out"
        r"|error\s+broadcasting|spark\.sql\.broadcastTimeout",
        exact=False,
    ),
    "broadcast_oom": _sig(
        r"not\s+enough\s+memory\s+to\s+build\s+and\s+broadcast"
        r"|broadcast.*OutOfMemoryError|OutOfMemoryError[^\n]*broadcast",
        exact=True,
    ),
    "stage_failure": _sig(
        r"job\s+aborted\s+due\s+to\s+stage\s+failure",
        exact=True,
    ),
    "data_skew": _sig(
        r"data\s+skew|skewed\s+(join|partition|keys?|group)",
        exact=False,
    ),
    # -- delta -------------------------------------------------------------
    "delta_metadata_changed": _sig(r"MetadataChangedException", exact=True),
    "delta_protocol_changed": _sig(r"ProtocolChangedException", exact=True),
    "delta_concurrent_transaction": _sig(r"ConcurrentTransactionException", exact=True),
    "delta_concurrent_conflict": _sig(
        r"ConcurrentAppendException"
        r"|ConcurrentDeleteDeleteException"
        r"|ConcurrentWriteException"
        r"|DeltaConcurrentModificationException",
        exact=True,
    ),
    "delta_merge_fields_failed": _sig(
        r"\[DELTA_FAILED_TO_MERGE_FIELDS\]|failed\s+to\s+merge\s+fields",
        exact=True,
    ),
    "delta_not_a_table": _sig(
        r"is\s+not\s+a\s+Delta\s+table",
        exact=False,
    ),
    "invalid_partition": _sig(
        r"\[INVALID_PARTITION_COLUMN"
        r"|\[PARTITION_WITH_NESTED_COLUMN"
        r"|cannot\s+use\s+[^\n]+\s+for\s+partition\s+column"
        r"|partition\s+clause\s+cannot\s+contain\s+the\s+non-partition\s+column"
        r"|invalid\s+partitioning:",
        exact=True,
    ),
    # -- performance -------------------------------------------------------
    "small_files": _sig(
        r"too\s+many\s+(small\s+)?files"
        r"|small\s+files?\s+(problem|issue|detected)"
        r"|number\s+of\s+files\s+(is\s+)?(too\s+)?(high|large|many)",
        exact=False,
    ),
    "excessive_shuffle": _sig(
        r"excessive\s+shuffle|shuffle\s+(data\s+)?(size|volume)\s+(is\s+)?(too\s+)?(high|large)"
        r"|shuffle\s+partition\s+count\s+(is\s+)?(too\s+)?(high|low)",
        exact=False,
    ),
    "missing_partition_pruning": _sig(
        r"partition\s+pruning\s+(was\s+)?(not|never)\s+(applied|pushed|enabled)"
        r"|full\s+(table\s+)?scan\s+(detected|on\s+non-partitioned|of\s+partition)"
        r"|missing\s+partition\s+(filter|pruning)",
        exact=False,
    ),
    "broadcast_size_exceeded": _sig(
        r"broadcast\s+(table\s+)?(size|data)\s+(exceeds|exceeded|is\s+(too\s+)?(large|big))"
        r"|autoBroadcastJoinThreshold"
        r"|too\s+large\s+to\s+broadcast"
        r"|broadcast[^\n]*(threshold|exceeded)",
        exact=False,
    ),
    # -- misc --------------------------------------------------------------
    "stacktrace_present": _sig(
        r"^\s+at\s+.+\(.+:\d+\)|Traceback \(most recent call last\)",
        exact=False,
        flags=re.MULTILINE,
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


def is_exact_signal(name: str) -> bool:
    """True when the signal is a known precise error signature (§10 weight 40)."""
    definition = SIGNAL_REGISTRY.get(name)
    return definition.exact if definition else False


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
    return {name for name, definition in SIGNAL_REGISTRY.items() if definition.pattern.search(text)}


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
