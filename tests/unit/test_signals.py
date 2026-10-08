"""Unit tests for signal extraction, exception extraction, and platform detection."""

from __future__ import annotations

from dedoc.analyzer.signals import (
    SIGNAL_REGISTRY,
    detect_platform,
    events_to_text,
    extract_exception_types,
    extract_signals,
)
from dedoc.models.failure import FailureEvent


def test_extract_exception_types_dotted_and_short() -> None:
    text = "pyspark.sql.utils.AnalysisException: boom"
    types = extract_exception_types(text)
    assert "pyspark.sql.utils.AnalysisException" in types
    assert "AnalysisException" in types


def test_extract_exception_types_multiple() -> None:
    text = "TypeError: bad\njava.lang.OutOfMemoryError: heap"
    types = extract_exception_types(text)
    assert "TypeError" in types
    assert "java.lang.OutOfMemoryError" in types


def test_detect_platform_spark() -> None:
    assert detect_platform("org.apache.spark.SparkException: boom") == "spark"
    assert detect_platform("pyspark.sql.utils.AnalysisException") == "spark"


def test_detect_platform_databricks_wins_over_spark() -> None:
    text = "com.databricks.sql warehouse error org.apache.spark.SparkException"
    assert detect_platform(text) == "databricks"


def test_detect_platform_unknown() -> None:
    assert detect_platform("something unrelated happened") == "unknown"


def test_signal_resolved_column_not_found() -> None:
    text = "AnalysisException: [RESOLVED_COLUMN_NOT_FOUND] Column 'x' cannot be resolved."
    assert "resolved_column_not_found" in extract_signals(text)


def test_signal_resolved_column_not_found_classic_wording() -> None:
    text = "AnalysisException: cannot resolve 'total_amt' in given schema: struct<id:bigint>"
    assert "resolved_column_not_found" in extract_signals(text)


def test_signal_datatype_mismatch() -> None:
    assert "datatype_mismatch" in extract_signals("AnalysisException: [DATATYPE_MISMATCH]")
    assert "datatype_mismatch" in extract_signals("failed: data type mismatch detected")


def test_signal_table_or_view_not_found() -> None:
    text = "AnalysisException: [TABLE_OR_VIEW_NOT_FOUND] Table or view 't1' not found."
    assert "table_or_view_not_found" in extract_signals(text)


def test_signal_authentication_failure() -> None:
    assert "authentication_failure" in extract_signals("Authentication failed for user alice")
    assert "permission_denied" not in extract_signals("Authentication failed for user alice")
    assert "permission_denied" in extract_signals("Permission denied: /warehouse")
    assert "authentication_failure" not in extract_signals("Permission denied: /warehouse")


def test_signal_dns_failure() -> None:
    assert "dns_failure" in extract_signals("java.net.UnknownHostException: host1")


def test_signal_executor_oom() -> None:
    assert "executor_oom" in extract_signals("java.lang.OutOfMemoryError: Java heap space")


def test_signal_registry_names_are_valid() -> None:
    from dedoc.models.diagnosis import SIGNAL_NAME_PATTERN

    for name in SIGNAL_REGISTRY:
        assert SIGNAL_NAME_PATTERN.match(name), name


def test_signal_registry_exact_flags() -> None:
    assert SIGNAL_REGISTRY["resolved_column_not_found"].exact is True
    assert SIGNAL_REGISTRY["datatype_mismatch"].exact is True
    assert SIGNAL_REGISTRY["table_or_view_not_found"].exact is True
    assert SIGNAL_REGISTRY["dns_failure"].exact is True
    assert SIGNAL_REGISTRY["executor_oom"].exact is True
    assert SIGNAL_REGISTRY["authentication_failure"].exact is True
    assert SIGNAL_REGISTRY["permission_denied"].exact is True
    assert SIGNAL_REGISTRY["connection_timeout"].exact is True
    assert SIGNAL_REGISTRY["driver_oom"].exact is False
    assert SIGNAL_REGISTRY["data_skew"].exact is False
    assert SIGNAL_REGISTRY["broadcast_size_exceeded"].exact is False
    assert SIGNAL_REGISTRY["stacktrace_present"].exact is False


def test_events_to_text() -> None:
    events = [
        FailureEvent(error_message="msg1", stacktrace="trace1", raw_payload="payload1"),
        FailureEvent(error_message="msg2"),
    ]
    text = events_to_text(events)
    assert "msg1" in text and "trace1" in text and "payload1" in text and "msg2" in text
