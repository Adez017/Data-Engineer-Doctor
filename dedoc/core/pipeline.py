"""End-to-end diagnosis pipeline (§9): deterministic engine plus the optional
bounded investigation agent (step 6) over structured context (Phase 4)."""

from __future__ import annotations

from pathlib import Path

from dedoc import __version__
from dedoc.agents.config import AgentConfig
from dedoc.agents.orchestrator import run_investigation
from dedoc.analyzer.signals import events_to_text, extract_exception_types
from dedoc.core.errors import InputError
from dedoc.diagnosis.engine import RuleMatch, match_rules, resolve_platform
from dedoc.diagnosis.loader import load_diagnoses
from dedoc.evidence import MIN_SCORE_FOR_DIAGNOSIS, score_match
from dedoc.evidence.models import ConfidenceBand, EvidenceBundle
from dedoc.models.diagnosis import severity_rank
from dedoc.models.failure import FailureEvent
from dedoc.models.report import DiagnosisReport, MatchedDiagnosis, ReportStatus
from dedoc.parser.input_parser import InputFormat, parse_input
from dedoc.tools.context import InvestigationContext

_NO_MATCH_MESSAGE = (
    "No diagnosis matched the available evidence. "
    "There is insufficient evidence to support a conclusion."
)

ScoredMatch = tuple[MatchedDiagnosis, EvidenceBundle]


def _rank_key(scored: ScoredMatch) -> tuple[int, int, str]:
    """Score desc, then severity (critical first), then stable id."""
    matched, _ = scored
    return (-matched.score, severity_rank(matched.severity), matched.id)


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


def _score_rule(rule_match: RuleMatch) -> ScoredMatch:
    diagnosis = rule_match.diagnosis
    bundle = score_match(rule_match)
    matched = MatchedDiagnosis(
        id=diagnosis.id,
        name=diagnosis.name,
        category=diagnosis.category,
        severity=diagnosis.severity.default,
        platforms=diagnosis.platforms,
        score=bundle.score,
        confidence_band=bundle.confidence_band,
        evidence=bundle.evidence,
        hypotheses=diagnosis.hypotheses,
        matched_exception_types=rule_match.matched_exception_types,
        matched_signals=rule_match.matched_signals,
        recommendations=diagnosis.recommendations,
        references=diagnosis.references,
    )
    return matched, bundle


def _build_status(ranked: list[ScoredMatch]) -> tuple[ReportStatus, ConfidenceBand | None, str]:
    if not ranked:
        return ReportStatus.INSUFFICIENT_EVIDENCE, None, _NO_MATCH_MESSAGE
    top_matched, top_bundle = ranked[0]
    band = top_bundle.confidence_band
    evidence_count = len(top_bundle.evidence)
    if top_bundle.score >= MIN_SCORE_FOR_DIAGNOSIS:
        message = (
            f"{top_matched.id} selected with {band.value} confidence "
            f"({top_bundle.score}/100) based on {evidence_count} evidence item(s)."
        )
        if len(ranked) > 1:
            message += f" {len(ranked) - 1} competing diagnosis(es) considered."
        return ReportStatus.DIAGNOSED, band, message
    message = (
        f"Best candidate {top_matched.id} reached only {band.value} confidence "
        f"({top_bundle.score}/100). Insufficient evidence for a conclusion."
    )
    return ReportStatus.INSUFFICIENT_EVIDENCE, band, message


def diagnose_file(
    path: str | Path,
    *,
    diagnoses_path: str | Path | None = None,
    input_format: InputFormat = InputFormat.AUTO,
    investigate: bool = False,
    context: InvestigationContext | None = None,
    agent_config: AgentConfig | None = None,
) -> DiagnosisReport:
    """Run the deterministic diagnosis pipeline on an input file.

    When ``investigate`` is enabled and the file yields at least one matched
    diagnosis, the bounded investigation agent (§11) inspects the optional
    ``context`` through the read-only tool layer and attaches its findings to
    the report.

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

    rules = match_rules(events, diagnoses, platform)
    ranked = sorted((_score_rule(rule) for rule in rules), key=_rank_key)
    status, top_band, message = _build_status(ranked)

    investigation = None
    if investigate and ranked and (top := diagnoses.get(ranked[0][0].id)) is not None:
        investigation = run_investigation(
            top,
            context if context is not None else InvestigationContext(events=events, text=text),
            config=agent_config,
        )

    return DiagnosisReport(
        dedoc_version=__version__,
        input_source=str(input_path),
        platform=platform,
        status=status,
        top_confidence_band=top_band,
        event_count=len(events),
        error_types=error_types,
        matches=[matched for matched, _ in ranked],
        message=message,
        investigation=investigation,
    )
