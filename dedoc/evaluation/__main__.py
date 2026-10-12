"""CLI entry point: ``python -m dedoc.evaluation`` (also ``make evaluate``).

Exit codes: 0 on success, 1 when ``--strict`` and a case failed or regressed,
2 on usage/setup errors.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from dedoc.core.paths import fixtures_root
from dedoc.evaluation.harness import baseline_from_result, run_evaluation
from dedoc.evaluation.report import render_json, render_text

_DESCRIPTION = "Grade the DEDoc deterministic pipeline against the fixtures corpus (§19)."


def _parse_baseline(path: Path) -> dict[str, bool]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not all(isinstance(v, bool) for v in data.values()):
        raise ValueError(f"baseline {path} must be a JSON object of name -> true/false")
    return {str(k): bool(v) for k, v in data.items()}


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m dedoc.evaluation", description=_DESCRIPTION)
    parser.add_argument("--corpus", type=Path, default=None, help="fixtures directory")
    parser.add_argument("--diagnoses", type=Path, default=None, help="diagnoses directory override")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--baseline", type=Path, default=None, help="regression baseline JSON")
    parser.add_argument("--output", type=Path, default=None, help="write full result JSON here")
    parser.add_argument(
        "--write-baseline", type=Path, default=None, help="write a fresh baseline JSON here"
    )
    parser.add_argument("--strict", action="store_true", help="exit 1 on any failure or regression")
    args = parser.parse_args(argv)

    corpus: Path = args.corpus if args.corpus is not None else fixtures_root()
    if not Path(corpus).is_dir():
        print(f"error: corpus directory not found: {corpus}", file=sys.stderr)
        return 2

    baseline: dict[str, bool] | None = None
    baseline_path: str | None = None
    if args.baseline is not None:
        try:
            baseline = _parse_baseline(args.baseline)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        baseline_path = str(args.baseline)

    result = run_evaluation(
        corpus,
        diagnoses_path=args.diagnoses,
        baseline=baseline,
        baseline_path=baseline_path,
    )
    rendered = render_json(result) if args.format == "json" else render_text(result)
    print(rendered)

    if args.output is not None:
        _write(args.output, render_json(result))
    if args.write_baseline is not None:
        payload: dict[str, Any] = baseline_from_result(result)
        _write(args.write_baseline, json.dumps(payload, indent=2) + "\n")

    if args.strict and (not result.ok or result.regressions):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
