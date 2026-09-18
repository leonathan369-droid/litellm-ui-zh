from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "build_patch.py"

spec = importlib.util.spec_from_file_location("litellm_ui_zh_builder", BUILDER)
assert spec and spec.loader
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class BuildPatchTest(unittest.TestCase):
    def test_repository_dist_is_reproducible(self) -> None:
        expected = builder.build(builder.DEFAULT_LOCALE, builder.DEFAULT_SOURCE)
        actual = builder.DEFAULT_OUTPUT.read_text(encoding="utf-8")
        self.assertEqual(actual, expected)

    def test_locale_requires_string_to_string_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            locale = root / "locale.json"
            source = root / "overlay.js"
            locale.write_text(json.dumps({"User": 123}), encoding="utf-8")
            source.write_text(
                "var translations = __LITELLM_ZH_TRANSLATIONS__;",
                encoding="utf-8",
            )
            with self.assertRaises(SystemExit):
                builder.build(locale, source)


if __name__ == "__main__":
    unittest.main()
