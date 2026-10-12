"""Shared errors for the deterministic pipeline."""

from __future__ import annotations


class DEDocError(Exception):
    """Base class for expected, user-facing DEDoc errors."""


class InputError(DEDocError):
    """The input file could not be read or parsed."""


class DiagnosisLoadError(DEDocError):
    """Diagnosis knowledge could not be loaded or validated."""


class ToolError(DEDocError):
    """A tool call had invalid parameters or could not execute safely."""


class AgentConfigError(DEDocError):
    """The investigation agent configuration violates its hard bounds."""


class ProviderConfigError(DEDocError):
    """The AI provider configuration is invalid (unknown provider, bad bounds)."""


class ProviderError(DEDocError):
    """An AI provider could not complete an explanation request."""
