#!/usr/bin/env python3
"""Collect likely untranslated English UI strings from a LiteLLM static export.

This is a maintenance helper, not a completeness proof. It scans rendered HTML
text and translatable attributes. Runtime-only strings inside JavaScript bundles
still require browser smoke testing.
"""

from __future__ import annotations

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOCALE = ROOT / "locales" / "zh-CN.json"
SKIP_TAGS = {"script", "style", "noscript", "pre", "code", "textarea"}
ATTRIBUTES = ("aria-label", "placeholder", "title")
LETTER_RE = re.compile(r"[A-Za-z]")


def normalize(value: str) -> str:
    return " ".join(value.split())


def is_candidate(value: str) -> bool:
    value = normalize(value)
    if not value or len(value) > 300 or not LETTER_RE.search(value):
        return False
    if value.startswith(("http://", "https://", "/_next/", "data:")):
        return False
    if value.count("{") + value.count("}") + value.count("[") + value.count("]") > 4:
        return False
    return True


class Collector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[str] = []
        self.values: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.stack.append(tag)
        if tag in SKIP_TAGS:
            return
        for name, value in attrs:
            if name in ATTRIBUTES and value and is_candidate(value):
                self.values.add(normalize(value))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in SKIP_TAGS:
            return
        for name, value in attrs:
            if name in ATTRIBUTES and value and is_candidate(value):
                self.values.add(normalize(value))

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index] == tag:
                del self.stack[index:]
                break

    def handle_data(self, data: str) -> None:
        if any(tag in SKIP_TAGS for tag in self.stack):
            return
        if is_candidate(data):
            self.values.add(normalize(data))


def collect(root: Path) -> set[str]:
    values: set[str] = set()
    for path in root.rglob("*.html"):
        parser = Collector()
        parser.feed(path.read_text(encoding="utf-8", errors="replace"))
        values.update(parser.values)
    return values


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ui_root", type=Path)
    parser.add_argument("--locale", type=Path, default=DEFAULT_LOCALE)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not args.ui_root.is_dir():
        raise SystemExit(f"UI directory does not exist: {args.ui_root}")

    translations = json.loads(args.locale.read_text(encoding="utf-8"))
    known = set(translations)
    values = collect(args.ui_root)
    unknown = sorted(value for value in values if value not in known)

    if args.json:
        print(json.dumps({
            "known_translation_count": len(known),
            "candidate_count": len(values),
            "unknown_count": len(unknown),
            "unknown": unknown,
        }, ensure_ascii=False, indent=2))
        return

    print(f"Known translations: {len(known)}")
    print(f"HTML candidates: {len(values)}")
    print(f"Unknown candidates: {len(unknown)}")
    for value in unknown:
        print(value)


if __name__ == "__main__":
    main()
