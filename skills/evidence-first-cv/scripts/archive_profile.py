#!/usr/bin/env python3
"""Plan or apply a verified, archive-first move of one private CV profile."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any


PROFILE_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
MANIFEST_NAME = "_archive_manifest.json"


def find_project_root() -> Path:
    for candidate in [Path.cwd(), *Path.cwd().parents, Path(__file__).resolve(), *Path(__file__).resolve().parents]:
        if candidate.is_file():
            candidate = candidate.parent
        if (candidate / "templates" / "master_cv.yaml.example").is_file():
            return candidate
    return Path.cwd()


def validate_profile_name(name: str) -> None:
    if not PROFILE_PATTERN.fullmatch(name) or ".." in name:
        raise ValueError(
            "profile name must use letters, numbers, dot, underscore, or hyphen; '..' is forbidden"
        )


def reject_symlink_components(path: Path, label: str, start: Path | None = None) -> None:
    if start is not None:
        current = start
        parts = path.relative_to(start).parts
    else:
        current = Path(path.anchor) if path.is_absolute() else Path.cwd()
        parts = path.parts[1:] if path.is_absolute() else path.parts
    for part in parts:
        current /= part
        if current.is_symlink():
            raise ValueError(f"{label} contains a symbolic-link path component: {current}")
        if not current.exists():
            break


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inventory_profile(source: Path) -> tuple[list[dict[str, Any]], int]:
    entries: list[dict[str, Any]] = []
    total_bytes = 0
    for path in sorted(source.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"archive refuses symbolic links: {path.relative_to(source)}")
        if not path.is_file():
            continue
        relative = path.relative_to(source).as_posix()
        if relative == MANIFEST_NAME:
            raise ValueError(f"reserved manifest already exists: {source / MANIFEST_NAME}")
        size = path.stat().st_size
        entries.append({"path": relative, "bytes": size, "sha256": file_sha256(path)})
        total_bytes += size
    return entries, total_bytes


def project_base_for_profiles(profiles_dir: Path) -> Path:
    """Return the repository root for both legacy and workspace/profiles layouts."""
    parent = profiles_dir.parent
    return parent.parent if parent.name == "workspace" else parent


def archive_plan(profiles_dir: Path, archive_dir: Path, name: str, year: str) -> dict[str, Any]:
    validate_profile_name(name)
    if not re.fullmatch(r"[0-9]{4}", year):
        raise ValueError("archive year must use four digits")
    profiles_dir = Path(os.path.abspath(profiles_dir))
    archive_dir = Path(os.path.abspath(archive_dir))
    project_base = project_base_for_profiles(profiles_dir)
    reject_symlink_components(profiles_dir, "profiles directory", project_base)
    archive_start = project_base if archive_dir.is_relative_to(project_base) else None
    reject_symlink_components(archive_dir, "archive directory", archive_start)
    if profiles_dir.is_symlink():
        raise ValueError(f"profiles directory must not be a symbolic link: {profiles_dir}")
    source = profiles_dir / name
    if source.is_symlink() or not source.is_dir():
        raise ValueError(f"profile is missing or unsafe: {source}")
    if archive_dir.is_symlink():
        raise ValueError(f"archive directory must not be a symbolic link: {archive_dir}")
    destination = archive_dir / year / name
    if destination.exists() or destination.is_symlink():
        raise ValueError(f"archive destination already exists: {destination}")

    files, total_bytes = inventory_profile(source)
    return {
        "schema_version": "1.0",
        "profile": name,
        "archived_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "source": source.relative_to(project_base).as_posix(),
        "destination": f"archive/applications/{year}/{name}",
        "file_count": len(files),
        "total_bytes": total_bytes,
        "files": files,
        "_source_path": source,
        "_destination_path": destination,
    }


def public_manifest(plan: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in plan.items() if not key.startswith("_")}


def apply_archive(plan: dict[str, Any]) -> Path:
    source = Path(plan["_source_path"])
    destination = Path(plan["_destination_path"])
    project_base = project_base_for_profiles(source.parent)
    reject_symlink_components(source, "profile source", project_base)
    destination_start = project_base if destination.is_relative_to(project_base) else None
    reject_symlink_components(destination.parent, "archive destination", destination_start)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.parent.is_symlink():
        raise ValueError(f"archive year directory must not be a symbolic link: {destination.parent}")

    manifest_path = source / MANIFEST_NAME
    temporary = source / f".{MANIFEST_NAME}.tmp"
    temporary.write_text(
        json.dumps(public_manifest(plan), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    os.chmod(temporary, 0o600)
    temporary.replace(manifest_path)
    source.rename(destination)

    for private_dir in (destination.parent, destination):
        os.chmod(private_dir, 0o700)
    for archived_path in destination.rglob("*"):
        os.chmod(archived_path, 0o700 if archived_path.is_dir() else 0o600)

    archived_files, archived_bytes = inventory_profile_for_verification(destination)
    expected = plan["files"]
    if archived_files != expected or archived_bytes != plan["total_bytes"]:
        raise RuntimeError(f"archive verification failed after move: {destination}")
    return destination


def inventory_profile_for_verification(source: Path) -> tuple[list[dict[str, Any]], int]:
    entries: list[dict[str, Any]] = []
    total_bytes = 0
    for path in sorted(source.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"archive contains symbolic link: {path.relative_to(source)}")
        relative = path.relative_to(source).as_posix()
        if not path.is_file() or relative == MANIFEST_NAME:
            continue
        size = path.stat().st_size
        entries.append({"path": relative, "bytes": size, "sha256": file_sha256(path)})
        total_bytes += size
    return entries, total_bytes


def main() -> int:
    root = find_project_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile")
    parser.add_argument("--year", default=str(dt.date.today().year))
    parser.add_argument(
        "--profiles-dir", type=Path, default=root / "workspace" / "profiles"
    )
    parser.add_argument("--archive-dir", type=Path, default=root / "archive" / "applications")
    parser.add_argument(
        "--active-file",
        type=Path,
        default=root / "workspace" / "current" / ".active_profile",
    )
    parser.add_argument("--apply", action="store_true", help="Move after inventory; default is dry-run")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    try:
        plan = archive_plan(args.profiles_dir, args.archive_dir, args.profile, args.year)
        if args.apply and args.active_file.is_file():
            active = args.active_file.read_text(encoding="utf-8").strip()
            if active == args.profile:
                raise ValueError("refusing to archive the active profile; switch profiles first")
        if args.as_json:
            print(json.dumps(public_manifest(plan), ensure_ascii=False, indent=2))
        else:
            print(
                f"Archive plan: {args.profile} -> {plan['destination']} "
                f"({plan['file_count']} files, {plan['total_bytes']} bytes)"
            )
        if not args.apply:
            print("Dry run only. Re-run with --apply after reviewing the plan.")
            return 0
        destination = apply_archive(plan)
        print(f"Archived and SHA-256 verified: {destination}")
        return 0
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
