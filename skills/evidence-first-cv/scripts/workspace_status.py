#!/usr/bin/env python3
"""Report the private CV workspace state before an AI starts an application."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from validate_master_cv import validate_master_cv


PROFILE_FILES = ("config.tex", "letter_config.tex")
SECTION_FILES = (
    "summary.tex",
    "experience.tex",
    "skills.tex",
    "letter_body.tex",
    "education.tex",
    "certificates.tex",
    "honors.tex",
)
PROFILE_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def find_project_root() -> Path:
    for candidate in [Path.cwd(), *Path.cwd().parents, Path(__file__).resolve(), *Path(__file__).resolve().parents]:
        if candidate.is_file():
            candidate = candidate.parent
        if (candidate / "templates" / "master_cv.yaml.example").is_file():
            return candidate
    return Path.cwd()


def safe_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return {}
    return data if isinstance(data, dict) else {}


def files_differ(left: Path, right: Path) -> bool:
    if left.is_file() != right.is_file():
        return True
    return left.is_file() and left.read_bytes() != right.read_bytes()


def active_profile_state(root: Path, active: str) -> tuple[bool, list[str]]:
    if not active:
        return False, []
    profile = root / "profiles" / active
    if not profile.is_dir() or profile.is_symlink():
        return True, ["active profile is missing or unsafe"]
    differences: list[str] = []
    for name in PROFILE_FILES:
        if files_differ(root / name, profile / name):
            differences.append(name)
    for name in SECTION_FILES:
        if files_differ(root / "sections" / name, profile / "sections" / name):
            differences.append(f"sections/{name}")
    return bool(differences), differences


def directory_inventory(path: Path) -> tuple[int, int]:
    directories = [item for item in path.iterdir() if item.is_dir() and not item.is_symlink()] if path.is_dir() else []
    total_bytes = 0
    for directory in directories:
        total_bytes += sum(item.stat().st_size for item in directory.rglob("*") if item.is_file() and not item.is_symlink())
    return len(directories), total_bytes


def collect_status(root: Path) -> dict[str, Any]:
    master_path = root / "meta" / "master_cv.yaml"
    validation = validate_master_cv(master_path)
    master = safe_yaml(master_path)
    claims = [item for item in master.get("claim_registry", []) if isinstance(item, dict)]
    eligible = [
        item
        for item in claims
        if item.get("cv_eligible") is True and item.get("status") in {"verified", "self_reported"}
    ]

    ledger = safe_yaml(root / "meta" / "applications.yaml")
    applications = [item for item in ledger.get("applications", []) if isinstance(item, dict)]
    stages = Counter(item.get("stage", "unknown") for item in applications)

    manifest_root = root / "meta" / "applications"
    manifests = sorted(manifest_root.glob("*/application.yaml")) if manifest_root.is_dir() else []
    manifest_stages = Counter(safe_yaml(path).get("stage", "unknown") for path in manifests)

    profiles_root = root / "profiles"
    profile_count, profile_bytes = directory_inventory(profiles_root)
    profile_names = (
        {
            item.name
            for item in profiles_root.iterdir()
            if item.is_dir() and not item.is_symlink()
        }
        if profiles_root.is_dir()
        else set()
    )

    ledger_profiles = {
        item.get("profile")
        for item in applications
        if isinstance(item.get("profile"), str) and item.get("profile")
    }
    manifest_profiles = {
        target.get("profile")
        for path in manifests
        for target in [safe_yaml(path).get("target", {})]
        if isinstance(target, dict)
        and isinstance(target.get("profile"), str)
        and target.get("profile")
    }

    catalog = safe_yaml(root / "meta" / "profile_catalog.yaml")
    catalog_items = catalog.get("profiles", [])
    reference_profiles: set[str] = set()
    catalog_seen: set[str] = set()
    catalog_warnings: list[str] = []
    if catalog_items and not isinstance(catalog_items, list):
        catalog_warnings.append("profile catalog entries must be a list")
        catalog_items = []
    for index, item in enumerate(catalog_items, 1):
        if not isinstance(item, dict):
            catalog_warnings.append(f"profile catalog entry {index} is not a mapping")
            continue
        profile_id = item.get("profile")
        kind = item.get("kind")
        if (
            not isinstance(profile_id, str)
            or not PROFILE_NAME_PATTERN.fullmatch(profile_id)
            or ".." in profile_id
        ):
            catalog_warnings.append(f"profile catalog entry {index} has an unsafe profile ID")
            continue
        if profile_id in catalog_seen:
            catalog_warnings.append(f"duplicate profile catalog entry: {profile_id}")
            continue
        catalog_seen.add(profile_id)
        if kind != "reference":
            catalog_warnings.append(f"profile catalog entry {profile_id} must use kind 'reference'")
            continue
        role_family = item.get("role_family")
        if role_family not in master.get("role_families", {}):
            catalog_warnings.append(
                f"profile catalog entry {profile_id} has unknown role family {role_family!r}"
            )
            continue
        reference_profiles.add(profile_id)

    linked_application_profiles = (ledger_profiles | manifest_profiles) & profile_names
    existing_reference_profiles = reference_profiles & profile_names
    overlapping_profiles = linked_application_profiles & existing_reference_profiles
    unclassified_profiles = profile_names - linked_application_profiles - existing_reference_profiles
    missing_catalog_profiles = reference_profiles - profile_names
    archive_count = len(list((root / "archive" / "applications").glob("*/*"))) if (root / "archive" / "applications").is_dir() else 0
    research_archive_count = len(list((root / "archive" / "research").glob("*/*"))) if (root / "archive" / "research").is_dir() else 0

    active_file = root / ".active_profile"
    active = active_file.read_text(encoding="utf-8").strip() if active_file.is_file() and not active_file.is_symlink() else ""
    active_dirty, active_differences = active_profile_state(root, active)

    warnings: list[str] = []
    if not validation.get("ok"):
        warnings.append("private master database is invalid")
    if not applications:
        warnings.append("application ledger is empty")
    if profile_count and not manifests:
        if applications:
            warnings.append("legacy profiles/ledger exist without manifests; create one for the next JD")
        else:
            warnings.append("profiles exist but no application manifests have been created")
    if active_dirty:
        warnings.append("working files differ from the active profile")
    warnings.extend(catalog_warnings)
    if overlapping_profiles:
        warnings.append(
            "profiles classified as both application and reference: "
            + ", ".join(sorted(overlapping_profiles))
        )
    if unclassified_profiles:
        warnings.append(
            "unclassified profile directories: " + ", ".join(sorted(unclassified_profiles))
        )
    if missing_catalog_profiles:
        warnings.append(
            "profile catalog references missing directories: "
            + ", ".join(sorted(missing_catalog_profiles))
        )
    abandoned = root / "skills" / "drive-evidence-first-cv"
    if abandoned.is_dir() and not (abandoned / "SKILL.md").is_file():
        warnings.append("empty skills/drive-evidence-first-cv skeleton exists")

    return {
        "schema_version": "1.0",
        "master": {
            "valid": bool(validation.get("ok")),
            "claims": len(claims),
            "eligible_claims": len(eligible),
            "evidence": len(master.get("evidence_registry", [])),
            "role_families": sorted(master.get("role_families", {})),
        },
        "applications": {
            "records": len(applications),
            "stages": dict(sorted(stages.items())),
            "manifests": len(manifests),
            "manifest_stages": dict(sorted(manifest_stages.items())),
        },
        "profiles": {
            "active": active,
            "active_dirty": active_dirty,
            "active_differences": active_differences,
            "count": profile_count,
            "bytes": profile_bytes,
            "archived": archive_count,
            "archived_research": research_archive_count,
            "applications": len(linked_application_profiles),
            "references": len(existing_reference_profiles),
            "unclassified": len(unclassified_profiles),
            "reference_names": sorted(existing_reference_profiles),
            "unclassified_names": sorted(unclassified_profiles),
        },
        "warnings": warnings,
    }


def render_text(status: dict[str, Any]) -> str:
    master = status["master"]
    applications = status["applications"]
    profiles = status["profiles"]
    lines = [
        "Evidence-First CV workspace",
        f"Master: {'OK' if master['valid'] else 'INVALID'}; {master['eligible_claims']}/{master['claims']} eligible claims; "
        f"{master['evidence']} evidence records; roles={','.join(master['role_families'])}",
        f"Applications: {applications['records']} ledger records; {applications['manifests']} manifests; stages={applications['stages']}",
        f"Profiles: {profiles['count']} total ({profiles['applications']} application, "
        f"{profiles['references']} reference, {profiles['unclassified']} unclassified); "
        f"{profiles['archived']} application archives, {profiles['archived_research']} research archives; "
        f"current={profiles['active'] or 'none'}; "
        f"dirty={'yes' if profiles['active_dirty'] else 'no'}",
    ]
    if profiles["reference_names"]:
        lines.append("Reference profiles: " + ", ".join(profiles["reference_names"]))
    if profiles["active_differences"]:
        lines.append("Active differences: " + ", ".join(profiles["active_differences"]))
    if status["warnings"]:
        lines.append("Warnings:")
        lines.extend(f"- {warning}" for warning in status["warnings"])
    else:
        lines.append("Warnings: none")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    status = collect_status(find_project_root())
    if args.as_json:
        print(json.dumps(status, ensure_ascii=False, indent=2))
    else:
        print(render_text(status))
    return 0 if status["master"]["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
