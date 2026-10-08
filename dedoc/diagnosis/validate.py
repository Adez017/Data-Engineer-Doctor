"""Validate diagnosis knowledge: schema, signal registry, fixtures, links.

Run by ``make validate`` (schema) and ``make link-check`` (network, §18).
"""

from __future__ import annotations

import sys
import time
import urllib.error
import urllib.request

from dedoc.analyzer.signals import SIGNAL_REGISTRY
from dedoc.core.errors import DiagnosisLoadError
from dedoc.core.paths import fixtures_root, resolve_diagnoses_path
from dedoc.diagnosis.loader import load_diagnoses
from dedoc.models.diagnosis import Diagnosis

_LINK_TIMEOUT_SECONDS = 15
_LINK_RETRIES = 2


def validate_diagnoses(diagnoses: dict[str, Diagnosis]) -> list[str]:
    """Return a list of problems (empty when valid)."""
    problems: list[str] = []
    for diagnosis in diagnoses.values():
        for signal in [*diagnosis.signals.positive, *diagnosis.signals.negative]:
            if signal not in SIGNAL_REGISTRY:
                problems.append(
                    f"{diagnosis.id}: signal {signal!r} has no extractor in "
                    "dedoc.analyzer.signals.SIGNAL_REGISTRY"
                )
        if not diagnosis.patterns.exception_types and not diagnosis.signals.positive:
            problems.append(
                f"{diagnosis.id}: must declare at least one exception type or positive signal"
            )
        if not diagnosis.hypotheses:
            problems.append(f"{diagnosis.id}: must declare at least one hypothesis")
        if not diagnosis.references:
            problems.append(f"{diagnosis.id}: must declare at least one reference")
    return problems


def validate_fixture_references(diagnoses: dict[str, Diagnosis]) -> list[str]:
    """Check that every fixture referenced by a diagnosis exists (when fixtures/ is present)."""
    root = fixtures_root()
    if not root.is_dir():
        return []
    problems: list[str] = []
    for diagnosis in diagnoses.values():
        for fixture in diagnosis.tests.fixtures:
            if not (root / fixture).is_dir():
                problems.append(f"{diagnosis.id}: unknown fixture reference {fixture!r}")
    return problems


def validate_fixture_coverage(diagnoses: dict[str, Diagnosis]) -> list[str]:
    """Every diagnosis must appear in at least one positive fixture (M2)."""
    root = fixtures_root()
    if not root.is_dir():
        return []
    positive_ids: set[str] = set()
    for meta_path in sorted((root / "positive").glob("*/meta.yaml")):
        import yaml

        meta = yaml.safe_load(meta_path.read_text(encoding="utf-8"))
        if isinstance(meta, dict):
            expected = meta.get("expected", {})
            if isinstance(expected, dict):
                ids = expected.get("diagnosis_ids", [])
                if isinstance(ids, list):
                    positive_ids.update(str(i) for i in ids)
    problems: list[str] = []
    for diagnosis in diagnoses.values():
        if diagnosis.id not in positive_ids:
            problems.append(f"{diagnosis.id}: no positive fixture expects this diagnosis")
    return problems


def _http_status(url: str) -> int:
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "dedoc-linkcheck"})
    try:
        with urllib.request.urlopen(request, timeout=_LINK_TIMEOUT_SECONDS) as response:  # noqa: S310
            return int(response.status)
    except urllib.error.HTTPError as exc:
        if exc.code in (403, 405, 429):  # HEAD rejected; retry with GET
            pass
        else:
            return int(exc.code)
    except (urllib.error.URLError, TimeoutError, OSError):
        return 0
    request = urllib.request.Request(url, headers={"User-Agent": "dedoc-linkcheck"})
    try:
        with urllib.request.urlopen(request, timeout=_LINK_TIMEOUT_SECONDS) as response:  # noqa: S310
            return int(response.status)
    except urllib.error.HTTPError as exc:
        return int(exc.code)
    except (urllib.error.URLError, TimeoutError, OSError):
        return 0


def check_links(diagnoses: dict[str, Diagnosis]) -> list[str]:
    """HTTP-check every reference URL; returns problems (empty when all reachable)."""
    problems: list[str] = []
    seen: dict[str, str] = {}
    for diagnosis in diagnoses.values():
        for reference in diagnosis.references:
            if reference.url in seen:
                if seen[reference.url] != "ok":
                    problems.append(
                        f"{diagnosis.id}: unreachable reference {reference.url} "
                        f"({seen[reference.url]})"
                    )
                continue
            status = 0
            for _attempt in range(_LINK_RETRIES + 1):
                status = _http_status(reference.url)
                if status and status < 400:
                    break
                time.sleep(1.0)
            if status and status < 400:
                seen[reference.url] = "ok"
            else:
                reason = f"HTTP {status}" if status else "connection failed"
                seen[reference.url] = reason
                problems.append(f"{diagnosis.id}: unreachable reference {reference.url} ({reason})")
    return problems


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    with_links = "--links" in args
    try:
        root = resolve_diagnoses_path()
        diagnoses = load_diagnoses(root)
    except DiagnosisLoadError as exc:
        print(f"diagnosis validation FAILED:\n{exc}", file=sys.stderr)
        return 1
    problems = (
        validate_diagnoses(diagnoses)
        + validate_fixture_references(diagnoses)
        + validate_fixture_coverage(diagnoses)
    )
    if with_links and not problems:
        problems = check_links(diagnoses)
    if problems:
        print("diagnosis validation FAILED:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1
    suffix = " (+ links)" if with_links else ""
    print(f"validated {len(diagnoses)} diagnosis definition(s) from {root}{suffix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
