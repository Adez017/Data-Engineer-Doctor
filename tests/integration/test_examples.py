"""The runnable examples in `examples/` must keep producing their documented output.

`examples/` is a convenience surface (see `examples/README.md`); the graded corpus
lives in `fixtures/`. This test keeps the two from drifting apart.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from dedoc.core.pipeline import diagnose_file

EXAMPLES_DIR = Path(__file__).resolve().parents[2] / "examples" / "logs"

#: input filename -> (platform, status, expected top match id or None)
EXPECTED: dict[str, tuple[str, str, str | None]] = {
    "spark-executor-oom.log": ("spark", "diagnosed", "DEDOC-SPARK-001"),
    "delta-concurrent-write.log": ("spark", "diagnosed", "DEDOC-DELTA-001"),
    "schema-missing-column.json": ("spark", "diagnosed", "DEDOC-SCHEMA-001"),
    "adf-linked-service.json": ("adf", "diagnosed", "DEDOC-ADF-001"),
    "no-signal-app.log": ("unknown", "insufficient_evidence", None),
}


def test_examples_dir_is_populated() -> None:
    names = {path.name for path in EXAMPLES_DIR.glob("*") if path.is_file()}
    assert set(EXPECTED) <= names, f"missing examples: {set(EXPECTED) - names}"


@pytest.mark.parametrize("name", sorted(EXPECTED))
def test_example_output_is_stable(name: str) -> None:
    platform, status, top_id = EXPECTED[name]
    report = diagnose_file(EXAMPLES_DIR / name)
    assert report.platform == platform
    assert report.status.value == status
    matches = [m.id for m in report.matches]
    if top_id is None:
        assert matches == []
    else:
        assert matches[:1] == [top_id]
