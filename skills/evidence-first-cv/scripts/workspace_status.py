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


def visible_skill_count(path: Path) -> int:
    if not path.is_file() or path.is_symlink():
        return 0
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return 0
    return len(re.findall(r"^\s*\\cvskill(?:\s|$)", content, flags=re.MULTILINE))


def active_profile_state(root: Path, active: str) -> tuple[bool, list[str]]:
    if not active:
        return False, []
    workspace = root / "workspace"
    current = workspace / "current"
    profile = workspace / "profiles" / active
    if not profile.is_dir() or profile.is_symlink():
        return True, ["active profile is missing or unsafe"]
    differences: list[str] = []
    for name in PROFILE_FILES:
        if files_differ(current / name, profile / name):
            differences.append(name)
    for name in SECTION_FILES:
        if files_differ(current / "sections" / name, profile / "sections" / name):
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
    personal = master.get("personal_information", {})
    metadata = master.get("metadata", {})
    example_data = (
        isinstance(personal, dict)
        and personal.get("full_name") == "Alex Example"
    ) or (
        isinstance(metadata, dict)
        and metadata.get("owner") == "Alex Example"
    )
    claims = [item for item in master.get("claim_registry", []) if isinstance(item, dict)]
    eligible = [
        item
        for item in claims
        if item.get("cv_eligible") is True and item.get("status") in {"verified", "self_reported"}
    ]
    role_interests = sorted(
        (
            {
                "role_family": item.get("role_family", ""),
                "interest": item.get("interest", ""),
                "application_priority": item.get("application_priority", ""),
            }
            for item in master.get("career_preferences", {}).get("role_interests", [])
            if isinstance(item, dict) and isinstance(item.get("role_family"), str)
        ),
        key=lambda item: (
            {"high": 0, "medium": 1, "low": 2}.get(item["interest"], 3),
            {"active": 0, "selective": 1, "explore": 2, "paused": 3}.get(
                item["application_priority"], 4
            ),
            item["role_family"],
        ),
    )

    ledger = safe_yaml(root / "meta" / "applications.yaml")
    applications = [item for item in ledger.get("applications", []) if isinstance(item, dict)]
    stages = Counter(item.get("stage", "unknown") for item in applications)

    manifest_root = root / "meta" / "applications"
    manifests = sorted(manifest_root.glob("*/application.yaml")) if manifest_root.is_dir() else []
    manifest_stages = Counter(safe_yaml(path).get("stage", "unknown") for path in manifests)

    profiles_root = root / "workspace" / "profiles"
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

    baselines_root = root / "workspace" / "baselines"
    baseline_count, baseline_bytes = directory_inventory(baselines_root)
    baseline_names = (
        {
            item.name
            for item in baselines_root.iterdir()
            if item.is_dir() and not item.is_symlink()
        }
        if baselines_root.is_dir()
        else set()
    )

    catalog = safe_yaml(root / "meta" / "baseline_catalog.yaml")
    catalog_items = catalog.get("baselines", [])
    catalogued_baselines: set[str] = set()
    catalog_seen: set[str] = set()
    catalog_warnings: list[str] = []
    if catalog_items and not isinstance(catalog_items, list):
        catalog_warnings.append("baseline catalog entries must be a list")
        catalog_items = []
    for index, item in enumerate(catalog_items, 1):
        if not isinstance(item, dict):
            catalog_warnings.append(f"baseline catalog entry {index} is not a mapping")
            continue
        baseline_id = item.get("baseline")
        if (
            not isinstance(baseline_id, str)
            or not PROFILE_NAME_PATTERN.fullmatch(baseline_id)
            or ".." in baseline_id
        ):
            catalog_warnings.append(f"baseline catalog entry {index} has an unsafe baseline ID")
            continue
        if baseline_id in catalog_seen:
            catalog_warnings.append(f"duplicate baseline catalog entry: {baseline_id}")
            continue
        catalog_seen.add(baseline_id)
        role_family = item.get("role_family")
        if role_family not in master.get("role_families", {}):
            catalog_warnings.append(
                f"baseline catalog entry {baseline_id} has unknown role family {role_family!r}"
            )
            continue
        catalogued_baselines.add(baseline_id)

    linked_application_profiles = (ledger_profiles | manifest_profiles) & profile_names
    unclassified_profiles = profile_names - linked_application_profiles
    existing_baselines = catalogued_baselines & baseline_names
    unclassified_baselines = baseline_names - catalogued_baselines
    missing_catalog_baselines = catalogued_baselines - baseline_names
    archive_count = len(list((root / "archive" / "applications").glob("*/*"))) if (root / "archive" / "applications").is_dir() else 0
    research_archive_count = len(list((root / "archive" / "research").glob("*/*"))) if (root / "archive" / "research").is_dir() else 0

    active_file = root / "workspace" / "current" / ".active_profile"
    active = active_file.read_text(encoding="utf-8").strip() if active_file.is_file() and not active_file.is_symlink() else ""
    active_dirty, active_differences = active_profile_state(root, active)
    active_skill_entries = (
        visible_skill_count(root / "workspace" / "current" / "sections" / "skills.tex")
        if active
        else 0
    )
    empty_baseline_skills = sorted(
        baseline
        for baseline in existing_baselines
        if visible_skill_count(baselines_root / baseline / "sections" / "skills.tex") == 0
    )

    warnings: list[str] = []
    if not validation.get("ok"):
        warnings.append("private master database is invalid")
    if example_data:
        warnings.append(
            "master still contains fictional example data; replace it before drafting"
        )
    if not applications:
        warnings.append("application ledger is empty")
    if linked_application_profiles and not manifests:
        warnings.append(
            "legacy application profiles exist without manifests; create one for the next JD"
        )
    if active_dirty:
        warnings.append("working files differ from the active profile")
    if active and active_skill_entries == 0:
        warnings.append("active profile has no visible Skills entries")
    if empty_baseline_skills:
        warnings.append(
            "baselines have no visible Skills entries: "
            + ", ".join(empty_baseline_skills)
        )
    warnings.extend(catalog_warnings)
    if unclassified_profiles:
        warnings.append(
            "unclassified profile directories: " + ", ".join(sorted(unclassified_profiles))
        )
    if unclassified_baselines:
        warnings.append(
            "uncatalogued baseline directories: " + ", ".join(sorted(unclassified_baselines))
        )
    if missing_catalog_baselines:
        warnings.append(
            "baseline catalog references missing directories: "
            + ", ".join(sorted(missing_catalog_baselines))
        )
    if (root / "meta" / "profile_catalog.yaml").is_file():
        warnings.append(
            "legacy meta/profile_catalog.yaml remains; migrate reusable references to "
            "workspace/baselines/ and meta/baseline_catalog.yaml"
        )
    abandoned = root / "skills" / "drive-evidence-first-cv"
    if abandoned.is_dir() and not (abandoned / "SKILL.md").is_file():
        warnings.append("empty skills/drive-evidence-first-cv skeleton exists")

    return {
        "schema_version": "1.1",
        "master": {
            "valid": bool(validation.get("ok")),
            "example_data": example_data,
            "claims": len(claims),
            "eligible_claims": len(eligible),
            "evidence": len(master.get("evidence_registry", [])),
            "role_families": sorted(master.get("role_families", {})),
            "role_interests": role_interests,
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
            "active_skill_entries": active_skill_entries,
            "count": profile_count,
            "bytes": profile_bytes,
            "archived": archive_count,
            "archived_research": research_archive_count,
            "applications": len(linked_application_profiles),
            "unclassified": len(unclassified_profiles),
            "unclassified_names": sorted(unclassified_profiles),
        },
        "baselines": {
            "count": baseline_count,
            "bytes": baseline_bytes,
            "catalogued": len(existing_baselines),
            "uncatalogued": len(unclassified_baselines),
            "names": sorted(existing_baselines),
            "uncatalogued_names": sorted(unclassified_baselines),
            "empty_skill_entries": empty_baseline_skills,
        },
        "warnings": warnings,
    }


def render_text(status: dict[str, Any]) -> str:
    master = status["master"]
    applications = status["applications"]
    profiles = status["profiles"]
    baselines = status["baselines"]
    lines = [
        "Evidence-First CV workspace",
        f"Master: {'OK' if master['valid'] else 'INVALID'}; {master['eligible_claims']}/{master['claims']} eligible claims; "
        f"{master['evidence']} evidence records; roles={','.join(master['role_families'])}",
    ]
    if master["role_interests"]:
        lines.append(
            "Career directions: "
            + ", ".join(
                f"{item['role_family']} ({item['interest']}/{item['application_priority']})"
                for item in master["role_interests"]
            )
        )
    lines.extend(
        [
            f"Applications: {applications['records']} ledger records; {applications['manifests']} manifests; stages={applications['stages']}",
            f"Profiles: {profiles['count']} total ({profiles['applications']} application, "
            f"{profiles['unclassified']} unclassified); "
            f"{profiles['archived']} application archives, {profiles['archived_research']} research archives; "
            f"current={profiles['active'] or 'none'}; "
            f"dirty={'yes' if profiles['active_dirty'] else 'no'}",
            f"Baselines: {baselines['count']} total ({baselines['catalogued']} catalogued, "
            f"{baselines['uncatalogued']} uncatalogued)",
        ]
    )
    if baselines["names"]:
        lines.append("Baseline snapshots: " + ", ".join(baselines["names"]))
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
