"""Analysis package: platform detection and signal extraction."""

from dedoc.analyzer.signals import (
    SIGNAL_REGISTRY,
    SignalDef,
    detect_platform,
    events_to_text,
    extract_exception_types,
    extract_signals,
    is_exact_signal,
)

__all__ = [
    "SIGNAL_REGISTRY",
    "SignalDef",
    "detect_platform",
    "events_to_text",
    "extract_exception_types",
    "extract_signals",
    "is_exact_signal",
]
