"""Evidence & confidence engine (BUILD_PLAN.md §10).

``models`` is imported eagerly; ``scoring`` is resolved lazily (PEP 562) because
it depends on ``dedoc.diagnosis.engine``, which itself reaches back through
``dedoc.models``. Eagerly importing it here would create an import cycle.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from dedoc.evidence.models import (
    SCORING_MODEL_VERSION,
    ConfidenceBand,
    Evidence,
    EvidenceBundle,
    EvidenceType,
)

if TYPE_CHECKING:  # pragma: no cover
    from dedoc.evidence.scoring import (
        MIN_SCORE_FOR_DIAGNOSIS,
        WEIGHTS,
        band_for_score,
        score_match,
    )

__all__ = [
    "MIN_SCORE_FOR_DIAGNOSIS",
    "SCORING_MODEL_VERSION",
    "WEIGHTS",
    "ConfidenceBand",
    "Evidence",
    "EvidenceBundle",
    "EvidenceType",
    "band_for_score",
    "score_match",
]

_LAZY_ATTRS = {
    "MIN_SCORE_FOR_DIAGNOSIS",
    "WEIGHTS",
    "band_for_score",
    "score_match",
}


def __getattr__(name: str) -> object:
    if name in _LAZY_ATTRS:
        import importlib

        module = importlib.import_module("dedoc.evidence.scoring")
        value = getattr(module, name)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(set(globals()) | _LAZY_ATTRS)
