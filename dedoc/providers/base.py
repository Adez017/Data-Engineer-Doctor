"""Provider contracts and configuration (BUILD_PLAN.md §13).

``ProviderConfig`` must never contain a secret. API keys are read from the
process environment by the registry and live only inside a provider instance.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from dedoc.core.errors import ProviderConfigError

KNOWN_PROVIDERS = ("none", "openai", "openai_compatible", "azure_openai", "ollama", "anthropic")


def _normalize_provider(value: str) -> str:
    name = value.strip().lower()
    if name not in KNOWN_PROVIDERS:
        raise ProviderConfigError(
            f"unknown AI provider {value!r}; expected one of {', '.join(KNOWN_PROVIDERS)}"
        )
    return name


@dataclass(frozen=True)
class ProviderConfig:
    """Optional AI explanation configuration.

    Values map directly to provider capabilities; nothing here is a secret.
    """

    provider: str = "none"
    model: str | None = None
    base_url: str | None = None
    timeout_seconds: float = 30.0
    max_tokens: int = 500
    temperature: float = 0.0

    def __post_init__(self) -> None:
        object.__setattr__(self, "provider", _normalize_provider(self.provider))
        if self.timeout_seconds <= 0:
            raise ProviderConfigError("timeout_seconds must be > 0")
        if self.max_tokens < 1:
            raise ProviderConfigError("max_tokens must be >= 1")
        if not 0.0 <= self.temperature <= 2.0:
            raise ProviderConfigError("temperature must be in [0.0, 2.0]")


class AIProvider(Protocol):
    """An optional explanation provider behind the §13 interface.

    ``available()`` reports readiness (creds/base URL/model present). Only a
    provider that is available may be called. Implementations must never echo
    credentials into prompts, requests, or raised errors.
    """

    name: str
    model: str | None

    def available(self) -> bool: ...

    def explain(self, prompt: str) -> str:
        """Return a plain-text explanation for a redacted diagnostic prompt."""
        ...


__all__ = ["AIProvider", "KNOWN_PROVIDERS", "ProviderConfig"]
