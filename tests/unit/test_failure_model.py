"""Unit tests for the canonical FailureEvent model (§8)."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from dedoc.models.failure import EventSeverity, FailureEvent


def test_defaults() -> None:
    event = FailureEvent()
    assert event.id
    assert event.platform == "unknown"
    assert event.severity is EventSeverity.ERROR
    assert event.timestamp.tzinfo is not None
    assert event.resource_attributes == {}


def test_epoch_millisecond_timestamp() -> None:
    event = FailureEvent(timestamp=1728390896000)
    assert event.timestamp.year == 2024
    assert event.timestamp.tzinfo is not None


def test_epoch_second_timestamp() -> None:
    event = FailureEvent(timestamp=1728390896)
    assert event.timestamp.year == 2024


def test_iso_timestamp() -> None:
    event = FailureEvent(timestamp="2024-10-08T12:34:56Z")
    assert event.timestamp == datetime(2024, 10, 8, 12, 34, 56, tzinfo=UTC)


def test_invalid_severity_rejected() -> None:
    with pytest.raises(ValidationError):
        FailureEvent(severity="CATASTROPHIC")
