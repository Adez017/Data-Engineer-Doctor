"""Evaluation framework tests (§19): discovery, grading, metrics, CLI, baseline."""

from __future__ import annotations

import json
from pathlib import Path

from dedoc.evaluation import (
    baseline_from_result,
    discover_cases,
    evaluate_case,
    render_json,
    render_text,
    run_evaluation,
)
from dedoc.evaluation.__main__ import main
from tests.conftest import iter_fixture_dirs, load_fixture_meta


def _expected_kind_counts(fixtures_dir: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    for fixture_dir in iter_fixture_dirs(fixtures_dir):
        kind = str(load_fixture_meta(fixture_dir).get("kind", ""))
        counts[kind] = counts.get(kind, 0) + 1
    return counts


def test_discover_cases_matches_fixtures(fixtures_dir: Path) -> None:
    cases = discover_cases(fixtures_dir)
    expected = _expected_kind_counts(fixtures_dir)
    assert len(cases) == len(iter_fixture_dirs(fixtures_dir))
    assert len(cases) == sum(expected.values())
    kinds = [case.kind for case in cases]
    for kind, count in expected.items():
        assert kinds.count(kind) == count
    assert cases


def test_full_corpus_passes_with_expected_metrics(fixtures_dir: Path) -> None:
    result = run_evaluation(fixtures_dir)
    total = len(iter_fixture_dirs(fixtures_dir))
    assert result.ok, [r.notes for r in result.results if not r.ok]
    metrics = result.metrics
    assert metrics.total == total
    assert metrics.passed == total
    assert metrics.accuracy == 1.0
    assert metrics.precision == 1.0
    assert metrics.recall == 1.0
    assert metrics.abstention_quality == 1.0
    assert metrics.confidence_calibration == 1.0
    assert metrics.evidence_coverage == 1.0
    assert metrics.remediation_coverage == 1.0
    assert metrics.unsupported_claim_rate == 0.0


def test_evaluate_case_reports_mismatches(fixtures_dir: Path) -> None:
    case = next(c for c in discover_cases(fixtures_dir) if c.name == "empty-file")
    graded = evaluate_case(case)
    assert graded.ok
    assert graded.predicted_status == "insufficient_evidence"
    assert graded.matched_ids == []


def test_regression_rate_against_baseline(fixtures_dir: Path) -> None:
    baseline = {"does-not-exist": True}
    result = run_evaluation(fixtures_dir, baseline=baseline, baseline_path="x.json")
    assert result.regressions == ["does-not-exist"]
    assert result.metrics.regression_rate == 1.0


def test_baseline_from_result_roundtrip(fixtures_dir: Path) -> None:
    result = run_evaluation(fixtures_dir)
    baseline = baseline_from_result(result)
    assert baseline == {r.case.name: True for r in result.results}
    assert run_evaluation(fixtures_dir, baseline=baseline).metrics.regression_rate == 0.0


def test_render_text_and_json(fixtures_dir: Path) -> None:
    result = run_evaluation(fixtures_dir)
    text = render_text(result)
    total = result.metrics.total
    assert "Evaluation" in text
    assert "Diagnosis accuracy" in text
    assert f"{total}/{total} passed" in text
    payload = json.loads(render_json(result))
    assert payload["ok"] is True
    assert payload["metrics"]["accuracy"] == 1.0
    assert len(payload["cases"]) == total


def test_main_strict_passes(fixtures_dir: Path) -> None:
    assert main(["--corpus", str(fixtures_dir), "--strict"]) == 0


def test_main_strict_flags_regression(fixtures_dir: Path, tmp_path: Path) -> None:
    baseline = tmp_path / "baseline.json"
    baseline.write_text(json.dumps({"ghost-case": True}), encoding="utf-8")
    assert main(["--corpus", str(fixtures_dir), "--baseline", str(baseline), "--strict"]) == 1


def test_main_missing_corpus(tmp_path: Path) -> None:
    assert main(["--corpus", str(tmp_path / "nope")]) == 2
