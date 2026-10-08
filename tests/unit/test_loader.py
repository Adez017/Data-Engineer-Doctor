"""Unit tests for the diagnosis YAML loader."""

from __future__ import annotations

from pathlib import Path

import pytest

from dedoc.core.errors import DiagnosisLoadError
from dedoc.diagnosis.loader import load_diagnoses

VALID_YAML = """
id: DEDOC-TEST-001
name: Test
category: test.category
platforms: [spark]
patterns:
  exception_types: [AnalysisException]
signals:
  positive: [datatype_mismatch]
hypotheses: [h]
"""


def _write(tmp_path: Path, name: str, content: str) -> Path:
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return path


def test_loads_real_diagnoses() -> None:
    diagnoses = load_diagnoses()
    assert "DEDOC-SCHEMA-001" in diagnoses
    diagnosis = diagnoses["DEDOC-SCHEMA-001"]
    assert diagnosis.platforms == ["spark", "databricks"]
    assert "resolved_column_not_found" in diagnosis.signals.positive
    assert diagnosis.tests.fixtures


def test_loads_from_explicit_path(tmp_path: Path) -> None:
    _write(tmp_path, "d.yaml", VALID_YAML)
    diagnoses = load_diagnoses(tmp_path)
    assert list(diagnoses) == ["DEDOC-TEST-001"]


def test_env_var_override(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write(tmp_path, "d.yaml", VALID_YAML)
    monkeypatch.setenv("DEDOC_DIAGNOSES_PATH", str(tmp_path))
    diagnoses = load_diagnoses()
    assert list(diagnoses) == ["DEDOC-TEST-001"]


def test_invalid_yaml_rejected(tmp_path: Path) -> None:
    _write(tmp_path, "bad.yaml", "id: [unclosed")
    with pytest.raises(DiagnosisLoadError, match="invalid YAML"):
        load_diagnoses(tmp_path)


def test_schema_violation_rejected(tmp_path: Path) -> None:
    _write(tmp_path, "bad.yaml", "id: not-a-valid-id\nname: x\ncategory: c\nplatforms: [spark]\n")
    with pytest.raises(DiagnosisLoadError, match="failed to load diagnoses"):
        load_diagnoses(tmp_path)


def test_duplicate_id_rejected(tmp_path: Path) -> None:
    _write(tmp_path, "a.yaml", VALID_YAML)
    _write(tmp_path, "b.yaml", VALID_YAML)
    with pytest.raises(DiagnosisLoadError, match="duplicate diagnosis id"):
        load_diagnoses(tmp_path)


def test_empty_directory_rejected(tmp_path: Path) -> None:
    with pytest.raises(DiagnosisLoadError, match="no diagnosis YAML files"):
        load_diagnoses(tmp_path)
