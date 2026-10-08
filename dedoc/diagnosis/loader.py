"""Load diagnosis definitions from YAML (§6, §9 step 4)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from dedoc.core.errors import DiagnosisLoadError
from dedoc.core.paths import resolve_diagnoses_path
from dedoc.models.diagnosis import Diagnosis


class _LoadFailure(Exception):
    def __init__(self, problems: list[str]) -> None:
        super().__init__("\n".join(problems))
        self.problems = problems


def _format_validation_error(exc: ValidationError) -> str:
    return "; ".join(
        f"{'.'.join(str(loc) for loc in err['loc'])}: {err['msg']}" for err in exc.errors()
    )


def _load_file(path: Path) -> Diagnosis:
    try:
        data: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise _LoadFailure([f"{path}: invalid YAML: {exc}"]) from exc
    except OSError as exc:
        raise _LoadFailure([f"{path}: cannot read file: {exc}"]) from exc
    if not isinstance(data, dict):
        raise _LoadFailure([f"{path}: top level must be a mapping"])
    try:
        return Diagnosis.model_validate(data)
    except ValidationError as exc:
        raise _LoadFailure([f"{path}: {_format_validation_error(exc)}"]) from exc


def load_diagnoses(path: str | Path | None = None) -> dict[str, Diagnosis]:
    """Load and validate every diagnosis YAML under the diagnoses directory.

    Returns:
        Mapping of diagnosis id -> Diagnosis, sorted by id.

    Raises:
        DiagnosisLoadError: if the directory is missing/empty or any file is invalid.
    """
    root = resolve_diagnoses_path(path)
    files = sorted([*root.rglob("*.yaml"), *root.rglob("*.yml")])
    if not files:
        raise DiagnosisLoadError(f"no diagnosis YAML files found under {root}")

    diagnoses: dict[str, Diagnosis] = {}
    problems: list[str] = []
    for file in files:
        try:
            diagnosis = _load_file(file)
        except _LoadFailure as exc:
            problems.extend(exc.problems)
            continue
        if diagnosis.id in diagnoses:
            problems.append(f"{file}: duplicate diagnosis id {diagnosis.id}")
            continue
        diagnoses[diagnosis.id] = diagnosis

    if problems:
        raise DiagnosisLoadError("failed to load diagnoses:\n" + "\n".join(problems))
    return dict(sorted(diagnoses.items()))
