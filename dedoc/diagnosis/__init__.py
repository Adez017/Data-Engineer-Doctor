"""Diagnosis knowledge package."""

from dedoc.diagnosis.engine import RuleMatch, match_rules, resolve_platform
from dedoc.diagnosis.loader import load_diagnoses

__all__ = ["RuleMatch", "load_diagnoses", "match_rules", "resolve_platform"]
