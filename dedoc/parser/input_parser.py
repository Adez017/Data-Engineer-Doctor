"""Input normalization: TXT / JSON / JSONL files -> FailureEvent list (§9 step 1)."""

from __future__ import annotations

import json
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from dedoc.core.errors import InputError
from dedoc.models.failure import FailureEvent

#: Bound input size to keep runtime and memory predictable (untrusted input).
MAX_INPUT_BYTES = 10 * 1024 * 1024


class InputFormat(StrEnum):
    AUTO = "auto"
    TEXT = "text"
    JSON = "json"
    JSONL = "jsonl"


#: Alias groups for common vendor/JSON key spellings -> canonical field names.
_ALIAS_GROUPS: dict[str, tuple[str, ...]] = {
    "error_type": ("error_type", "errorType", "exception_type", "exceptionType", "error_class"),
    "error_message": ("error_message", "errorMessage", "message", "msg"),
    "stacktrace": ("stacktrace", "stackTrace", "stack_trace", "traceback"),
    "resource_attributes": ("resource_attributes", "resourceAttributes"),
    "event_attributes": ("event_attributes", "eventAttributes"),
}

_DIRECT_FIELDS = (
    "id",
    "timestamp",
    "platform",
    "service",
    "job",
    "stage",
    "task",
    "severity",
    "source",
)

_STACKTRACE_LINE_MARKERS = ("\tat ", "    at ", "Traceback (most recent call last)", "Caused by:")


def _read_text(path: Path) -> str:
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise InputError(f"cannot read input file: {path}: {exc}") from exc
    if size > MAX_INPUT_BYTES:
        raise InputError(
            f"input file exceeds the {MAX_INPUT_BYTES // (1024 * 1024)} MiB limit: {path}"
        )
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise InputError(f"cannot read input file: {path}: {exc}") from exc
    # Untrusted input must never crash the tool: decode tolerantly.
    return raw.decode("utf-8", errors="replace")


def detect_format(path: Path) -> InputFormat:
    suffix = path.suffix.lower()
    if suffix == ".json":
        return InputFormat.JSON
    if suffix in {".jsonl", ".ndjson"}:
        return InputFormat.JSONL
    return InputFormat.TEXT


def _event_from_dict(data: dict[str, Any], source: str) -> FailureEvent:
    mapped: dict[str, Any] = {}
    for field, aliases in _ALIAS_GROUPS.items():
        for alias in aliases:
            value = data.get(alias)
            if value is not None and value != "":
                mapped[field] = value
                break
    for field in _DIRECT_FIELDS:
        if field in data and data[field] is not None:
            mapped[field] = data[field]
    if isinstance(mapped.get("severity"), str):
        mapped["severity"] = mapped["severity"].upper()
    mapped["source"] = mapped.get("source") or source
    mapped["raw_payload"] = data
    try:
        return FailureEvent.model_validate(mapped)
    except ValidationError as exc:
        detail = "; ".join(
            f"{'.'.join(str(loc) for loc in err['loc'])}: {err['msg']}" for err in exc.errors()
        )
        raise InputError(f"invalid event in {source}: {detail}") from exc


def _events_from_json(text: str, source: str) -> list[FailureEvent]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise InputError(f"invalid JSON in {source}: {exc}") from exc
    if isinstance(data, dict):
        return [_event_from_dict(data, source)]
    if isinstance(data, list):
        events = []
        for index, item in enumerate(data):
            if not isinstance(item, dict):
                raise InputError(f"invalid JSON in {source}: item {index} is not an object")
            events.append(_event_from_dict(item, source))
        return events
    raise InputError(f"invalid JSON in {source}: expected an object or an array of objects")


def _events_from_jsonl(text: str, source: str) -> list[FailureEvent]:
    events: list[FailureEvent] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            data = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise InputError(f"invalid JSON on line {line_no} of {source}: {exc}") from exc
        if not isinstance(data, dict):
            raise InputError(f"invalid JSON on line {line_no} of {source}: expected an object")
        events.append(_event_from_dict(data, source))
    return events


def _event_from_text(text: str, source: str) -> FailureEvent:
    lines = text.splitlines()
    first_next = next((line.strip() for line in lines if line.strip()), "")
    stack_lines = [
        line for line in lines if any(line.startswith(m) for m in _STACKTRACE_LINE_MARKERS)
    ]
    return FailureEvent(
        platform="unknown",
        error_message=first_next or None,
        stacktrace="\n".join(stack_lines) if stack_lines else None,
        source=source,
        raw_payload=text,
    )


def parse_input(path: Path, input_format: InputFormat = InputFormat.AUTO) -> list[FailureEvent]:
    """Parse an input file into canonical failure events.

    Raises:
        InputError: if the file is missing, too large, or malformed.
    """
    if not path.exists():
        raise InputError(f"input file not found: {path}")
    if not path.is_file():
        raise InputError(f"not a file: {path}")
    text = _read_text(path)
    fmt = detect_format(path) if input_format is InputFormat.AUTO else input_format
    source = str(path)
    if fmt is InputFormat.JSON:
        return _events_from_json(text, source)
    if fmt is InputFormat.JSONL:
        return _events_from_jsonl(text, source)
    if not text.strip():
        return []
    return [_event_from_text(text, source)]
