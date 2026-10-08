"""Evidence scoring: explicit weights -> score -> confidence band (§10).

Weights are the initial implementation hypothesis from BUILD_PLAN.md §10 and
are versioned via SCORING_MODEL_VERSION. Calibrate against an evaluation
dataset before changing them.
"""

from __future__ import annotations

from dedoc.diagnosis.engine import RuleMatch
from dedoc.evidence.models import (
    SCORING_MODEL_VERSION,
    ConfidenceBand,
    Evidence,
    EvidenceBundle,
    EvidenceType,
)

#: §10 weight table (initial hypothesis, versioned).
WEIGHTS: dict[EvidenceType, int] = {
    EvidenceType.ERROR_SIGNATURE: 40,
    EvidenceType.PLATFORM_MATCH: 20,
    EvidenceType.STACKTRACE: 20,
    EvidenceType.CORRELATED_SIGNAL: 15,
    EvidenceType.SUPPORTING_METADATA: 5,
}

#: Score -> band cutoffs (top of band): >=70 HIGH, >=40 MEDIUM, else LOW.
BAND_THRESHOLDS: tuple[tuple[int, ConfidenceBand], ...] = (
    (70, ConfidenceBand.HIGH),
    (40, ConfidenceBand.MEDIUM),
)

#: A diagnosis is only reported as conclusive at MEDIUM band or above.
MIN_SCORE_FOR_DIAGNOSIS = 40

MAX_SCORE = 100


def band_for_score(score: int) -> ConfidenceBand:
    for cutoff, band in BAND_THRESHOLDS:
        if score >= cutoff:
            return band
    return ConfidenceBand.LOW


def score_match(match: RuleMatch) -> EvidenceBundle:
    """Derive a 0-100 score, confidence band, and evidence list for a rule match."""
    evidence: list[Evidence] = []
    excerpt_used = False

    def add(etype: EvidenceType, description: str, source: str) -> None:
        nonlocal excerpt_used
        excerpt = None
        if not excerpt_used and match.excerpt:
            excerpt = match.excerpt
            excerpt_used = True
        evidence.append(
            Evidence(
                type=etype,
                weight=WEIGHTS[etype],
                description=description,
                source=source,
                excerpt=excerpt,
            )
        )

    for signal in match.exact_signals:
        add(
            EvidenceType.ERROR_SIGNATURE,
            f"Exact error signature matched: {signal}",
            f"signal:{signal}",
        )
    for signal in match.matched_signals:
        if signal not in match.exact_signals:
            add(
                EvidenceType.CORRELATED_SIGNAL,
                f"Supporting signal observed: {signal}",
                f"signal:{signal}",
            )
    if match.matched_exception_types:
        where = "stack trace" if match.has_stacktrace_evidence else "failure text"
        add(
            EvidenceType.STACKTRACE,
            f"Declared exception observed in {where}: " + ", ".join(match.matched_exception_types),
            "exception:" + ",".join(match.matched_exception_types),
        )
    if match.platform_match:
        add(
            EvidenceType.PLATFORM_MATCH,
            f"Platform detected: {match.platform}"
            f" (diagnosis supports: {', '.join(match.diagnosis.platforms)})",
            "platform:detect",
        )
    if match.has_metadata:
        add(
            EvidenceType.SUPPORTING_METADATA,
            "Runtime metadata present (job/stage/service/attributes)",
            "metadata:event",
        )

    raw_score = sum(item.weight for item in evidence)
    score = min(MAX_SCORE, raw_score)
    return EvidenceBundle(
        score=score,
        confidence_band=band_for_score(score),
        evidence=evidence,
    )


__all__ = [
    "BAND_THRESHOLDS",
    "MAX_SCORE",
    "MIN_SCORE_FOR_DIAGNOSIS",
    "SCORING_MODEL_VERSION",
    "WEIGHTS",
    "band_for_score",
    "score_match",
]
