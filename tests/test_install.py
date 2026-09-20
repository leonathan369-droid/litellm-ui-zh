from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "scripts" / "install.py"


class InstallTest(unittest.TestCase):
    def run_installer(
        self,
        *args: str,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(INSTALLER), *args],
            text=True,
            capture_output=True,
            check=check,
        )

    def make_ui(self, root: Path, *, label: str = "Home") -> Path:
        source = root / f"source-ui-{label.lower()}"
        (source / "_next").mkdir(parents=True)
        (source / "index.html").write_text(
            f"<html><head></head><body>{label}</body></html>",
            encoding="utf-8",
        )
        (source / "login").mkdir()
        (source / "login" / "index.html").write_text(
            "<html><head></head><body>Login</body></html>",
            encoding="utf-8",
        )
        return source

    def test_install_check_diagnose_and_restore(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = self.make_ui(root)
            target = root / "patched-ui"

            self.run_installer(
                "install", "--source", str(source), "--target", str(target)
            )

            metadata = json.loads((target / ".litellm-ui-zh.json").read_text())
            self.assertEqual(metadata["schema_version"], 2)
            self.assertEqual(metadata["patch_version"], "0.2.0")
            self.assertEqual(metadata["html_files_injected"], 2)
            self.assertEqual(metadata["html_files_total"], 2)
            self.assertEqual(len(metadata["source_fingerprint"]), 64)
            marker = f'litellm-zh.js?v={metadata["asset_version"]}'
            self.assertIn(marker, (target / "index.html").read_text())
            self.assertNotIn(marker, (source / "index.html").read_text())

            checked = self.run_installer("check", "--target", str(target))
            self.assertIn("translation asset: OK", checked.stdout)
            self.assertIn("compatibility:", checked.stdout)

            diagnosed = self.run_installer("diagnose", "--target", str(target))
            self.assertIn("patch_version=0.2.0", diagnosed.stdout)
            self.assertIn("patch_checksum=OK", diagnosed.stdout)

            self.run_installer(
                "restore", "--source", str(source), "--target", str(target)
            )
            self.assertFalse((target / ".litellm-ui-zh.json").exists())
            self.assertNotIn("litellm-zh.js", (target / "index.html").read_text())

    def test_install_refuses_existing_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = self.make_ui(root)
            target = root / "patched-ui"
            target.mkdir()

            result = self.run_installer(
                "install",
                "--source",
                str(source),
                "--target",
                str(target),
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("use upgrade", result.stderr)

    def test_check_detects_modified_overlay(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = self.make_ui(root)
            target = root / "patched-ui"

            self.run_installer(
                "install", "--source", str(source), "--target", str(target)
            )
            patch = target / "assets" / "litellm-zh.js"
            patch.write_text(patch.read_text() + "\n// modified\n")

            result = self.run_installer(
                "check", "--target", str(target), check=False
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("checksum differs", result.stderr)

    def test_check_refuses_unmarked_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = self.make_ui(root)

            result = self.run_installer(
                "check", "--target", str(source), check=False
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("manifest is missing", result.stderr)


if __name__ == "__main__":
    unittest.main()
