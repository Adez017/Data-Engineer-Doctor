"""Shared errors for the deterministic pipeline."""

from __future__ import annotations


class DEDocError(Exception):
    """Base class for expected, user-facing DEDoc errors."""


class InputError(DEDocError):
    """The input file could not be read or parsed."""


class DiagnosisLoadError(DEDocError):
    """Diagnosis knowledge could not be loaded or validated."""
