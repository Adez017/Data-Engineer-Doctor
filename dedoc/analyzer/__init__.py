"""Analysis package: platform detection and signal extraction."""

from dedoc.analyzer.signals import (
    SIGNAL_PATTERNS,
    detect_platform,
    events_to_text,
    extract_exception_types,
    extract_signals,
)

__all__ = [
    "SIGNAL_PATTERNS",
    "detect_platform",
    "events_to_text",
    "extract_exception_types",
    "extract_signals",
]
