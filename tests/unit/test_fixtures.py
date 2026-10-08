"""Fixture validation: every fixture has well-formed, self-consistent metadata (§18)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from tests.conftest import iter_fixture_dirs, load_fixture_meta

VALID_KINDS = {"positive", "negative", "malformed"}
VALID_STATUSES = {"diagnosed", "insufficient_evidence", "input_error"}
VALID_BANDS = {"HIGH", "MEDIUM"}


def test_fixtures_exist(fixtures_dir: Path) -> None:
    dirs = iter_fixture_dirs(fixtures_dir)
    assert len(dirs) >= 8, f"expected at least 8 fixtures, found {len(dirs)}"


def test_every_fixture_has_valid_meta(fixtures_dir: Path) -> None:
    problems: list[str] = []
    for fixture_dir in iter_fixture_dirs(fixtures_dir):
        rel = fixture_dir.relative_to(fixtures_dir)
        meta_path = fixture_dir / "meta.yaml"
        if not meta_path.is_file():
            problems.append(f"{rel}: missing meta.yaml")
            continue
        try:
            meta: dict[str, Any] = load_fixture_meta(fixture_dir)
        except yaml.YAMLError as exc:
            problems.append(f"{rel}: invalid YAML: {exc}")
            continue
        for key in ("name", "kind", "description", "expected"):
            if key not in meta:
                problems.append(f"{rel}: missing key {key!r}")
        kind = meta.get("kind")
        expected = meta.get("expected", {})
        if kind not in VALID_KINDS:
            problems.append(f"{rel}: invalid kind {kind!r}")
        if not isinstance(expected, dict):
            problems.append(f"{rel}: expected must be a mapping")
            continue
        status = expected.get("status")
        exit_code = expected.get("exit_code")
        ids = expected.get("diagnosis_ids")
        if status not in VALID_STATUSES:
            problems.append(f"{rel}: invalid status {status!r}")
        if exit_code not in (0, 1):
            problems.append(f"{rel}: invalid exit_code {exit_code!r}")
        if not isinstance(ids, list):
            problems.append(f"{rel}: diagnosis_ids must be a list")
        elif any(not isinstance(i, str) or not i.startswith("DEDOC-") for i in ids):
            problems.append(f"{rel}: diagnosis_ids must be DEDOC-* strings")
        # kind/status consistency
        if kind == "positive" and (status != "diagnosed" or exit_code != 0 or not ids):
            problems.append(f"{rel}: positive fixtures require status=diagnosed, exit_code=0, ids")
        if kind == "positive":
            band = expected.get("confidence_band")
            if band not in VALID_BANDS:
                problems.append(
                    f"{rel}: positive fixtures require confidence_band HIGH|MEDIUM, got {band!r}"
                )
        if kind == "negative" and (status != "insufficient_evidence" or ids != []):
            problems.append(f"{rel}: negative fixtures require insufficient_evidence and no ids")
        if kind == "malformed":
            expected_exit = 1 if status == "input_error" else 0
            if exit_code != expected_exit or ids != []:
                problems.append(f"{rel}: malformed fixtures require matching exit_code and no ids")
    assert not problems, "\n".join(problems)


def test_fixture_inputs_exist(fixtures_dir: Path) -> None:
    problems: list[str] = []
    for fixture_dir in iter_fixture_dirs(fixtures_dir):
        inputs = sorted(fixture_dir.glob("input.*"))
        if len(inputs) != 1:
            problems.append(f"{fixture_dir.name}: expected exactly one input.* file")
    assert not problems, "\n".join(problems)


def test_diagnosis_fixture_references_exist(fixtures_dir: Path) -> None:
    from dedoc.diagnosis.loader import load_diagnoses

    problems: list[str] = []
    for diagnosis in load_diagnoses().values():
        for fixture in diagnosis.tests.fixtures:
            if not (fixtures_dir / fixture).is_dir():
                problems.append(f"{diagnosis.id}: unknown fixture {fixture!r}")
    assert not problems, "\n".join(problems)
