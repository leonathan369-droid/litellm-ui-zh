#!/usr/bin/env python3
"""Install, verify, or restore the LiteLLM WebUI Simplified Chinese patch.

The script copies LiteLLM's packaged UI into an explicitly supplied target
directory. It never edits the package directory or LiteLLM configuration.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import uuid


PATCH_VERSION = "0.1.0"
MARKER = 'src="/ui/assets/litellm-zh.js?v=3"'
MANIFEST_NAME = ".litellm-ui-zh.json"
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
PATCH_SOURCE = REPOSITORY_ROOT / "patches" / "litellm-zh.js"


def fail(message: str) -> None:
    raise SystemExit(f"error: {message}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_ui(path: Path) -> None:
    if not path.is_dir():
        fail(f"UI directory does not exist: {path}")
    if not (path / "index.html").is_file() or not (path / "_next").is_dir():
        fail(f"not a LiteLLM static UI directory: {path}")


def resolve_packaged_ui(python: str) -> Path:
    probe = (
        "import importlib.util, pathlib; "
        "spec = importlib.util.find_spec('litellm'); "
        "assert spec and spec.origin, 'litellm is not installed'; "
        "print(pathlib.Path(spec.origin).resolve().parent / 'proxy' / '_experimental' / 'out')"
    )
    try:
        output = subprocess.run(
            [python, "-c", probe], check=True, text=True, capture_output=True
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as error:
        fail(f"unable to locate LiteLLM using {python}: {error}")
    return Path(output)


def resolve_source(source: str | None, python: str) -> Path:
    path = Path(source).expanduser() if source else resolve_packaged_ui(python)
    path = path.resolve()
    validate_ui(path)
    return path


def html_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.html") if path.is_file())


def inject_script(root: Path) -> int:
    script_tag = '<script src="/ui/assets/litellm-zh.js?v=3"></script>'
    injected = 0
    for path in html_files(root):
        content = path.read_text(encoding="utf-8")
        if MARKER in content:
            continue
        if "</head>" not in content:
            fail(f"cannot inject patch because </head> is missing: {path}")
        path.write_text(content.replace("</head>", f"{script_tag}</head>", 1), encoding="utf-8")
        injected += 1
    return injected


def manifest(target: Path, source: Path, injected: int) -> dict[str, object]:
    return {
        "patch": "litellm-ui-zh",
        "patch_version": PATCH_VERSION,
        "patch_sha256": sha256(PATCH_SOURCE),
        "source": str(source),
        "target": str(target),
        "html_files_injected": injected,
    }


def staging_directory(target: Path) -> Path:
    return target.parent / f".{target.name}.litellm-ui-zh-staging-{uuid.uuid4().hex}"


def build_patched_ui(source: Path, target: Path) -> tuple[Path, int]:
    stage = staging_directory(target)
    shutil.copytree(source, stage)
    try:
        assets = stage / "assets"
        assets.mkdir(exist_ok=True)
        shutil.copy2(PATCH_SOURCE, assets / "litellm-zh.js")
        injected = inject_script(stage)
        (stage / MANIFEST_NAME).write_text(
            json.dumps(manifest(target, source, injected), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return stage, injected
    except Exception:
        print(f"staging directory retained for recovery: {stage}", file=sys.stderr)
        raise


def install(args: argparse.Namespace) -> None:
    if not PATCH_SOURCE.is_file():
        fail(f"patch asset is missing: {PATCH_SOURCE}")
    source = resolve_source(args.source, args.python)
    target = Path(args.target).expanduser().resolve()
    if target == source or source in target.parents:
        fail("target must be outside the packaged UI directory")
    if target.exists():
        fail(f"target already exists: {target}; choose a new empty path")

    target.parent.mkdir(parents=True, exist_ok=True)
    stage, injected = build_patched_ui(source, target)
    try:
        os.replace(stage, target)
    except Exception:
        print(f"staging directory retained for recovery: {stage}", file=sys.stderr)
        raise
    print(f"installed {injected} HTML injections at {target}")
    print("set LITELLM_UI_PATH to this directory, then restart LiteLLM")


def check(args: argparse.Namespace) -> None:
    target = Path(args.target).expanduser().resolve()
    validate_ui(target)
    metadata_path = target / MANIFEST_NAME
    if not metadata_path.is_file():
        fail(f"patch manifest is missing: {metadata_path}")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    patch_path = target / "assets" / "litellm-zh.js"
    files = html_files(target)
    injected = sum(MARKER in path.read_text(encoding="utf-8") for path in files)
    errors = []
    if not patch_path.is_file():
        errors.append("translation script is missing")
    elif metadata.get("patch_sha256") != sha256(patch_path):
        errors.append("translation script checksum differs from the install manifest")
    if injected != len(files):
        errors.append(f"script injected into {injected}/{len(files)} HTML files")
    if errors:
        fail("; ".join(errors))
    print(f"ok: {target} has {len(files)} patched HTML files")


def restore(args: argparse.Namespace) -> None:
    target = Path(args.target).expanduser().resolve()
    validate_ui(target)
    metadata_path = target / MANIFEST_NAME
    if not metadata_path.is_file():
        fail(f"refusing to restore an unmarked directory: {target}")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    source = resolve_source(args.source or metadata.get("source"), args.python)
    stage = staging_directory(target)
    shutil.copytree(source, stage)
    backup = target.parent / f"{target.name}.litellm-ui-zh-backup-{uuid.uuid4().hex[:8]}"
    try:
        os.replace(target, backup)
        os.replace(stage, target)
    except Exception:
        if backup.exists() and not target.exists():
            os.replace(backup, target)
        print(f"staging directory retained for recovery: {stage}", file=sys.stderr)
        raise
    print(f"restored upstream UI at {target}")
    print(f"patched copy retained for recovery at {backup}")
    print("remove LITELLM_UI_PATH or point it at another UI directory, then restart LiteLLM")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("command", choices=("install", "check", "restore"))
    result.add_argument("--target", required=True, help="custom UI directory to create or verify")
    result.add_argument("--source", help="LiteLLM packaged UI directory; auto-detected by default")
    result.add_argument("--python", default=sys.executable, help="Python environment containing LiteLLM")
    return result


def main() -> None:
    args = parser().parse_args()
    if args.command == "install":
        install(args)
    elif args.command == "check":
        check(args)
    else:
        restore(args)


if __name__ == "__main__":
    main()
