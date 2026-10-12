"""AI provider layer (BUILD_PLAN.md §13): optional explanation providers.

The deterministic engine never depends on this package. Providers are only
constructed when a user explicitly opts in via ``ProviderConfig`` or the
``DEDOC_AI_PROVIDER`` environment variable, and they never receive an API key
through a CLI argument or a report.
"""

from __future__ import annotations

from dedoc.providers.base import AIProvider, ProviderConfig
from dedoc.providers.registry import (
    build_provider,
    provider_config_from_env,
)

__all__ = [
    "AIProvider",
    "ProviderConfig",
    "build_provider",
    "provider_config_from_env",
]
