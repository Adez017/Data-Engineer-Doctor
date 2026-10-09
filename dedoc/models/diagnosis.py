"""Diagnosis knowledge model (BUILD_PLAN.md §6)."""

from __future__ import annotations

import re
from enum import StrEnum

from pydantic import BaseModel, Field, field_validator

#: Public diagnosis IDs are a stable API (BUILD_PLAN.md §5): DEDOC-<CATEGORY>-<NNN>
DIAGNOSIS_ID_PATTERN = re.compile(r"^DEDOC-[A-Z0-9]+-\d{3}$")
SIGNAL_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")
CATEGORY_PATTERN = re.compile(r"^[a-z0-9]+(\.[a-z0-9_]+)*$")
PLATFORM_PATTERN = re.compile(r"^[a-z][a-z0-9_-]*$")


class DiagnosisSeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


#: Ascending rank used to break score ties (critical first).
_SEVERITY_RANK: dict[DiagnosisSeverity, int] = {
    DiagnosisSeverity.CRITICAL: 0,
    DiagnosisSeverity.HIGH: 1,
    DiagnosisSeverity.MEDIUM: 2,
    DiagnosisSeverity.LOW: 3,
}


def severity_rank(severity: DiagnosisSeverity) -> int:
    """Return a sort rank for a severity (critical=0 ... low=3)."""
    return _SEVERITY_RANK[severity]


class SeveritySpec(BaseModel):
    default: DiagnosisSeverity = DiagnosisSeverity.MEDIUM


class Patterns(BaseModel):
    """Deterministic match patterns for a diagnosis."""

    exception_types: list[str] = Field(default_factory=list)


class Signals(BaseModel):
    """Named signals. Positive signals support the diagnosis; negative signals
    are contradictory evidence and disqualify it (BUILD_PLAN.md §6)."""

    positive: list[str] = Field(default_factory=list)
    negative: list[str] = Field(default_factory=list)

    @field_validator("positive", "negative")
    @classmethod
    def _valid_signal_names(cls, value: list[str]) -> list[str]:
        for name in value:
            if not SIGNAL_NAME_PATTERN.match(name):
                raise ValueError(f"invalid signal name: {name!r} (expected snake_case)")
        if len(set(value)) != len(value):
            raise ValueError("duplicate signal names are not allowed")
        return value


class Recommendations(BaseModel):
    immediate: list[str] = Field(default_factory=list)
    recommended: list[str] = Field(default_factory=list)
    prevention: list[str] = Field(default_factory=list)


class Reference(BaseModel):
    source: str
    url: str


class TestSpec(BaseModel):
    fixtures: list[str] = Field(default_factory=list)


class Diagnosis(BaseModel):
    """Machine-readable diagnosis definition loaded from YAML."""

    id: str
    name: str
    category: str
    severity: SeveritySpec = Field(default_factory=SeveritySpec)
    platforms: list[str]
    patterns: Patterns = Field(default_factory=Patterns)
    signals: Signals = Field(default_factory=Signals)
    hypotheses: list[str] = Field(default_factory=list)
    recommendations: Recommendations = Field(default_factory=Recommendations)
    references: list[Reference] = Field(default_factory=list)
    tests: TestSpec = Field(default_factory=TestSpec)

    @field_validator("id")
    @classmethod
    def _valid_id(cls, value: str) -> str:
        if not DIAGNOSIS_ID_PATTERN.match(value):
            raise ValueError(f"invalid diagnosis id: {value!r} (expected DEDOC-<CATEGORY>-<NNN>)")
        return value

    @field_validator("category")
    @classmethod
    def _valid_category(cls, value: str) -> str:
        if not CATEGORY_PATTERN.match(value):
            raise ValueError(f"invalid category: {value!r} (expected dotted lowercase)")
        return value

    @field_validator("platforms")
    @classmethod
    def _valid_platforms(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("at least one platform is required")
        for name in value:
            if not PLATFORM_PATTERN.match(name):
                raise ValueError(f"invalid platform name: {name!r}")
        if len(set(value)) != len(value):
            raise ValueError("duplicate platforms are not allowed")
        return value
