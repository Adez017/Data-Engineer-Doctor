"""Deterministic rule matching: exceptions + signals -> rule matches (§9 steps 4-5).

Precision rule (v0.1): a diagnosis with declared positive signals only matches
when at least one positive signal is observed — a bare exception type is
corroborating evidence, not sufficient on its own. A diagnosis with no
declared signals matches on its exception types alone.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from dedoc.analyzer.signals import (
    SIGNAL_REGISTRY,
    events_to_text,
    extract_exception_types,
    extract_signals,
    is_exact_signal,
)
from dedoc.core.redaction import redact
from dedoc.models.diagnosis import Diagnosis
from dedoc.models.failure import FailureEvent

_EXCERPT_MAX = 200


@dataclass
class RuleMatch:
    """Internal: one diagnosis matched by deterministic rules, with observations."""

    diagnosis: Diagnosis
    platform: str
    platform_match: bool
    matched_signals: list[str]
    matched_exception_types: list[str]
    exact_signals: list[str]
    has_stacktrace_evidence: bool
    has_metadata: bool
    excerpt: str | None


def _exception_matches(declared: str, observed: str) -> bool:
    """A declared exception type matches an observed one exactly or as a class-name suffix."""
    return observed == declared or observed.endswith("." + declared)


def _observed_exception_types(events: list[FailureEvent], text: str) -> list[str]:
    from_event: list[str] = []
    for event in events:
        if event.error_type:
            from_event.append(event.error_type)
            short = event.error_type.rsplit(".", 1)[-1]
            if short != event.error_type:
                from_event.append(short)
    combined = from_event + extract_exception_types(text)
    return list(dict.fromkeys(combined))


def resolve_platform(events: list[FailureEvent], text: str) -> str:
    """Detect the platform from text, falling back to event fields (§9 step 2)."""
    from dedoc.analyzer.signals import detect_platform

    platform = detect_platform(text)
    if platform != "unknown":
        return platform
    for event in events:
        if event.platform and event.platform != "unknown":
            return event.platform
    return "unknown"


def _find_excerpt(
    text: str, matched_signals: list[str], matched_exceptions: list[str]
) -> str | None:
    """Best supporting line, redacted and clamped.

    Priority: a line matching a declared signal, then an exception message
    line (not a stack frame), then any line mentioning the exception type.
    """
    lines = [
        (line_no, line.strip())
        for line_no, line in enumerate(text.splitlines(), start=1)
        if line.strip()
    ]
    signal_patterns = [
        definition.pattern
        for name in matched_signals
        if (definition := SIGNAL_REGISTRY.get(name)) is not None
    ]
    for line_no, line in lines:
        if any(pattern.search(line) for pattern in signal_patterns):
            return f"line {line_no}: {redact(line)[:_EXCERPT_MAX]}"
    for line_no, line in lines:
        if line.startswith("at "):
            continue
        if any(exception in line for exception in matched_exceptions):
            return f"line {line_no}: {redact(line)[:_EXCERPT_MAX]}"
    for line_no, line in lines:
        if any(exception in line for exception in matched_exceptions):
            return f"line {line_no}: {redact(line)[:_EXCERPT_MAX]}"
    return None


def _has_metadata(events: list[FailureEvent]) -> bool:
    for event in events:
        if event.job or event.stage or event.service or event.task:
            return True
        if event.resource_attributes or event.event_attributes:
            return True
    return False


def match_rules(
    events: list[FailureEvent],
    diagnoses: Mapping[str, Diagnosis],
    platform: str,
) -> list[RuleMatch]:
    """Apply deterministic rules and return rule matches, sorted by diagnosis id."""
    text = events_to_text(events)
    exception_types = _observed_exception_types(events, text)
    signals = extract_signals(text)
    has_stacktrace = "stacktrace_present" in signals or any(e.stacktrace for e in events)
    has_metadata = _has_metadata(events)

    matches: list[RuleMatch] = []
    for diagnosis in diagnoses.values():
        if platform != "unknown" and platform not in diagnosis.platforms:
            continue
        matched_exceptions = sorted(
            {
                declared
                for declared in diagnosis.patterns.exception_types
                if any(_exception_matches(declared, observed) for observed in exception_types)
            }
        )
        matched_signals = sorted(set(diagnosis.signals.positive) & signals)

        if diagnosis.signals.positive:
            if not matched_signals:
                continue
        elif not matched_exceptions:
            continue

        if set(diagnosis.signals.negative) & signals:
            continue

        matches.append(
            RuleMatch(
                diagnosis=diagnosis,
                platform=platform,
                platform_match=platform != "unknown" and platform in diagnosis.platforms,
                matched_signals=matched_signals,
                matched_exception_types=matched_exceptions,
                exact_signals=[s for s in matched_signals if is_exact_signal(s)],
                has_stacktrace_evidence=has_stacktrace,
                has_metadata=has_metadata,
                excerpt=_find_excerpt(text, matched_signals, matched_exceptions),
            )
        )
    return sorted(matches, key=lambda match: match.diagnosis.id)
