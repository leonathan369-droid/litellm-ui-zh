#!/usr/bin/env python3
"""Check whether LiteLLM has a newer stable GitHub release than we verified."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATE = ROOT / "compatibility" / "upstream.json"
LATEST_RELEASE_API = "https://api.github.com/repos/BerriAI/litellm/releases/latest"


def normalize_version(value: str) -> str:
    return value.strip().lstrip("v")


def version_key(value: str) -> tuple[int, ...]:
    normalized = normalize_version(value)
    match = re.fullmatch(r"(\d+(?:\.\d+)*)", normalized)
    if not match:
        raise ValueError(f"unsupported stable version format: {value}")
    return tuple(int(part) for part in normalized.split("."))


def load_latest_release(url: str = LATEST_RELEASE_API) -> dict[str, object]:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "litellm-ui-zh-upstream-watch",
        },
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def evaluate(state: dict[str, object], release: dict[str, object]) -> dict[str, object]:
    latest = normalize_version(str(release.get("tag_name") or ""))
    verified = normalize_version(str(state.get("latest_verified") or ""))
    if not latest or not verified:
        raise ValueError("state and release must contain versions")

    update_available = version_key(latest) > version_key(verified)
    return {
        "project": state.get("project"),
        "latest": latest,
        "verified": verified,
        "update_available": update_available,
        "release_url": release.get("html_url") or "",
        "release_name": release.get("name") or release.get("tag_name") or "",
    }


def write_github_output(path: Path, status: dict[str, object]) -> None:
    values = {
        "latest": status["latest"],
        "verified": status["verified"],
        "update_available": str(bool(status["update_available"])).lower(),
        "release_url": status["release_url"],
    }
    with path.open("a", encoding="utf-8") as handle:
        for key, value in values.items():
            handle.write(f"{key}={value}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument(
        "--release-json",
        type=Path,
        help="read a local GitHub release payload instead of making a network request",
    )
    parser.add_argument(
        "--github-output",
        type=Path,
        help="append status fields to a GitHub Actions output file",
    )
    args = parser.parse_args()

    state = json.loads(args.state.read_text(encoding="utf-8"))
    release = (
        json.loads(args.release_json.read_text(encoding="utf-8"))
        if args.release_json
        else load_latest_release()
    )
    status = evaluate(state, release)
    print(json.dumps(status, ensure_ascii=False, indent=2))

    if args.github_output:
        write_github_output(args.github_output, status)


if __name__ == "__main__":
    main()
