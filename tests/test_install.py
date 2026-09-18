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
    def run_installer(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(INSTALLER), *args],
            text=True,
            capture_output=True,
            check=True,
        )

    def make_ui(self, root: Path) -> Path:
        source = root / "source-ui"
        (source / "_next").mkdir(parents=True)
        (source / "index.html").write_text("<html><head></head><body>Home</body></html>")
        (source / "login").mkdir()
        (source / "login" / "index.html").write_text("<html><head></head><body>Login</body></html>")
        return source

    def test_install_check_and_restore(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = self.make_ui(root)
            target = root / "patched-ui"

            self.run_installer("install", "--source", str(source), "--target", str(target))
            self.run_installer("check", "--target", str(target))

            metadata = json.loads((target / ".litellm-ui-zh.json").read_text())
            self.assertEqual(metadata["patch_version"], "0.1.2")
            self.assertEqual(metadata["html_files_injected"], 2)
            self.assertIn('litellm-zh.js?v=3', (target / "index.html").read_text())
            self.assertNotIn('litellm-zh.js?v=3', (source / "index.html").read_text())

            self.run_installer("restore", "--source", str(source), "--target", str(target))
            self.assertNotIn('litellm-zh.js?v=3', (target / "index.html").read_text())
            self.assertFalse((target / ".litellm-ui-zh.json").exists())


if __name__ == "__main__":
    unittest.main()
