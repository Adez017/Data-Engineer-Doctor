"""Anthropic Messages API provider (optional, §13)."""

from __future__ import annotations

import json
from typing import Any

from dedoc.core.errors import ProviderError
from dedoc.providers.base import AIProvider
from dedoc.providers.prompt import SYSTEM_INSTRUCTIONS
from dedoc.providers.transport import HttpPost, default_http_post


class AnthropicProvider(AIProvider):
    """Anthropic-hosted model via the /v1/messages endpoint."""

    name = "anthropic"
    DEFAULT_BASE_URL = "https://api.anthropic.com"
    API_VERSION = "2023-06-01"

    def __init__(
        self,
        *,
        model: str | None,
        api_key: str | None,
        base_url: str | None = None,
        transport: HttpPost | None = None,
        timeout_seconds: float = 30.0,
        max_tokens: int = 500,
        temperature: float = 0.0,
    ) -> None:
        self.model = model
        self._base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self._api_key = api_key
        self._transport = transport or default_http_post
        self._timeout_seconds = timeout_seconds
        self._max_tokens = max_tokens
        self._temperature = temperature

    def _endpoint(self) -> str:
        return f"{self._base_url}/v1/messages"

    def available(self) -> bool:
        return bool(self.model) and bool(self._api_key)

    def explain(self, prompt: str) -> str:
        if not self.available():
            raise ProviderError("provider 'anthropic' is not available")
        body: dict[str, object] = {
            "model": self.model,
            "max_tokens": self._max_tokens,
            "temperature": self._temperature,
            "system": SYSTEM_INSTRUCTIONS,
            "messages": [{"role": "user", "content": prompt}],
        }
        headers = {
            "x-api-key": self._api_key or "",
            "anthropic-version": self.API_VERSION,
        }
        raw = self._transport(self._endpoint(), body, headers, self._timeout_seconds)
        return self._parse(raw)

    @staticmethod
    def _parse(raw: bytes) -> str:
        try:
            data: Any = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ProviderError("provider returned invalid JSON") from exc
        try:
            content = data["content"][0]["text"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ProviderError("provider response missing content[0].text") from exc
        return str(content)


__all__ = ["AnthropicProvider"]
