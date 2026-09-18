from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "scripts" / "install.py"


class UpgradeTest(unittest.TestCase):
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

    def make_ui(self, root: Path, name: str, text: str) -> Path:
        source = root / name
        (source / "_next").mkdir(parents=True)
        (source / "index.html").write_text(
            f"<html><head></head><body>{text}</body></html>",
            encoding="utf-8",
        )
        return source

    def test_upgrade_replaces_source_and_keeps_backup(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            old_source = self.make_ui(root, "old-source", "Old")
            new_source = self.make_ui(root, "new-source", "New")
            target = root / "patched-ui"

            self.run_installer(
                "install", "--source", str(old_source), "--target", str(target)
            )
            old_fingerprint = json.loads(
                (target / ".litellm-ui-zh.json").read_text()
            )["source_fingerprint"]

            result = self.run_installer(
                "upgrade", "--source", str(new_source), "--target", str(target)
            )

            metadata = json.loads((target / ".litellm-ui-zh.json").read_text())
            self.assertNotEqual(metadata["source_fingerprint"], old_fingerprint)
            self.assertIn("New", (target / "index.html").read_text())
            backups = list(root.glob("patched-ui.litellm-ui-zh-backup-*"))
            self.assertEqual(len(backups), 1)
            self.assertIn("Old", (backups[0] / "index.html").read_text())
            self.assertIn("previous patched copy retained", result.stdout)

    def test_upgrade_rejects_unmarked_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = self.make_ui(root, "source", "Home")
            target = self.make_ui(root, "target", "Existing")

            result = self.run_installer(
                "upgrade",
                "--source",
                str(source),
                "--target",
                str(target),
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("manifest is missing", result.stderr)

    def test_failed_upgrade_does_not_replace_current_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            old_source = self.make_ui(root, "old-source", "Old")
            broken_source = root / "broken-source"
            (broken_source / "_next").mkdir(parents=True)
            (broken_source / "index.html").write_text(
                "<html><body>Broken</body></html>",
                encoding="utf-8",
            )
            target = root / "patched-ui"

            self.run_installer(
                "install", "--source", str(old_source), "--target", str(target)
            )
            before = (target / "index.html").read_text()

            result = self.run_installer(
                "upgrade",
                "--source",
                str(broken_source),
                "--target",
                str(target),
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertEqual((target / "index.html").read_text(), before)
            self.assertTrue((target / ".litellm-ui-zh.json").exists())


if __name__ == "__main__":
    unittest.main()
