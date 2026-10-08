"""Deterministic rule matching: exceptions + signals -> matched diagnoses (§9 steps 4-5)."""

from __future__ import annotations

from collections.abc import Mapping

from dedoc.analyzer.signals import (
    detect_platform,
    events_to_text,
    extract_exception_types,
    extract_signals,
)
from dedoc.models.diagnosis import Diagnosis
from dedoc.models.failure import FailureEvent
from dedoc.models.report import MatchedDiagnosis


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
    platform = detect_platform(text)
    if platform != "unknown":
        return platform
    for event in events:
        if event.platform and event.platform != "unknown":
            return event.platform
    return "unknown"


def match_diagnoses(
    events: list[FailureEvent],
    diagnoses: Mapping[str, Diagnosis],
    platform: str,
) -> list[MatchedDiagnosis]:
    """Apply deterministic rules and return matched diagnoses, sorted by id.

    A diagnosis matches when at least one declared exception type or positive
    signal is observed AND no negative (contradictory) signal is present.
    """
    text = events_to_text(events)
    exception_types = _observed_exception_types(events, text)
    signals = extract_signals(text)

    matched: list[MatchedDiagnosis] = []
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
        if not matched_exceptions and not matched_signals:
            continue
        if set(diagnosis.signals.negative) & signals:
            continue
        matched.append(
            MatchedDiagnosis(
                id=diagnosis.id,
                name=diagnosis.name,
                category=diagnosis.category,
                severity=diagnosis.severity.default,
                platforms=diagnosis.platforms,
                hypotheses=diagnosis.hypotheses,
                matched_exception_types=matched_exceptions,
                matched_signals=matched_signals,
                recommendations=diagnosis.recommendations,
                references=diagnosis.references,
            )
        )
    return sorted(matched, key=lambda item: item.id)
