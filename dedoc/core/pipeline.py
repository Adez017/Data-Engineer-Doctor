"""End-to-end deterministic diagnosis pipeline (§9, without steps 6/7 — Phase 3+)."""

from __future__ import annotations

from pathlib import Path

from dedoc import __version__
from dedoc.analyzer.signals import events_to_text, extract_exception_types
from dedoc.core.errors import InputError
from dedoc.diagnosis.engine import match_diagnoses, resolve_platform
from dedoc.diagnosis.loader import load_diagnoses
from dedoc.models.failure import FailureEvent
from dedoc.models.report import DiagnosisReport, ReportStatus
from dedoc.parser.input_parser import InputFormat, parse_input

_INSUFFICIENT_MESSAGE = (
    "No diagnosis matched the available evidence. "
    "There is insufficient evidence to support a conclusion."
)


def _annotate_events(events: list[FailureEvent], platform: str, text: str) -> list[str]:
    """Fill platform/error_type on events; return all observed error types."""
    exception_types = extract_exception_types(text)
    for event in events:
        if event.platform == "unknown":
            event.platform = platform
        if event.error_type is None and exception_types:
            event.error_type = exception_types[0]
    observed = [e.error_type for e in events if e.error_type is not None]
    return sorted(dict.fromkeys([*observed, *exception_types]))


def diagnose_file(
    path: str | Path,
    *,
    diagnoses_path: str | Path | None = None,
    input_format: InputFormat = InputFormat.AUTO,
) -> DiagnosisReport:
    """Run the deterministic diagnosis pipeline on an input file.

    Raises:
        InputError: if the input file is missing or malformed.
        DiagnosisLoadError: if diagnosis knowledge cannot be loaded.
    """
    input_path = Path(path)
    if not input_path.exists():
        raise InputError(f"input file not found: {input_path}")
    if not input_path.is_file():
        raise InputError(f"not a file: {input_path}")

    diagnoses = load_diagnoses(diagnoses_path)
    events = parse_input(input_path, input_format)
    text = events_to_text(events)
    platform = resolve_platform(events, text)
    error_types = _annotate_events(events, platform, text)
    matches = match_diagnoses(events, diagnoses, platform)

    if matches:
        status = ReportStatus.DIAGNOSED
        message = f"{len(matches)} diagnosis matched the available evidence."
    else:
        status = ReportStatus.INSUFFICIENT_EVIDENCE
        message = _INSUFFICIENT_MESSAGE

    return DiagnosisReport(
        dedoc_version=__version__,
        input_source=str(input_path),
        platform=platform,
        status=status,
        event_count=len(events),
        error_types=error_types,
        matches=matches,
        message=message,
    )
