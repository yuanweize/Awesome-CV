#!/usr/bin/env python3
"""Package the Dify plugin from a clean staging tree and inspect the archive."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


EXCLUDED_NAMES = {".venv", ".env", ".DS_Store", "__pycache__"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".difypkg"}


def ignored(_directory: str, names: list[str]) -> set[str]:
    return {
        name
        for name in names
        if name in EXCLUDED_NAMES or any(name.endswith(suffix) for suffix in EXCLUDED_SUFFIXES)
    }


def inspect_package(path: Path) -> list[str]:
    errors: list[str] = []
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
    for name in names:
        parts = Path(name).parts
        if any(part in EXCLUDED_NAMES for part in parts):
            errors.append(f"forbidden local path in package: {name}")
        if Path(name).suffix in {".pyc", ".pyo"}:
            errors.append(f"compiled local file in package: {name}")
    required = {"manifest.yaml", "main.py", "pyproject.toml", "uv.lock"}
    missing = sorted(required - set(names))
    errors.extend(f"required package file missing: {name}" for name in missing)
    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=root / "integrations" / "dify" / "evidence-first-cv.difypkg",
    )
    args = parser.parse_args()
    cli = shutil.which("dify")
    if not cli:
        print("ERROR: Dify CLI not found; install it from the official Dify documentation", file=sys.stderr)
        return 2

    source = root / "integrations" / "dify" / "plugin"
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="evidence-first-cv-dify-") as directory:
        staged = Path(directory) / "plugin"
        shutil.copytree(source, staged, ignore=ignored)
        result = subprocess.run(
            [cli, "plugin", "package", str(staged), "--output_path", str(output)],
            check=False,
        )
    if result.returncode:
        return result.returncode
    errors = inspect_package(output)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Dify package OK: {output} ({output.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
