#!/usr/bin/env python3
"""Remove only generated CV build artifacts inside the repository root."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path


ROOT_AUX_SUFFIXES = (
    ".aux",
    ".log",
    ".out",
    ".toc",
    ".fls",
    ".dvi",
    ".synctex.gz",
)


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def safe_build_path(root: Path, build_dir: str) -> Path:
    """Resolve a build path without allowing cleanup outside *root*."""
    root = root.resolve()
    requested = Path(build_dir).expanduser()
    candidate = requested if requested.is_absolute() else root / requested
    # os.path.abspath collapses '..' lexically without following the final path
    # as Path.resolve() would. This keeps a build symlink removable while making
    # parent-directory traversal visible to the containment check.
    candidate = Path(os.path.abspath(candidate))

    if candidate == root or root not in candidate.parents:
        raise ValueError(f"build directory must be a child of the repository: {build_dir!r}")

    # A symlink in an intermediate directory could redirect shutil.rmtree outside
    # the repository even when the lexical path looks safe.
    resolved_parent = candidate.parent.resolve()
    if resolved_parent != root and root not in resolved_parent.parents:
        raise ValueError(f"build directory parent escapes the repository: {build_dir!r}")
    return candidate


def clean(root: Path, build_dir: str) -> list[Path]:
    root = root.resolve()
    target = safe_build_path(root, build_dir)
    removed: list[Path] = []

    if target.is_symlink():
        target.unlink()
        removed.append(target)
    elif target.is_dir():
        shutil.rmtree(target)
        removed.append(target)
    elif target.exists():
        raise ValueError(f"build path exists but is not a directory: {target}")

    for path in root.iterdir():
        if not path.is_file() and not path.is_symlink():
            continue
        if any(path.name.endswith(suffix) for suffix in ROOT_AUX_SUFFIXES):
            path.unlink()
            removed.append(path)
    return removed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-dir", default="build")
    args = parser.parse_args()
    try:
        removed = clean(project_root(), args.build_dir)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(f"Cleaned {len(removed)} generated path(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
