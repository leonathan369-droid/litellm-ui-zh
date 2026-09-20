from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "collect_strings.py"

spec = importlib.util.spec_from_file_location("collect_strings", SCRIPT)
assert spec and spec.loader
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)


class CollectStringsTest(unittest.TestCase):
    def test_collects_visible_text_and_attributes_but_skips_code(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "index.html").write_text(
                '<html><body><h1>New Dashboard Label</h1>'
                '<input placeholder="Search something new">'
                '<code>UserService</code>'
                '<script>var x = "Hidden Script Text";</script>'
                '</body></html>',
                encoding="utf-8",
            )
            values = collector.collect(root)
            self.assertIn("New Dashboard Label", values)
            self.assertIn("Search something new", values)
            self.assertNotIn("UserService", values)
            self.assertNotIn("Hidden Script Text", values)


if __name__ == "__main__":
    unittest.main()
