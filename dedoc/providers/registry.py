"""Provider factory and environment wiring (BUILD_PLAN.md §13).

API keys are read from the process environment only — never from a CLI
argument, a config file, or a report. ``ProviderConfig`` stays secret-free.
"""

from __future__ import annotations

import os

from dedoc.core.errors import ProviderConfigError
from dedoc.providers.anthropic import AnthropicProvider
from dedoc.providers.base import KNOWN_PROVIDERS, AIProvider, ProviderConfig
from dedoc.providers.noop import NullProvider
from dedoc.providers.openai_compat import (
    AzureOpenAIProvider,
    OllamaProvider,
    OpenAICompatibleProvider,
    OpenAIProvider,
)

ENV_PROVIDER = "DEDOC_AI_PROVIDER"
ENV_MODEL = "DEDOC_AI_MODEL"
ENV_BASE_URL = "DEDOC_AI_BASE_URL"
ENV_OPENAI_KEY = "DEDOC_OPENAI_API_KEY"
ENV_AZURE_KEY = "DEDOC_AZURE_OPENAI_API_KEY"
ENV_AZURE_ENDPOINT = "DEDOC_AZURE_OPENAI_ENDPOINT"
ENV_ANTHROPIC_KEY = "DEDOC_ANTHROPIC_API_KEY"


def provider_config_from_env(
    *,
    provider: str | None = None,
    model: str | None = None,
    base_url: str | None = None,
) -> ProviderConfig:
    """Build a ``ProviderConfig`` from CLI overrides + ``DEDOC_AI_*`` env vars."""
    name = (provider or os.environ.get(ENV_PROVIDER) or "none").strip().lower()
    if name not in KNOWN_PROVIDERS:
        raise ProviderConfigError(
            f"unknown AI provider {name!r}; expected one of {', '.join(KNOWN_PROVIDERS)}"
        )
    return ProviderConfig(
        provider=name,
        model=model or os.environ.get(ENV_MODEL),
        base_url=base_url or os.environ.get(ENV_BASE_URL),
    )


def build_provider(config: ProviderConfig) -> AIProvider:
    """Instantiate the provider described by ``config``.

    The provider instance carries credentials from the environment; the config
    and the resulting report remain free of secrets.
    """
    name = config.provider
    if name == "none":
        return NullProvider()
    if name == "openai":
        return OpenAIProvider(
            model=config.model,
            base_url=config.base_url,
            api_key=os.environ.get(ENV_OPENAI_KEY),
            timeout_seconds=config.timeout_seconds,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
        )
    if name == "openai_compatible":
        return OpenAICompatibleProvider(
            model=config.model,
            base_url=config.base_url if config.base_url else "",
            api_key=os.environ.get(ENV_OPENAI_KEY),
            timeout_seconds=config.timeout_seconds,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
        )
    if name == "ollama":
        return OllamaProvider(
            model=config.model,
            base_url=config.base_url,
            timeout_seconds=config.timeout_seconds,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
        )
    if name == "azure_openai":
        if config.model is None:
            raise ProviderConfigError("azure_openai requires a model (deployment name)")
        endpoint = config.base_url or os.environ.get(ENV_AZURE_ENDPOINT)
        if not endpoint:
            raise ProviderConfigError(
                "azure_openai requires DEDOC_AZURE_OPENAI_ENDPOINT or a --ai-base-url"
            )
        return AzureOpenAIProvider(
            model=config.model,
            base_url=endpoint,
            api_key=os.environ.get(ENV_AZURE_KEY) or os.environ.get(ENV_OPENAI_KEY),
            timeout_seconds=config.timeout_seconds,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
        )
    if name == "anthropic":
        return AnthropicProvider(
            model=config.model,
            api_key=os.environ.get(ENV_ANTHROPIC_KEY),
            base_url=config.base_url,
            timeout_seconds=config.timeout_seconds,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
        )
    raise ProviderConfigError(f"unknown AI provider {name!r}")


__all__ = [
    "build_provider",
    "provider_config_from_env",
]
