"""Evaluation framework for Data Engineer Doctor (BUILD_PLAN.md §19).

Grades the deterministic pipeline against the curated ``fixtures/`` corpus and
reports accuracy, precision, recall, abstention quality, confidence
calibration, evidence coverage, unsupported-claim rate, remediation coverage
and regression rate. Run it with ``python -m dedoc.evaluation`` (``make evaluate``).
"""

from __future__ import annotations

from dedoc.evaluation.corpus import EvalCase, discover_cases
from dedoc.evaluation.harness import (
    CaseResult,
    EvaluationResult,
    Metrics,
    baseline_from_result,
    compute_metrics,
    evaluate_case,
    run_evaluation,
)
from dedoc.evaluation.report import render_json, render_text, to_dict

__all__ = [
    "CaseResult",
    "EvalCase",
    "EvaluationResult",
    "Metrics",
    "baseline_from_result",
    "compute_metrics",
    "discover_cases",
    "evaluate_case",
    "render_json",
    "render_text",
    "run_evaluation",
    "to_dict",
]
