from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_upstream.py"

spec = importlib.util.spec_from_file_location("upstream_watch", SCRIPT)
assert spec and spec.loader
watch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(watch)


class UpstreamWatchTest(unittest.TestCase):
    def test_newer_stable_release_is_detected(self) -> None:
        state = {"project": "BerriAI/litellm", "latest_verified": "1.99.0"}
        release = {
            "tag_name": "v1.101.0",
            "html_url": "https://example.invalid/release",
            "name": "v1.101.0",
        }
        status = watch.evaluate(state, release)
        self.assertTrue(status["update_available"])
        self.assertEqual(status["latest"], "1.101.0")

    def test_automated_reviewed_release_is_not_rediscovered(self) -> None:
        state = {
            "project": "BerriAI/litellm",
            "latest_verified": "1.99.0",
            "latest_automated_verified": "1.101.0",
        }
        release = {"tag_name": "v1.101.0"}
        status = watch.evaluate(state, release)
        self.assertFalse(status["update_available"])
        self.assertEqual(status["tracked"], "1.101.0")

    def test_equal_release_is_not_an_update(self) -> None:
        state = {"project": "BerriAI/litellm", "latest_verified": "1.101.0"}
        release = {"tag_name": "v1.101.0"}
        self.assertFalse(watch.evaluate(state, release)["update_available"])

    def test_rc_versions_are_not_accepted_as_stable_state(self) -> None:
        with self.assertRaises(ValueError):
            watch.version_key("1.102.0rc1")


if __name__ == "__main__":
    unittest.main()
