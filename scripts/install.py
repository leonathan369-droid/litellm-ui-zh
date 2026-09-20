#!/usr/bin/env python3
"""Install, upgrade, verify, diagnose, or restore the LiteLLM WebUI Chinese overlay.

The installer always works through a separate custom UI directory. It never
edits the LiteLLM package directory or LiteLLM configuration in place.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import uuid


PATCH_VERSION = "0.2.0"
MANIFEST_SCHEMA_VERSION = 2
MANIFEST_NAME = ".litellm-ui-zh.json"
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
PATCH_SOURCE = REPOSITORY_ROOT / "dist" / "litellm-zh.js"
PATCH_ASSET_NAME = "litellm-zh.js"
COMPATIBILITY_STATE = REPOSITORY_ROOT / "compatibility" / "upstream.json"


def fail(message: str) -> None:
    raise SystemExit(f"error: {message}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def validate_ui(path: Path) -> None:
    if not path.is_dir():
        fail(f"UI directory does not exist: {path}")
    if not (path / "index.html").is_file() or not (path / "_next").is_dir():
        fail(f"not a LiteLLM static UI directory: {path}")


def probe_python(python: str, code: str) -> str:
    try:
        return subprocess.run(
            [python, "-c", code],
            check=True,
            text=True,
            capture_output=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as error:
        fail(f"unable to query LiteLLM using {python}: {error}")


def resolve_packaged_ui(python: str) -> Path:
    probe = (
        "import importlib.util, pathlib; "
        "spec = importlib.util.find_spec('litellm'); "
        "assert spec and spec.origin, 'litellm is not installed'; "
        "print(pathlib.Path(spec.origin).resolve().parent / 'proxy' / '_experimental' / 'out')"
    )
    return Path(probe_python(python, probe))


def resolve_litellm_version(python: str, *, required: bool = False) -> str | None:
    code = (
        "import importlib.metadata; "
        "print(importlib.metadata.version('litellm'))"
    )
    try:
        result = subprocess.run(
            [python, "-c", code],
            check=True,
            text=True,
            capture_output=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        if required:
            fail(f"unable to determine LiteLLM version using {python}")
        return None
    return result or None


def resolve_source(source: str | None, python: str) -> Path:
    path = Path(source).expanduser() if source else resolve_packaged_ui(python)
    path = path.resolve()
    validate_ui(path)
    return path


def html_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.html") if path.is_file())


def source_fingerprint(root: Path) -> str:
    digest = hashlib.sha256()
    for path in html_files(root):
        relative = path.relative_to(root).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def patch_asset_version() -> str:
    return sha256(PATCH_SOURCE)[:12]


def script_src(asset_version: str) -> str:
    return f"/ui/assets/{PATCH_ASSET_NAME}?v={asset_version}"


def marker(asset_version: str) -> str:
    return f'src="{script_src(asset_version)}"'


def inject_script(root: Path, asset_version: str) -> int:
    tag = f'<script src="{script_src(asset_version)}"></script>'
    expected_marker = marker(asset_version)
    injected = 0
    for path in html_files(root):
        content = path.read_text(encoding="utf-8")
        if expected_marker in content:
            continue
        if "</head>" not in content:
            fail(f"cannot inject patch because </head> is missing: {path}")
        path.write_text(
            content.replace("</head>", f"{tag}</head>", 1),
            encoding="utf-8",
        )
        injected += 1
    return injected


def manifest(
    target: Path,
    source: Path,
    injected: int,
    total: int,
    litellm_version: str | None,
    asset_version: str,
) -> dict[str, object]:
    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "patch": "litellm-ui-zh",
        "patch_version": PATCH_VERSION,
        "patch_sha256": sha256(PATCH_SOURCE),
        "asset_version": asset_version,
        "litellm_version": litellm_version,
        "source": str(source),
        "source_fingerprint": source_fingerprint(source),
        "target": str(target),
        "html_files_total": total,
        "html_files_injected": injected,
        "installed_at": utc_now(),
    }


def staging_directory(target: Path) -> Path:
    return target.parent / f".{target.name}.litellm-ui-zh-staging-{uuid.uuid4().hex}"


def backup_directory(target: Path) -> Path:
    return target.parent / f"{target.name}.litellm-ui-zh-backup-{uuid.uuid4().hex[:8]}"


def read_manifest(target: Path) -> dict[str, object]:
    metadata_path = target / MANIFEST_NAME
    if not metadata_path.is_file():
        fail(f"patch manifest is missing: {metadata_path}")
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(f"patch manifest is unreadable: {error}")
    if metadata.get("patch") != "litellm-ui-zh":
        fail(f"refusing to operate on an unrelated directory: {target}")
    return metadata


def build_patched_ui(
    source: Path,
    target: Path,
    litellm_version: str | None,
) -> tuple[Path, dict[str, object]]:
    if not PATCH_SOURCE.is_file():
        fail(f"patch asset is missing: {PATCH_SOURCE}")

    stage = staging_directory(target)
    shutil.copytree(source, stage)
    try:
        assets = stage / "assets"
        assets.mkdir(exist_ok=True)
        shutil.copy2(PATCH_SOURCE, assets / PATCH_ASSET_NAME)

        asset_version = patch_asset_version()
        injected = inject_script(stage, asset_version)
        total = len(html_files(stage))
        metadata = manifest(
            target,
            source,
            injected,
            total,
            litellm_version,
            asset_version,
        )
        (stage / MANIFEST_NAME).write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        verify_target(stage, repository_check=True)
        return stage, metadata
    except Exception:
        print(f"staging directory retained for recovery: {stage}", file=sys.stderr)
        raise


def verify_target(
    target: Path,
    *,
    repository_check: bool,
) -> tuple[dict[str, object], list[str], list[str]]:
    validate_ui(target)
    metadata = read_manifest(target)
    patch_path = target / "assets" / PATCH_ASSET_NAME
    files = html_files(target)

    errors: list[str] = []
    warnings: list[str] = []

    if metadata.get("schema_version") != MANIFEST_SCHEMA_VERSION:
        errors.append(
            f"manifest schema is {metadata.get('schema_version')!r}, "
            f"expected {MANIFEST_SCHEMA_VERSION}"
        )

    if not patch_path.is_file():
        errors.append("translation script is missing")
    else:
        installed_hash = sha256(patch_path)
        if metadata.get("patch_sha256") != installed_hash:
            errors.append("translation script checksum differs from install manifest")

        if repository_check:
            repository_hash = sha256(PATCH_SOURCE) if PATCH_SOURCE.is_file() else None
            if repository_hash is None:
                errors.append(f"repository patch asset is missing: {PATCH_SOURCE}")
            elif installed_hash != repository_hash:
                warnings.append("installed patch differs from the current repository build")

    asset_version = str(metadata.get("asset_version") or "")
    expected_marker = marker(asset_version) if asset_version else ""
    injected = (
        sum(expected_marker in path.read_text(encoding="utf-8") for path in files)
        if expected_marker
        else 0
    )
    if injected != len(files):
        errors.append(f"script injected into {injected}/{len(files)} HTML files")

    expected_total = metadata.get("html_files_total")
    if isinstance(expected_total, int) and expected_total != len(files):
        warnings.append(
            f"HTML route count changed from manifest {expected_total} to {len(files)}"
        )

    if repository_check and metadata.get("patch_version") != PATCH_VERSION:
        warnings.append(
            f"installed patch {metadata.get('patch_version')} differs from "
            f"repository {PATCH_VERSION}"
        )

    if errors:
        fail("; ".join(errors))
    return metadata, warnings, files


def install(args: argparse.Namespace) -> None:
    source = resolve_source(args.source, args.python)
    target = Path(args.target).expanduser().resolve()
    if target == source or source in target.parents:
        fail("target must be outside the packaged UI directory")
    if target.exists():
        fail(f"target already exists: {target}; use upgrade for an existing patch")

    target.parent.mkdir(parents=True, exist_ok=True)
    version = resolve_litellm_version(args.python, required=False)
    stage, metadata = build_patched_ui(source, target, version)
    try:
        os.replace(stage, target)
    except Exception:
        print(f"staging directory retained for recovery: {stage}", file=sys.stderr)
        raise

    print(f"installed {metadata['html_files_injected']} HTML injections at {target}")
    if version:
        print(f"LiteLLM version: {version}")
    print("set LITELLM_UI_PATH to this directory, then restart LiteLLM")


def upgrade(args: argparse.Namespace) -> None:
    target = Path(args.target).expanduser().resolve()
    validate_ui(target)
    read_manifest(target)

    source = resolve_source(args.source, args.python)
    if target == source or source in target.parents:
        fail("target must be outside the packaged UI directory")

    version = resolve_litellm_version(args.python, required=False)
    stage, metadata = build_patched_ui(source, target, version)
    backup = backup_directory(target)

    swapped_old = False
    try:
        os.replace(target, backup)
        swapped_old = True
        os.replace(stage, target)
        verify_target(target, repository_check=True)
    except BaseException:
        if target.exists():
            failed = target.parent / f"{target.name}.litellm-ui-zh-failed-{uuid.uuid4().hex[:8]}"
            os.replace(target, failed)
            print(f"failed upgraded copy retained at {failed}", file=sys.stderr)
        if swapped_old and backup.exists():
            os.replace(backup, target)
        if stage.exists():
            print(f"staging directory retained for recovery: {stage}", file=sys.stderr)
        raise

    print(f"upgraded patch at {target}")
    print(f"previous patched copy retained at {backup}")
    if version:
        print(f"LiteLLM version: {version}")
    print(f"HTML routes: {metadata['html_files_injected']}/{metadata['html_files_total']}")


def normalize_version(value: object) -> str:
    return str(value or "").strip().lstrip("v")


def source_version_status(
    metadata: dict[str, object],
    installed_version: str | None,
) -> str:
    manifest_version = normalize_version(metadata.get("litellm_version"))
    current_version = normalize_version(installed_version)
    if not manifest_version or not current_version:
        return "UNKNOWN"
    return "MATCH" if manifest_version == current_version else "CHANGED"


def load_compatibility_state() -> dict[str, object] | None:
    if not COMPATIBILITY_STATE.is_file():
        return None
    try:
        state = json.loads(COMPATIBILITY_STATE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return state if isinstance(state, dict) else None


def compatibility_status(
    installed_version: str | None,
    state: dict[str, object] | None = None,
) -> str:
    current = normalize_version(installed_version)
    if not current:
        return "UNKNOWN"

    state = state if state is not None else load_compatibility_state()
    if not state:
        return "UNKNOWN"

    records = state.get("verified")
    if not isinstance(records, list):
        return "UNKNOWN"

    for record in records:
        if not isinstance(record, dict):
            continue
        if normalize_version(record.get("litellm")) != current:
            continue
        status = str(record.get("status") or "").replace("_", "-").lower()
        if status == "verified":
            return "VERIFIED"
        if status == "automated-verified":
            return "AUTOMATED_VERIFIED"
        return "UNVERIFIED"
    return "UNVERIFIED"


def check(args: argparse.Namespace) -> None:
    target = Path(args.target).expanduser().resolve()
    metadata, warnings, files = verify_target(target, repository_check=True)
    installed_version = resolve_litellm_version(args.python, required=False)
    source_status = source_version_status(metadata, installed_version)
    status = compatibility_status(installed_version)

    print("litellm-ui-zh check")
    print(f"patch installed:   {metadata.get('patch_version')}")
    print(f"patch repository:  {PATCH_VERSION}")
    print(f"translation asset: OK")
    print(f"HTML injection:    {len(files)}/{len(files)}")
    print(f"LiteLLM manifest:  {metadata.get('litellm_version') or 'unknown'}")
    print(f"LiteLLM installed: {installed_version or 'unknown'}")
    print(f"source version:     {source_status}")
    print(f"compatibility:      {status}")
    for warning in warnings:
        print(f"warning: {warning}")


def diagnose(args: argparse.Namespace) -> None:
    target = Path(args.target).expanduser().resolve()
    metadata, warnings, files = verify_target(target, repository_check=True)
    installed_version = resolve_litellm_version(args.python, required=False)

    print("litellm-ui-zh diagnose")
    print(f"patch_version={metadata.get('patch_version')}")
    print(f"repository_version={PATCH_VERSION}")
    print(f"litellm_manifest={metadata.get('litellm_version') or 'unknown'}")
    print(f"litellm_installed={installed_version or 'unknown'}")
    print(f"python={sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    print(f"platform={sys.platform}")
    print(f"manifest_schema={metadata.get('schema_version')}")
    print(f"patch_checksum=OK")
    print(f"html_routes={len(files)}")
    print(f"source_version={source_version_status(metadata, installed_version)}")
    print(f"compatibility={compatibility_status(installed_version)}")
    for warning in warnings:
        print(f"warning={warning}")


def restore(args: argparse.Namespace) -> None:
    target = Path(args.target).expanduser().resolve()
    validate_ui(target)
    metadata = read_manifest(target)
    source_value = args.source or metadata.get("source")
    source = resolve_source(str(source_value) if source_value else None, args.python)

    stage = staging_directory(target)
    shutil.copytree(source, stage)
    backup = backup_directory(target)
    swapped_old = False
    try:
        os.replace(target, backup)
        swapped_old = True
        os.replace(stage, target)
    except BaseException:
        if target.exists():
            failed = target.parent / f"{target.name}.litellm-ui-zh-failed-{uuid.uuid4().hex[:8]}"
            os.replace(target, failed)
            print(f"failed restore copy retained at {failed}", file=sys.stderr)
        if swapped_old and backup.exists():
            os.replace(backup, target)
        if stage.exists():
            print(f"staging directory retained for recovery: {stage}", file=sys.stderr)
        raise

    print(f"restored upstream UI at {target}")
    print(f"patched copy retained for recovery at {backup}")
    print("remove LITELLM_UI_PATH or point it at another UI directory, then restart LiteLLM")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument(
        "command",
        choices=("install", "upgrade", "check", "restore", "diagnose"),
    )
    result.add_argument("--target", required=True, help="custom UI directory to operate on")
    result.add_argument("--source", help="LiteLLM packaged UI directory; auto-detected by default")
    result.add_argument("--python", default=sys.executable, help="Python environment containing LiteLLM")
    return result


def main() -> None:
    args = parser().parse_args()
    commands = {
        "install": install,
        "upgrade": upgrade,
        "check": check,
        "restore": restore,
        "diagnose": diagnose,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
