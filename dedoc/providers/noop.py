"""No-AI provider: deterministic mode (BUILD_PLAN.md §13, required).

Never available, so ``build_provider`` + ``available()`` keeps the pipeline
fully deterministic unless the user explicitly configures a real provider.
"""

from __future__ import annotations

from dedoc.core.errors import ProviderError


class NullProvider:
    """The deterministic provider: AI is disabled and cannot be called."""

    name = "none"
    model: str | None = None

    def available(self) -> bool:
        return False

    def explain(self, prompt: str) -> str:
        raise ProviderError("no AI provider is configured")


__all__ = ["NullProvider"]
