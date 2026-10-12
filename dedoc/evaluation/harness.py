"""Evaluation harness: run the deterministic pipeline over the corpus and grade it.

Implements the §19 evaluation metrics:

* diagnosis accuracy / precision / recall,
* abstention quality (specificity),
* confidence calibration,
* evidence coverage and unsupported-claim rate,
* remediation coverage,
* regression rate against an optional baseline,
* tool efficiency (only meaningful once context-bearing cases exist).

No metric is derived from an LLM's self-reported certainty; every value is a
function of observable pipeline output compared with the fixture's expectation.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from dedoc import __version__
from dedoc.core.errors import InputError
from dedoc.core.pipeline import diagnose_file
from dedoc.diagnosis.loader import load_diagnoses
from dedoc.evaluation.corpus import EvalCase, discover_cases
from dedoc.evidence import MIN_SCORE_FOR_DIAGNOSIS
from dedoc.models.diagnosis import Diagnosis

__all__ = [
    "CaseResult",
    "EvaluationResult",
    "Metrics",
    "compute_metrics",
    "evaluate_case",
    "run_evaluation",
]

_INPUT_ERROR = "input_error"
_DIAGNOSED = "diagnosed"


@dataclass
class CaseResult:
    """Predicted outcome for one case, graded against its expectation."""

    case: EvalCase
    predicted_status: str
    matched_ids: list[str]
    top_confidence_band: str | None
    top_score: int | None
    has_evidence: bool
    has_remediation: bool
    notes: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.notes

    @property
    def diagnosed(self) -> bool:
        return self.predicted_status == _DIAGNOSED


def evaluate_case(
    case: EvalCase,
    *,
    diagnoses: Mapping[str, Diagnosis] | None = None,
) -> CaseResult:
    """Run the pipeline on one case and grade the result."""
    matched_ids: list[str] = []
    top_band: str | None = None
    top_score: int | None = None
    has_evidence = False
    has_remediation = False
    try:
        report = diagnose_file(case.input_path, diagnoses=diagnoses)
    except InputError:
        predicted_status = _INPUT_ERROR
    else:
        predicted_status = str(report.status)
        matched_ids = [match.id for match in report.matches]
        if report.matches:
            top = report.matches[0]
            top_score = top.score
            has_evidence = bool(top.evidence)
            has_remediation = bool(
                top.recommendations.immediate
                or top.recommendations.recommended
                or top.recommendations.prevention
            )
        top_band = report.top_confidence_band.value if report.top_confidence_band else None

    notes: list[str] = []
    expected_ids = list(case.expected_diagnosis_ids)
    if predicted_status != case.expected_status:
        notes.append(f"status {predicted_status!r} != expected {case.expected_status!r}")
    if matched_ids != expected_ids:
        notes.append(f"matches {matched_ids} != expected {expected_ids}")
    if case.expected_confidence_band is not None and top_band != case.expected_confidence_band:
        notes.append(f"band {top_band!r} != expected {case.expected_confidence_band!r}")

    return CaseResult(
        case=case,
        predicted_status=predicted_status,
        matched_ids=matched_ids,
        top_confidence_band=top_band,
        top_score=top_score,
        has_evidence=has_evidence,
        has_remediation=has_remediation,
        notes=notes,
    )


@dataclass
class Metrics:
    """Aggregate §19 metrics over the corpus (``None`` means not applicable)."""

    total: int
    passed: int
    positive: int
    negative: int
    malformed: int
    accuracy: float | None
    precision: float | None
    recall: float | None
    abstention_quality: float | None
    confidence_calibration: float | None
    evidence_coverage: float | None
    unsupported_claim_rate: float | None
    remediation_coverage: float | None
    regression_rate: float | None
    tool_efficiency: float | None


def _ratio(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def _is_regression(by_name: dict[str, CaseResult], name: str) -> bool:
    """A previously passing case that is now missing or failing."""
    result = by_name.get(name)
    return result is None or not result.ok


def compute_metrics(
    results: list[CaseResult],
    *,
    baseline: dict[str, bool] | None = None,
) -> Metrics:
    """Compute aggregate metrics from graded case results."""
    total = len(results)
    passed = sum(1 for r in results if r.ok)
    positive = [r for r in results if r.case.kind == "positive"]
    negative = [r for r in results if r.case.kind == "negative"]
    malformed = [r for r in results if r.case.kind == "malformed"]

    correctly_diagnosed = sum(1 for r in positive if r.diagnosed and not r.notes)
    emitted = [r for r in results if r.diagnosed]
    correctly_emitted = sum(1 for r in emitted if not r.notes)

    abstain_cases = [r for r in results if r.case.expects_abstention or r.case.expects_input_error]
    correct_abstentions = sum(1 for r in abstain_cases if not r.notes)

    band_cases = [r for r in positive if r.case.expected_confidence_band is not None]
    correct_bands = sum(
        1 for r in band_cases if r.top_confidence_band == r.case.expected_confidence_band
    )

    evidence_ok = sum(1 for r in emitted if r.has_evidence)
    remediation_ok = sum(1 for r in emitted if r.has_remediation)
    unsupported = sum(
        1
        for r in emitted
        if not r.has_evidence or (r.top_score is not None and r.top_score < MIN_SCORE_FOR_DIAGNOSIS)
    )

    regression_rate: float | None = None
    if baseline:
        by_name = {r.case.name: r for r in results}
        baseline_passed = [name for name, ok in baseline.items() if ok]
        regressions = sum(1 for name in baseline_passed if _is_regression(by_name, name))
        regression_rate = _ratio(regressions, len(baseline_passed))

    return Metrics(
        total=total,
        passed=passed,
        positive=len(positive),
        negative=len(negative),
        malformed=len(malformed),
        accuracy=_ratio(passed, total),
        precision=_ratio(correctly_emitted, len(emitted)),
        recall=_ratio(correctly_diagnosed, len(positive)),
        abstention_quality=_ratio(correct_abstentions, len(abstain_cases)),
        confidence_calibration=_ratio(correct_bands, len(band_cases)),
        evidence_coverage=_ratio(evidence_ok, len(emitted)),
        unsupported_claim_rate=_ratio(unsupported, len(emitted)),
        remediation_coverage=_ratio(remediation_ok, len(emitted)),
        regression_rate=regression_rate,
        tool_efficiency=None,
    )


@dataclass
class EvaluationResult:
    """Full evaluation output: graded cases, metrics, and regressions."""

    corpus_dir: str
    dedoc_version: str
    results: list[CaseResult]
    metrics: Metrics
    regressions: list[str]
    baseline_path: str | None

    @property
    def ok(self) -> bool:
        return all(result.ok for result in self.results)


class _Missing:
    """Sentinel evaluated as a failing (not-ok) case."""

    ok = False


_MISSING = _Missing()


def run_evaluation(
    corpus_dir: str | Path,
    *,
    diagnoses_path: str | Path | None = None,
    baseline: dict[str, bool] | None = None,
    baseline_path: str | None = None,
) -> EvaluationResult:
    """Run the pipeline over every case under ``corpus_dir`` and grade it."""
    cases = discover_cases(corpus_dir)
    loaded = load_diagnoses(diagnoses_path)
    results = [evaluate_case(case, diagnoses=loaded) for case in cases]
    metrics = compute_metrics(results, baseline=baseline)
    regressions: list[str] = []
    if baseline:
        by_name = {r.case.name: r for r in results}
        regressions = [
            name for name, ok in baseline.items() if ok and _is_regression(by_name, name)
        ]
    return EvaluationResult(
        corpus_dir=str(corpus_dir),
        dedoc_version=__version__,
        results=results,
        metrics=metrics,
        regressions=regressions,
        baseline_path=baseline_path,
    )


def baseline_from_result(result: EvaluationResult) -> dict[str, Any]:
    """Serialise a result into a regression baseline (``{name: ok}``)."""
    return {r.case.name: r.ok for r in result.results}
