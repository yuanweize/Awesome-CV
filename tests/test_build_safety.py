from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "tools" / "author_slug.py"
sys.path.insert(0, str(ROOT / "tools"))

from safe_clean import clean, safe_build_path  # noqa: E402


class BuildSafetyTests(unittest.TestCase):
    def test_author_slug_accepts_normal_name(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "config.tex"
            config.write_text(r"\name{Alex}{Example}", encoding="utf-8")
            result = subprocess.run(
                ["python3", str(SCRIPT), str(config)],
                check=True,
                capture_output=True,
                text=True,
            )
        self.assertEqual("Alex_Example", result.stdout.strip())

    def test_author_slug_never_emits_shell_metacharacters(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "config.tex"
            config.write_text(r"\name{Alex;$(touch bad)}{O'Connor}", encoding="utf-8")
            result = subprocess.run(
                ["python3", str(SCRIPT), str(config)],
                check=True,
                capture_output=True,
                text=True,
            )
        slug = result.stdout.strip()
        self.assertRegex(slug, re.compile(r"^[A-Za-z0-9_]+$"))
        self.assertNotIn("$", slug)
        self.assertNotIn(";", slug)

    def test_missing_config_uses_public_fallback(self) -> None:
        result = subprocess.run(
            ["python3", str(SCRIPT), "/path/that/does/not/exist"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual("Awesome", result.stdout.strip())

    def test_clean_rejects_repository_root_and_parent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            with self.assertRaisesRegex(ValueError, "child of the repository"):
                safe_build_path(root, ".")
            with self.assertRaisesRegex(ValueError, "child of the repository"):
                safe_build_path(root, "../outside")

    def test_clean_removes_generated_files_but_preserves_unrelated_pdf(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            build = root / "build"
            build.mkdir()
            (build / "resume.pdf").write_bytes(b"generated")
            (root / "main.aux").write_text("generated", encoding="utf-8")
            keep = root / "evidence.pdf"
            keep.write_bytes(b"private evidence")

            clean(root, "build")

            self.assertFalse(build.exists())
            self.assertFalse((root / "main.aux").exists())
            self.assertTrue(keep.exists())

    def test_clean_unlinks_build_symlink_without_following_it(self) -> None:
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            root = Path(directory)
            protected = Path(outside) / "protected.txt"
            protected.write_text("keep", encoding="utf-8")
            (root / "build").symlink_to(Path(outside), target_is_directory=True)

            clean(root, "build")

            self.assertFalse((root / "build").exists())
            self.assertEqual("keep", protected.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
