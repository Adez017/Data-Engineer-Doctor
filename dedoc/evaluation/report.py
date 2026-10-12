"""Render evaluation results as human-readable text or machine-readable JSON."""

from __future__ import annotations

import json
import os
from typing import Any

from dedoc.core.paths import repo_root
from dedoc.evaluation.harness import EvaluationResult, Metrics

__all__ = ["render_json", "render_text", "to_dict"]


def _display_path(raw: str | None) -> str | None:
    """Relativise a path to the repository root when possible (portable output)."""
    if raw is None:
        return None
    root = repo_root()
    try:
        return os.path.relpath(raw, root)
    except ValueError:
        return raw


def _fmt(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.3f}"


def _metric_rows(metrics: Metrics) -> list[tuple[str, float | None]]:
    return [
        ("Diagnosis accuracy", metrics.accuracy),
        ("Precision", metrics.precision),
        ("Recall", metrics.recall),
        ("Abstention quality", metrics.abstention_quality),
        ("Confidence calibration", metrics.confidence_calibration),
        ("Evidence coverage", metrics.evidence_coverage),
        ("Unsupported-claim rate", metrics.unsupported_claim_rate),
        ("Remediation coverage", metrics.remediation_coverage),
        ("Regression rate", metrics.regression_rate),
        ("Tool efficiency", metrics.tool_efficiency),
    ]


def render_text(result: EvaluationResult) -> str:
    """Render a conclusion-first human report of the evaluation run."""
    m = result.metrics
    lines: list[str] = []
    lines.append("Data Engineer Doctor — Evaluation")
    lines.append(f"DEDoc {result.dedoc_version} | corpus: {_display_path(result.corpus_dir)}")
    lines.append(
        f"Cases: {m.total} ({m.positive} positive, {m.negative} negative, {m.malformed} malformed)"
    )
    lines.append(f"Result: {m.passed}/{m.total} passed")
    lines.append("")
    lines.append("Metrics")
    for label, value in _metric_rows(m):
        lines.append(f"  {label:<24} {_fmt(value)}")
    if result.baseline_path:
        lines.append(f"  (regression baseline: {result.baseline_path})")
    failures = [r for r in result.results if not r.ok]
    lines.append("")
    if not failures:
        lines.append("No failures.")
        return "\n".join(lines)
    lines.append(f"Failures ({len(failures)}):")
    for r in failures:
        lines.append(f"  - {r.case.label} [{r.case.kind}]")
        for note in r.notes:
            lines.append(f"      {note}")
    return "\n".join(lines)


def to_dict(result: EvaluationResult) -> dict[str, Any]:
    """Serialise an evaluation result to a JSON-compatible mapping."""
    m = result.metrics
    return {
        "dedoc_version": result.dedoc_version,
        "corpus": _display_path(result.corpus_dir),
        "ok": result.ok,
        "metrics": {
            "total": m.total,
            "passed": m.passed,
            "positive": m.positive,
            "negative": m.negative,
            "malformed": m.malformed,
            "accuracy": m.accuracy,
            "precision": m.precision,
            "recall": m.recall,
            "abstention_quality": m.abstention_quality,
            "confidence_calibration": m.confidence_calibration,
            "evidence_coverage": m.evidence_coverage,
            "unsupported_claim_rate": m.unsupported_claim_rate,
            "remediation_coverage": m.remediation_coverage,
            "regression_rate": m.regression_rate,
            "tool_efficiency": m.tool_efficiency,
        },
        "baseline": _display_path(result.baseline_path),
        "regressions": result.regressions,
        "cases": [
            {
                "name": r.case.name,
                "kind": r.case.kind,
                "label": r.case.label,
                "ok": r.ok,
                "expected_status": r.case.expected_status,
                "predicted_status": r.predicted_status,
                "expected_diagnosis_ids": list(r.case.expected_diagnosis_ids),
                "matched_ids": r.matched_ids,
                "top_confidence_band": r.top_confidence_band,
                "top_score": r.top_score,
                "has_evidence": r.has_evidence,
                "has_remediation": r.has_remediation,
                "notes": r.notes,
            }
            for r in result.results
        ],
    }


def render_json(result: EvaluationResult) -> str:
    """Render the evaluation result as indented JSON."""
    return json.dumps(to_dict(result), indent=2, sort_keys=False)
