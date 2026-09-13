#!/usr/bin/env python3
"""Build the public synthetic CV without reading a local user instance."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def find_project_root(start: Path | None = None) -> Path:
    """Find the public checkout without importing compatibility wrappers."""
    origin = (start or Path.cwd()).resolve()
    candidates = (origin, *origin.parents, Path(__file__).resolve(), *Path(__file__).resolve().parents)
    for candidate in candidates:
        if candidate.is_file():
            candidate = candidate.parent
        if (candidate / "templates" / "config.tex.example").is_file() and (
            candidate / "src" / "main.tex"
        ).is_file():
            return candidate
    raise ValueError("cannot locate the Awesome-CV repository root")


def build_demo(root: Path, output_dir: Path) -> Path:
    root = root.resolve()
    output_dir = output_dir.resolve()
    allowed_output = (root / "output").resolve()
    if not output_dir.is_relative_to(allowed_output):
        raise ValueError("demo output must stay under output/")
    if output_dir.is_symlink():
        raise ValueError("demo output directory must not be a symbolic link")
    if shutil.which("lualatex") is None:
        raise ValueError("lualatex is required; run './cv doctor' for dependency guidance")

    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / "Awesome-CV_Demo_CV.pdf"
    if destination.is_symlink():
        raise ValueError("demo output must not be a symbolic link")

    with tempfile.TemporaryDirectory(prefix="awesome-cv-demo-") as directory:
        demo_root = Path(directory)
        shutil.copytree(root / "src", demo_root / "src")
        shutil.copytree(root / "templates", demo_root / "templates")
        current = demo_root / "workspace" / "current"
        shutil.copytree(demo_root / "templates" / "sections", current / "sections")
        shutil.copy2(demo_root / "templates" / "config.tex.example", current / "config.tex")
        shutil.copy2(
            demo_root / "templates" / "letter_config.tex.example",
            current / "letter_config.tex",
        )
        build = demo_root / "build"
        build.mkdir()
        environment = os.environ.copy()
        environment["TEXINPUTS"] = f"{demo_root / 'src'}:{demo_root}:"
        cache_root = Path(tempfile.gettempdir()) / "awesome-cv-demo-tex-cache"
        environment.setdefault("TEXMFVAR", str(cache_root / "var"))
        environment.setdefault("TEXMFCONFIG", str(cache_root / "config"))
        environment.setdefault("TEXMFCACHE", str(cache_root / "var"))
        command = [
            "lualatex",
            "-interaction=nonstopmode",
            "-halt-on-error",
            f"-output-directory={build}",
            "-jobname=Awesome-CV_Demo_CV",
            "src/main.tex",
        ]
        for _ in range(2):
            completed = subprocess.run(
                command,
                cwd=demo_root,
                env=environment,
                check=False,
                capture_output=True,
                text=True,
            )
            if completed.returncode != 0:
                tail = "\n".join((completed.stdout + completed.stderr).splitlines()[-30:])
                raise ValueError(f"synthetic demo build failed:\n{tail}")
        shutil.copy2(build / destination.name, destination)
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, help="repository root; auto-detected by default")
    parser.add_argument("--output-dir", type=Path, help="destination under output/")
    args = parser.parse_args()
    try:
        root = args.root.resolve() if args.root else find_project_root()
        output_dir = args.output_dir or root / "output" / "demo"
        pdf = build_demo(root, output_dir)
    except (OSError, ValueError) as exc:
        print(f"Demo build failed: {exc}", file=sys.stderr)
        return 2
    print(f"Synthetic demo built: {pdf.relative_to(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
