"""Unit tests for the Diagnosis model (§6)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from dedoc.models.diagnosis import Diagnosis


def _base() -> dict[str, object]:
    return {
        "id": "DEDOC-TEST-001",
        "name": "Test Diagnosis",
        "category": "test.category",
        "platforms": ["spark"],
        "patterns": {"exception_types": ["AnalysisException"]},
        "signals": {"positive": ["datatype_mismatch"], "negative": ["dns_failure"]},
        "hypotheses": ["some_hypothesis"],
    }


def test_valid_diagnosis() -> None:
    diagnosis = Diagnosis.model_validate(_base())
    assert diagnosis.id == "DEDOC-TEST-001"
    assert diagnosis.severity.default.value == "medium"
    assert diagnosis.recommendations.immediate == []


@pytest.mark.parametrize(
    "bad_id", ["DED-TEST-001", "DEDOC-TEST-1", "dedoc-test-001", "DEDOC-TEST-0011"]
)
def test_invalid_ids_rejected(bad_id: str) -> None:
    data = _base()
    data["id"] = bad_id
    with pytest.raises(ValidationError):
        Diagnosis.model_validate(data)


def test_invalid_signal_name_rejected() -> None:
    data = _base()
    data["signals"] = {"positive": ["Not Snake Case"], "negative": []}
    with pytest.raises(ValidationError):
        Diagnosis.model_validate(data)


def test_empty_platforms_rejected() -> None:
    data = _base()
    data["platforms"] = []
    with pytest.raises(ValidationError):
        Diagnosis.model_validate(data)


def test_duplicate_platforms_rejected() -> None:
    data = _base()
    data["platforms"] = ["spark", "spark"]
    with pytest.raises(ValidationError):
        Diagnosis.model_validate(data)


def test_invalid_category_rejected() -> None:
    data = _base()
    data["category"] = "Schema Mismatch!"
    with pytest.raises(ValidationError):
        Diagnosis.model_validate(data)
