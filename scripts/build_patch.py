#!/usr/bin/env python3
"""Build the browser overlay from the locale dictionary and runtime source."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOCALE = ROOT / "locales" / "zh-CN.json"
DEFAULT_SOURCE = ROOT / "src" / "overlay.js"
DEFAULT_OUTPUT = ROOT / "dist" / "litellm-zh.js"
PLACEHOLDER = "__LITELLM_ZH_TRANSLATIONS__"


def build(locale_path: Path, source_path: Path) -> str:
    translations = json.loads(locale_path.read_text(encoding="utf-8"))
    if not isinstance(translations, dict) or not all(
        isinstance(key, str) and isinstance(value, str)
        for key, value in translations.items()
    ):
        raise SystemExit("locale must be a JSON object with string keys and values")

    source = source_path.read_text(encoding="utf-8")
    if source.count(PLACEHOLDER) != 1:
        raise SystemExit(f"source must contain exactly one {PLACEHOLDER} placeholder")

    payload = json.dumps(translations, ensure_ascii=False, separators=(",", ":"))
    return source.replace(PLACEHOLDER, payload)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--locale", type=Path, default=DEFAULT_LOCALE)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    result = build(args.locale, args.source)
    if args.check:
        if not args.output.is_file():
            raise SystemExit(f"generated output is missing: {args.output}")
        if args.output.read_text(encoding="utf-8") != result:
            raise SystemExit("generated overlay is stale; run scripts/build_patch.py")
        print(f"ok: {args.output} is reproducible")
        return

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result, encoding="utf-8")
    print(f"built {args.output}")


if __name__ == "__main__":
    main()
