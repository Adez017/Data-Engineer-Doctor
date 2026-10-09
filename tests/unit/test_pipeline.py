"""Unit tests for the diagnosis pipeline (§9 step 6): ranking, status, message."""

from __future__ import annotations

from dedoc.core.pipeline import _rank_key
from dedoc.evidence.models import ConfidenceBand, EvidenceBundle
from dedoc.models.diagnosis import DiagnosisSeverity, severity_rank
from dedoc.models.report import MatchedDiagnosis


def _matched(severity: DiagnosisSeverity, *, score: int, id: str) -> MatchedDiagnosis:
    return MatchedDiagnosis(
        id=id,
        name="test",
        category="test.category",
        severity=severity,
        platforms=["spark"],
        score=score,
        confidence_band=ConfidenceBand.MEDIUM,
    )


def _key(severity: DiagnosisSeverity, *, score: int, id: str) -> tuple[int, int, str]:
    bundle = EvidenceBundle(score=score, confidence_band=ConfidenceBand.MEDIUM)
    return _rank_key((_matched(severity, score=score, id=id), bundle))


def test_severity_rank_ordering() -> None:
    critical = DiagnosisSeverity.CRITICAL
    high = DiagnosisSeverity.HIGH
    medium = DiagnosisSeverity.MEDIUM
    low = DiagnosisSeverity.LOW
    assert (
        severity_rank(critical) < severity_rank(high) < severity_rank(medium) < severity_rank(low)
    )


def test_score_is_primary_then_severity_then_id() -> None:
    # Score is the primary key: a MEDIUM 40 outranks a HIGH 30.
    assert _key(DiagnosisSeverity.MEDIUM, score=40, id="B") < _key(
        DiagnosisSeverity.HIGH, score=30, id="C"
    )
    # On a score tie, severity breaks it: critical before low.
    assert _key(DiagnosisSeverity.CRITICAL, score=40, id="A") < _key(
        DiagnosisSeverity.LOW, score=40, id="B"
    )
    # Severity AND score equal -> stable diagnosis id decides.
    assert _key(DiagnosisSeverity.LOW, score=40, id="A") < _key(
        DiagnosisSeverity.LOW, score=40, id="Z"
    )
