"""Validate every diagnosis YAML: schema, signal registry, fixture references.

Run by ``make validate`` (BUILD_PLAN.md §18).
"""

from __future__ import annotations

import sys

from dedoc.analyzer.signals import SIGNAL_PATTERNS
from dedoc.core.errors import DiagnosisLoadError
from dedoc.core.paths import fixtures_root, resolve_diagnoses_path
from dedoc.diagnosis.loader import load_diagnoses
from dedoc.models.diagnosis import Diagnosis


def validate_diagnoses(diagnoses: dict[str, Diagnosis]) -> list[str]:
    """Return a list of problems (empty when valid)."""
    problems: list[str] = []
    for diagnosis in diagnoses.values():
        for signal in [*diagnosis.signals.positive, *diagnosis.signals.negative]:
            if signal not in SIGNAL_PATTERNS:
                problems.append(
                    f"{diagnosis.id}: signal {signal!r} has no extractor in "
                    "dedoc.analyzer.signals.SIGNAL_PATTERNS"
                )
        if not diagnosis.patterns.exception_types and not diagnosis.signals.positive:
            problems.append(
                f"{diagnosis.id}: must declare at least one exception type or positive signal"
            )
        if not diagnosis.hypotheses:
            problems.append(f"{diagnosis.id}: must declare at least one hypothesis")
    return problems


def validate_fixture_references(diagnoses: dict[str, Diagnosis]) -> list[str]:
    """Check that every fixture referenced by a diagnosis exists (when fixtures/ is present)."""
    root = fixtures_root()
    if not root.is_dir():
        return []
    problems: list[str] = []
    for diagnosis in diagnoses.values():
        for fixture in diagnosis.tests.fixtures:
            if not (root / fixture).is_dir():
                problems.append(f"{diagnosis.id}: unknown fixture reference {fixture!r}")
    return problems


def main() -> int:
    try:
        root = resolve_diagnoses_path()
        diagnoses = load_diagnoses(root)
    except DiagnosisLoadError as exc:
        print(f"diagnosis validation FAILED:\n{exc}", file=sys.stderr)
        return 1
    problems = validate_diagnoses(diagnoses) + validate_fixture_references(diagnoses)
    if problems:
        print("diagnosis validation FAILED:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1
    print(f"validated {len(diagnoses)} diagnosis definition(s) from {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
