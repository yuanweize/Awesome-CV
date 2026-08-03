#!/usr/bin/env python3
"""Safely initialize the ignored runtime layer of an Awesome-CV workspace."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Callable


RUNTIME_DIRECTORIES = (
    "meta",
    "meta/applications",
    "meta/evidence",
    "meta/inventory",
    "meta/audits",
    "baselines",
    "profiles",
    "archive/applications",
    "archive/research",
    "sections",
    "build",
    "tmp",
)

TEMPLATE_FILES = (
    ("templates/meta_README.md.example", "meta/README.md"),
    ("templates/master_cv.yaml.example", "meta/master_cv.yaml"),
    ("templates/applications.yaml.example", "meta/applications.yaml"),
    ("templates/baseline_catalog.yaml.example", "meta/baseline_catalog.yaml"),
    ("templates/config.tex.example", "config.tex"),
    ("templates/letter_config.tex.example", "letter_config.tex"),
)

SECTION_TEMPLATE_NAMES = (
    "certificates.tex",
    "education.tex",
    "experience.tex",
    "honors.tex",
    "letter_body.tex",
    "order.tex",
    "skills.tex",
    "summary.tex",
)


def find_project_root(start: Path | None = None) -> Path:
    """Find a checkout that contains the public initialization templates."""
    origin = (start or Path.cwd()).resolve()
    candidates = (origin, *origin.parents, Path(__file__).resolve(), *Path(__file__).resolve().parents)
    for candidate in candidates:
        if candidate.is_file():
            candidate = candidate.parent
        if (candidate / "templates" / "master_cv.yaml.example").is_file():
            return candidate
    raise ValueError(
        "Awesome-CV repository root not found. Clone the repository, then run "
        "'./cv init' from inside it."
    )


def _assert_safe_path(root: Path, path: Path, *, destination: bool) -> None:
    """Reject links and paths that escape the selected workspace root."""
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"Path escapes workspace root: {path}") from exc

    relative = path.relative_to(root)
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            kind = "destination" if destination else "template"
            raise ValueError(f"Unsafe symbolic-link {kind}: {current}")


def _private_mode(path: Path) -> None:
    """Restrict newly created private files where POSIX permissions are available."""
    try:
        path.chmod(0o600)
    except OSError:
        pass


def _private_directory_mode(path: Path) -> None:
    try:
        path.chmod(0o700)
    except OSError:
        pass


def initialize_workspace(
    root: Path,
    *,
    emit: Callable[[str], None] | None = None,
) -> dict[str, list[str]]:
    """Create the private runtime layer without replacing any existing file."""
    root = root.resolve()
    template_root = root / "templates"
    if not (template_root / "master_cv.yaml.example").is_file():
        raise ValueError(f"Public templates are missing under {template_root}")

    result: dict[str, list[str]] = {
        "created_directories": [],
        "created_files": [],
        "preserved_files": [],
    }

    mappings = list(TEMPLATE_FILES)
    mappings.extend(
        (f"templates/sections/{name}", f"sections/{name}")
        for name in SECTION_TEMPLATE_NAMES
    )
    for source_relative, _ in mappings:
        source = root / source_relative
        _assert_safe_path(root, source, destination=False)
        if not source.is_file():
            raise ValueError(f"Required public template is missing: {source}")

    for relative in RUNTIME_DIRECTORIES:
        destination = root / relative
        _assert_safe_path(root, destination, destination=True)
        if destination.exists() and not destination.is_dir():
            raise ValueError(f"Expected a directory but found a file: {destination}")
        if not destination.exists():
            destination.mkdir(parents=True, exist_ok=False)
            _private_directory_mode(destination)
            result["created_directories"].append(relative)

    for source_relative, destination_relative in mappings:
        source = root / source_relative
        destination = root / destination_relative
        _assert_safe_path(root, destination, destination=True)
        if destination.exists():
            if not destination.is_file():
                raise ValueError(f"Expected a file but found another object: {destination}")
            result["preserved_files"].append(destination_relative)
            continue
        shutil.copy2(source, destination)
        _private_mode(destination)
        result["created_files"].append(destination_relative)

    if emit:
        for relative in result["created_directories"]:
            emit(f"Created private directory: {relative}/")
        for relative in result["created_files"]:
            emit(f"Created private file: {relative}")
        for relative in result["preserved_files"]:
            emit(f"Preserved existing file: {relative}")

    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Initialize Awesome-CV private memory, profiles, archives, and build paths safely."
    )
    parser.add_argument("--root", type=Path, help="Repository root; auto-detected by default")
    parser.add_argument("--json", action="store_true", help="Print a machine-readable result")
    args = parser.parse_args()

    try:
        root = args.root.resolve() if args.root else find_project_root()
        result = initialize_workspace(root, emit=None if args.json else print)
    except (OSError, ValueError) as exc:
        print(f"Initialization failed: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps({"root": str(root), **result}, indent=2))
    else:
        print("\nWorkspace ready. Public example data was copied only into ignored paths.")
        print("Directory map: meta/README.md")
        print("Next: replace the fictional master data, run './cv validate --strict',")
        print("then tell the agent you want a new CV and provide the complete JD.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
