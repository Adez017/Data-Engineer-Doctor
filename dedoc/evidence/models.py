"""Evidence & confidence models (BUILD_PLAN.md §10).

Confidence is derived from observable evidence and explicit weights — never
from an LLM's self-reported certainty. Weights are an initial implementation
hypothesis (§10) and must be versioned when changed.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

#: Version of the scoring model; bump whenever weights or bands change.
SCORING_MODEL_VERSION = "1"


class EvidenceType(StrEnum):
    ERROR_SIGNATURE = "error_signature"
    PLATFORM_MATCH = "platform_match"
    STACKTRACE = "stacktrace_evidence"
    CORRELATED_SIGNAL = "correlated_signal"
    SUPPORTING_METADATA = "supporting_metadata"


class ConfidenceBand(StrEnum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class Evidence(BaseModel):
    """One observable fact supporting a diagnosis."""

    type: EvidenceType
    weight: int
    description: str
    source: str
    excerpt: str | None = None


class EvidenceBundle(BaseModel):
    """Scored evidence for one matched diagnosis."""

    score: int = Field(ge=0, le=100)
    confidence_band: ConfidenceBand
    evidence: list[Evidence] = Field(default_factory=list)
