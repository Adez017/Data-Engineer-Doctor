"""Minimal JSON-over-HTTPS transport for provider calls.

Implemented with the standard library so optional AI support adds no runtime
dependencies and the deterministic core stays key-free. A transport is an
injectable POST function so tests can capture the exact bytes that would leave
the process (and prove they are redacted).
"""

from __future__ import annotations

import json
from collections.abc import Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from dedoc.core.errors import ProviderError

#: (url, json_body, headers, timeout_seconds) -> raw response bytes
HttpPost = Callable[[str, dict[str, object], dict[str, str], float], bytes]


def _read_response(response: object) -> bytes:
    if not hasattr(response, "read"):
        raise ProviderError("unexpected transport response (no read method)")
    data = response.read()
    if not isinstance(data, bytes):
        raise ProviderError("unexpected transport response (non-bytes body)")
    return data


def default_http_post(
    url: str, body: dict[str, object], headers: dict[str, str], timeout: float
) -> bytes:
    """POST a JSON body and return the raw response bytes (stdlib only)."""
    request = Request(
        url,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:  # noqa: S310
            return _read_response(response)
    except HTTPError as exc:
        try:
            detail = exc.read(512).decode("utf-8", errors="replace").strip()
        except Exception:  # noqa: BLE001 - response body is best-effort
            detail = ""
        raise ProviderError(
            f"provider returned HTTP {exc.code}{(': ' + detail) if detail else ''}"
        ) from exc
    except URLError as exc:
        raise ProviderError(f"provider request failed: {exc.reason}") from exc


__all__ = ["HttpPost", "default_http_post"]
