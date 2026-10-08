"""Diagnosis knowledge package."""

from dedoc.diagnosis.engine import match_diagnoses, resolve_platform
from dedoc.diagnosis.loader import load_diagnoses

__all__ = ["load_diagnoses", "match_diagnoses", "resolve_platform"]
