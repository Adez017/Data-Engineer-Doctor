"""OpenAI-compatible providers (OpenAI, Ollama, any /v1 chat completions).

Covers BUILD_PLAN.md §13's OpenAI-compatible and local (Ollama-compatible)
options with one code path. Azure OpenAI is a thin subclass that uses the
deployment URL form and ``api-key`` header instead of ``Authorization``.
"""

from __future__ import annotations

import json
from typing import Any

from dedoc.core.errors import ProviderError
from dedoc.providers.base import AIProvider
from dedoc.providers.prompt import SYSTEM_INSTRUCTIONS
from dedoc.providers.transport import HttpPost, default_http_post


class OpenAICompatibleProvider(AIProvider):
    """A chat-completions provider with an optional bearer key."""

    name = "openai_compatible"

    def __init__(
        self,
        *,
        model: str | None,
        base_url: str,
        api_key: str | None = None,
        require_api_key: bool = False,
        transport: HttpPost | None = None,
        timeout_seconds: float = 30.0,
        max_tokens: int = 500,
        temperature: float = 0.0,
    ) -> None:
        self.model = model
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._require_api_key = require_api_key
        self._transport = transport or default_http_post
        self._timeout_seconds = timeout_seconds
        self._max_tokens = max_tokens
        self._temperature = temperature

    def _endpoint(self) -> str:
        if self._base_url.endswith("/chat/completions"):
            return self._base_url
        return f"{self._base_url}/chat/completions"

    def _headers(self) -> dict[str, str]:
        if self._api_key:
            return {"Authorization": f"Bearer {self._api_key}"}
        return {}

    def available(self) -> bool:
        return (
            bool(self.model)
            and bool(self._base_url)
            and (not self._require_api_key or bool(self._api_key))
        )

    def explain(self, prompt: str) -> str:
        if not self.available():
            raise ProviderError(f"provider {self.name!r} is not available")
        body: dict[str, object] = {
            "model": self.model,
            "temperature": self._temperature,
            "max_tokens": self._max_tokens,
            "messages": [
                {"role": "system", "content": SYSTEM_INSTRUCTIONS},
                {"role": "user", "content": prompt},
            ],
        }
        raw = self._transport(self._endpoint(), body, self._headers(), self._timeout_seconds)
        return self._parse(raw)

    @staticmethod
    def _parse(raw: bytes) -> str:
        try:
            data: Any = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ProviderError("provider returned invalid JSON") from exc
        try:
            return str(data["choices"][0]["message"]["content"])
        except (KeyError, IndexError, TypeError) as exc:
            raise ProviderError("provider response missing choices[0].message.content") from exc


class OpenAIProvider(OpenAICompatibleProvider):
    """OpenAI-hosted chat completions (requires an API key)."""

    name = "openai"
    DEFAULT_BASE_URL = "https://api.openai.com/v1"

    def __init__(
        self,
        *,
        model: str | None,
        base_url: str | None = None,
        api_key: str | None = None,
        transport: HttpPost | None = None,
        timeout_seconds: float = 30.0,
        max_tokens: int = 500,
        temperature: float = 0.0,
    ) -> None:
        super().__init__(
            model=model,
            base_url=base_url or self.DEFAULT_BASE_URL,
            api_key=api_key,
            require_api_key=True,
            transport=transport,
            timeout_seconds=timeout_seconds,
            max_tokens=max_tokens,
            temperature=temperature,
        )


class OllamaProvider(OpenAICompatibleProvider):
    """Local Ollama via its OpenAI-compatible endpoint (no key)."""

    name = "ollama"
    DEFAULT_BASE_URL = "http://localhost:11434/v1"

    def __init__(
        self,
        *,
        model: str | None,
        base_url: str | None = None,
        transport: HttpPost | None = None,
        timeout_seconds: float = 30.0,
        max_tokens: int = 500,
        temperature: float = 0.0,
    ) -> None:
        super().__init__(
            model=model,
            base_url=base_url or self.DEFAULT_BASE_URL,
            api_key=None,
            require_api_key=False,
            transport=transport,
            timeout_seconds=timeout_seconds,
            max_tokens=max_tokens,
            temperature=temperature,
        )


class AzureOpenAIProvider(OpenAICompatibleProvider):
    """Azure OpenAI chat completions (deployment URL + ``api-key`` header)."""

    name = "azure_openai"
    API_VERSION = "2024-06-01"

    def __init__(
        self,
        *,
        model: str | None,
        base_url: str,
        api_key: str | None = None,
        transport: HttpPost | None = None,
        timeout_seconds: float = 30.0,
        max_tokens: int = 500,
        temperature: float = 0.0,
    ) -> None:
        if model is None:
            raise ProviderError("azure_openai requires a deployment name as the model")
        super().__init__(
            model=model,
            base_url=base_url,
            api_key=api_key,
            require_api_key=True,
            transport=transport,
            timeout_seconds=timeout_seconds,
            max_tokens=max_tokens,
            temperature=temperature,
        )

    def _endpoint(self) -> str:
        root = self._base_url.rstrip("/")
        return (
            f"{root}/openai/deployments/{self.model}/chat/completions"
            f"?api-version={self.API_VERSION}"
        )

    def _headers(self) -> dict[str, str]:
        if self._api_key:
            return {"api-key": self._api_key}
        return {}


__all__ = [
    "AzureOpenAIProvider",
    "OllamaProvider",
    "OpenAICompatibleProvider",
    "OpenAIProvider",
]
