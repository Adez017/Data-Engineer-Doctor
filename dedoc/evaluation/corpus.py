"""Evaluation corpus discovery (BUILD_PLAN.md §19).

The corpus is the ``fixtures/`` tree: every directory that contains an
``input.*`` file and a ``meta.yaml`` describes one evaluation case with its
expected outcome (status, exit code, diagnosis ids, confidence band).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

__all__ = ["EvalCase", "discover_cases"]


@dataclass(frozen=True)
class EvalCase:
    """One graded case from the evaluation corpus."""

    name: str
    kind: str
    label: str
    input_path: Path
    expected_status: str
    expected_exit_code: int
    expected_diagnosis_ids: tuple[str, ...]
    expected_confidence_band: str | None
    description: str = ""

    @property
    def expects_input_error(self) -> bool:
        """True when the case must fail cleanly with a non-zero exit code."""
        return self.expected_exit_code != 0

    @property
    def expects_abstention(self) -> bool:
        """True when the case must abstain with no diagnosis (specificity)."""
        return not self.expects_input_error and not self.expected_diagnosis_ids


def _require_mapping(value: Any, where: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{where} must be a mapping")
    return value


def _first_input(directory: Path) -> Path:
    inputs = sorted(path for path in directory.glob("input.*") if path.is_file())
    if not inputs:
        raise ValueError(f"no input.* file in {directory}")
    return inputs[0]


def _case_from_dir(directory: Path, root: Path) -> EvalCase:
    meta_path = directory / "meta.yaml"
    meta = _require_mapping(yaml.safe_load(meta_path.read_text(encoding="utf-8")), str(meta_path))
    expected = _require_mapping(meta.get("expected", {}), f"{meta_path}: expected")
    raw_ids = expected.get("diagnosis_ids", [])
    if not isinstance(raw_ids, list):
        raise ValueError(f"{meta_path}: expected.diagnosis_ids must be a list")
    band = expected.get("confidence_band")
    return EvalCase(
        name=str(meta.get("name", directory.name)),
        kind=str(meta.get("kind", directory.parent.name)),
        label=str(directory.relative_to(root)),
        input_path=_first_input(directory),
        expected_status=str(expected["status"]),
        expected_exit_code=int(expected["exit_code"]),
        expected_diagnosis_ids=tuple(str(i) for i in raw_ids),
        expected_confidence_band=str(band) if band is not None else None,
        description=str(meta.get("description", "")),
    )


def discover_cases(corpus_dir: str | Path) -> list[EvalCase]:
    """Return every evaluation case found under ``corpus_dir``, sorted by label."""
    root = Path(corpus_dir)
    if not root.is_dir():
        raise ValueError(f"corpus directory not found: {root}")
    cases = [_case_from_dir(meta.parent, root) for meta in sorted(root.rglob("meta.yaml"))]
    if not cases:
        raise ValueError(f"no evaluation cases found under {root}")
    return cases
