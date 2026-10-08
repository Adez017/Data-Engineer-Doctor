"""Unit tests for evidence scoring (§10)."""

from __future__ import annotations

from pathlib import Path

from dedoc.diagnosis.engine import RuleMatch, match_rules, resolve_platform
from dedoc.diagnosis.loader import load_diagnoses
from dedoc.evidence import MIN_SCORE_FOR_DIAGNOSIS, band_for_score, score_match
from dedoc.evidence.models import ConfidenceBand, EvidenceType
from dedoc.evidence.scoring import WEIGHTS
from dedoc.models.diagnosis import Diagnosis
from dedoc.parser.input_parser import parse_input


def test_band_thresholds() -> None:
    assert band_for_score(100) is ConfidenceBand.HIGH
    assert band_for_score(70) is ConfidenceBand.HIGH
    assert band_for_score(69) is ConfidenceBand.MEDIUM
    assert band_for_score(40) is ConfidenceBand.MEDIUM
    assert band_for_score(39) is ConfidenceBand.LOW
    assert band_for_score(0) is ConfidenceBand.LOW
    assert MIN_SCORE_FOR_DIAGNOSIS == 40


def test_weights_match_build_plan_section_10() -> None:
    assert WEIGHTS[EvidenceType.ERROR_SIGNATURE] == 40
    assert WEIGHTS[EvidenceType.PLATFORM_MATCH] == 20
    assert WEIGHTS[EvidenceType.STACKTRACE] == 20
    assert WEIGHTS[EvidenceType.CORRELATED_SIGNAL] == 15
    assert WEIGHTS[EvidenceType.SUPPORTING_METADATA] == 5


def _rule(**overrides: object) -> RuleMatch:
    diagnosis = load_diagnoses()["DEDOC-SCHEMA-001"]
    kwargs: dict[str, object] = {
        "diagnosis": diagnosis,
        "platform": "spark",
        "platform_match": True,
        "matched_signals": ["resolved_column_not_found"],
        "matched_exception_types": ["AnalysisException"],
        "exact_signals": ["resolved_column_not_found"],
        "has_stacktrace_evidence": True,
        "has_metadata": False,
        "excerpt": "line 4: AnalysisException: boom",
    }
    kwargs.update(overrides)
    return RuleMatch(**kwargs)  # type: ignore[arg-type]


def test_full_evidence_scores_high() -> None:
    bundle = score_match(
        _rule(has_metadata=True),  # exact 40 + platform 20 + stacktrace 20 + metadata 5
    )
    assert bundle.score == 85
    assert bundle.confidence_band is ConfidenceBand.HIGH
    types = [item.type for item in bundle.evidence]
    assert types.count(EvidenceType.PLATFORM_MATCH) == 1
    assert types.count(EvidenceType.STACKTRACE) == 1
    assert types.count(EvidenceType.SUPPORTING_METADATA) == 1


def test_exact_plus_correlated_plus_metadata_caps_at_100() -> None:
    bundle = score_match(
        _rule(
            matched_signals=["resolved_column_not_found", "stacktrace_present"],
            exact_signals=["resolved_column_not_found"],
            has_metadata=True,
        ),
    )  # 40 + 15 + 20 + 20 + 5 = 100
    assert bundle.score == 100
    assert bundle.confidence_band is ConfidenceBand.HIGH


def test_exact_signature_plus_platform_is_medium() -> None:
    bundle = score_match(
        _rule(matched_exception_types=[], has_stacktrace_evidence=False, platform_match=False),
    )
    assert bundle.score == 40  # exact signal alone
    assert bundle.confidence_band is ConfidenceBand.MEDIUM


def test_heuristic_signal_scores_correlated() -> None:
    bundle = score_match(
        _rule(
            matched_signals=["authentication_failure"],
            exact_signals=[],
            platform_match=True,
        )
    )
    # correlated 15 + stacktrace 20 + platform 20
    assert bundle.score == 55
    assert bundle.confidence_band is ConfidenceBand.MEDIUM
    assert all(item.type != EvidenceType.ERROR_SIGNATURE for item in bundle.evidence)


def test_exception_only_scores_low_without_platform() -> None:
    bundle = score_match(
        _rule(
            matched_signals=[],
            exact_signals=[],
            platform_match=False,
            has_stacktrace_evidence=False,
        )
    )
    assert bundle.score == 20
    assert bundle.confidence_band is ConfidenceBand.LOW


def test_score_capped_at_100() -> None:
    diagnosis = load_diagnoses()["DEDOC-SCHEMA-001"]
    rule = RuleMatch(
        diagnosis=diagnosis,
        platform="spark",
        platform_match=True,
        matched_signals=["resolved_column_not_found", "datatype_mismatch"],
        matched_exception_types=["AnalysisException"],
        exact_signals=["resolved_column_not_found", "datatype_mismatch"],
        has_stacktrace_evidence=True,
        has_metadata=True,
        excerpt=None,
    )
    assert score_match(rule).score == 100


def test_real_fixture_evidence_has_excerpt(fixtures_dir: Path) -> None:
    fixture = fixtures_dir / "positive" / "spark-schema-mismatch-resolved-column" / "input.log"
    events = parse_input(fixture)
    text = "\n".join(str(e.raw_payload) for e in events)
    platform = resolve_platform(events, text)
    (rule,) = match_rules(events, load_diagnoses(), platform)
    bundle = score_match(rule)
    assert any(item.excerpt for item in bundle.evidence)
    assert bundle.score >= 70
    assert bundle.confidence_band is ConfidenceBand.HIGH


def test_diagnosis_type_smoke() -> None:
    diagnosis: Diagnosis = load_diagnoses()["DEDOC-SCHEMA-001"]
    assert diagnosis.signals.positive
