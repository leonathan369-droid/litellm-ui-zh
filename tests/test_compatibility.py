from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "scripts" / "install.py"

spec = importlib.util.spec_from_file_location("litellm_ui_zh_installer", INSTALLER)
assert spec and spec.loader
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class CompatibilityStatusTest(unittest.TestCase):
    def test_matching_versions_are_reported_as_match(self) -> None:
        metadata = {"litellm_version": "1.101.0"}
        self.assertEqual(
            installer.compatibility_status(metadata, "1.101.0"),
            "MATCH",
        )

    def test_changed_litellm_version_is_unverified(self) -> None:
        metadata = {"litellm_version": "1.101.0"}
        self.assertEqual(
            installer.compatibility_status(metadata, "1.102.0"),
            "UNVERIFIED",
        )

    def test_missing_version_is_unknown(self) -> None:
        self.assertEqual(
            installer.compatibility_status({"litellm_version": None}, None),
            "UNKNOWN",
        )


if __name__ == "__main__":
    unittest.main()
