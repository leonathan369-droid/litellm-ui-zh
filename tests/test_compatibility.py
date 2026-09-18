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
    def test_manifest_and_current_version_match_is_only_source_match(self) -> None:
        metadata = {"litellm_version": "1.101.0"}
        self.assertEqual(
            installer.source_version_status(metadata, "1.101.0"),
            "MATCH",
        )

    def test_changed_installed_version_is_reported_separately(self) -> None:
        metadata = {"litellm_version": "1.101.0"}
        self.assertEqual(
            installer.source_version_status(metadata, "1.102.0"),
            "CHANGED",
        )

    def test_verified_version_requires_verified_compatibility_record(self) -> None:
        state = {
            "verified": [
                {
                    "litellm": "1.101.0",
                    "status": "verified",
                    "os": ["macOS"],
                }
            ]
        }
        self.assertEqual(
            installer.compatibility_status("1.101.0", state),
            "VERIFIED",
        )

    def test_unreviewed_version_is_unverified_even_when_installed_cleanly(self) -> None:
        state = {
            "verified": [
                {"litellm": "1.101.0", "status": "verified"}
            ]
        }
        self.assertEqual(
            installer.compatibility_status("1.102.0", state),
            "UNVERIFIED",
        )

    def test_non_verified_record_does_not_count(self) -> None:
        state = {
            "verified": [
                {"litellm": "1.102.0", "status": "community"}
            ]
        }
        self.assertEqual(
            installer.compatibility_status("1.102.0", state),
            "UNVERIFIED",
        )

    def test_missing_version_or_state_is_unknown(self) -> None:
        self.assertEqual(installer.compatibility_status(None, {"verified": []}), "UNKNOWN")
        self.assertEqual(installer.compatibility_status("1.101.0", {}), "UNKNOWN")
        self.assertEqual(
            installer.source_version_status({"litellm_version": None}, None),
            "UNKNOWN",
        )


if __name__ == "__main__":
    unittest.main()
