#!/usr/bin/env python3
"""Plan or apply a verified move of private research into archive/research."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from archive_profile import (
    MANIFEST_NAME,
    inventory_profile,
    inventory_profile_for_verification,
    reject_symlink_components,
)


NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


def find_project_root() -> Path:
    for candidate in [Path.cwd(), *Path.cwd().parents, Path(__file__).resolve(), *Path(__file__).resolve().parents]:
        if candidate.is_file():
            candidate = candidate.parent
        if (candidate / "templates" / "master_cv.yaml.example").is_file():
            return candidate
    return Path.cwd()


def research_plan(root: Path, source_arg: Path, name: str, year: str) -> dict[str, Any]:
    if not NAME_PATTERN.fullmatch(name) or ".." in name:
        raise ValueError("archive name must use lowercase letters, numbers, dot, underscore, or hyphen")
    if not re.fullmatch(r"[0-9]{4}", year):
        raise ValueError("archive year must use four digits")

    root = Path(os.path.abspath(root))
    source = Path(os.path.abspath(source_arg if source_arg.is_absolute() else root / source_arg))
    allowed_roots = (root / "profiles", root / "meta" / "chat")
    if not any(source.is_relative_to(base) and source != base for base in allowed_roots):
        raise ValueError("research source must be inside profiles/ or meta/chat/")
    reject_symlink_components(source, "research source", root)
    if source.is_symlink() or not source.is_dir():
        raise ValueError(f"research source is missing or unsafe: {source}")

    destination = root / "archive" / "research" / year / name
    reject_symlink_components(destination.parent, "research archive destination", root)
    if destination.exists() or destination.is_symlink():
        raise ValueError(f"archive destination already exists: {destination}")

    files, total_bytes = inventory_profile(source)
    return {
        "schema_version": "1.0",
        "kind": "research",
        "name": name,
        "archived_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "source": str(source.relative_to(root)),
        "destination": str(destination.relative_to(root)),
        "file_count": len(files),
        "total_bytes": total_bytes,
        "files": files,
        "_source_path": source,
        "_destination_path": destination,
    }


def apply_research_archive(plan: dict[str, Any]) -> Path:
    source = Path(plan["_source_path"])
    destination = Path(plan["_destination_path"])
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(destination))

    public = {key: value for key, value in plan.items() if not key.startswith("_")}
    manifest = destination / MANIFEST_NAME
    manifest.write_text(json.dumps(public, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.chmod(destination.parent, 0o700)
    os.chmod(destination, 0o700)
    for path in destination.rglob("*"):
        os.chmod(path, 0o700 if path.is_dir() else 0o600)

    archived_files, archived_bytes = inventory_profile_for_verification(destination)
    if archived_files != plan["files"] or archived_bytes != plan["total_bytes"]:
        raise RuntimeError(f"research archive verification failed after move: {destination}")
    return destination


def main() -> int:
    root = find_project_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("name")
    parser.add_argument("--year", default=str(dt.date.today().year))
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    try:
        plan = research_plan(root, args.source, args.name, args.year)
        if not args.apply:
            print(
                f"Research archive plan: {plan['source']} -> {plan['destination']} "
                f"({plan['file_count']} files, {plan['total_bytes']} bytes)"
            )
            return 0
        destination = apply_research_archive(plan)
        print(f"Research archived and verified: {destination}")
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
