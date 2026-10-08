"""Canonical failure model (BUILD_PLAN.md §8)."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator

AttributeValue = str | int | float | bool


class EventSeverity(StrEnum):
    """Severity of a failure event, aligned with OpenTelemetry severity names."""

    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    FATAL = "FATAL"


class FailureEvent(BaseModel):
    """Canonical, vendor-neutral representation of a single failure event.

    Vendor-specific attributes are preserved separately in ``resource_attributes`` /
    ``event_attributes`` / ``raw_payload`` (BUILD_PLAN.md §8).
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    platform: str = "unknown"
    service: str | None = None
    job: str | None = None
    stage: str | None = None
    task: str | None = None
    severity: EventSeverity = EventSeverity.ERROR
    error_type: str | None = None
    error_message: str | None = None
    stacktrace: str | None = None
    source: str | None = None
    resource_attributes: dict[str, AttributeValue] = Field(default_factory=dict)
    event_attributes: dict[str, AttributeValue] = Field(default_factory=dict)
    raw_payload: Any = None

    @field_validator("timestamp", mode="before")
    @classmethod
    def _coerce_timestamp(cls, value: Any) -> Any:
        """Accept ISO-8601 strings and epoch seconds/milliseconds."""
        if isinstance(value, (int, float)):
            seconds = value / 1000.0 if value > 1e11 else float(value)
            return datetime.fromtimestamp(seconds, tz=UTC)
        return value
