#!/usr/bin/env python3
"""Create and validate the private decision record for one job application."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Any

import yaml


SCHEMA_VERSION = "1.0"
MANIFEST_STAGES = (
    "analysis",
    "awaiting-confirmation",
    "approved",
    "drafted",
    "validated",
    "sent",
    "closed",
)
PRIORITIES = {"must", "should", "nice"}
MATCH_LEVELS = {"direct", "adjacent", "gap"}
SECTIONS = {"headline", "summary", "projects", "experience", "education", "skills"}
ADJACENT_VALUES = {
    "execution_leverage",
    "delivery_risk_reduction",
    "cross_functional_bridge",
    "autonomy",
}
ADJACENT_SECTIONS = {"projects", "experience", "skills"}
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


def find_project_root() -> Path:
    for candidate in [Path.cwd(), *Path.cwd().parents, Path(__file__).resolve(), *Path(__file__).resolve().parents]:
        if candidate.is_file():
            candidate = candidate.parent
        if (candidate / "templates" / "master_cv.yaml.example").is_file():
            return candidate
    return Path.cwd()


def today() -> str:
    return dt.date.today().isoformat()


def slug(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return cleaned or "application"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_yaml(path: Path, label: str) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError(f"Cannot read {label} {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{label} root must be a mapping: {path}")
    return data


def master_index(path: Path) -> tuple[dict[str, dict[str, Any]], set[str]]:
    data = load_yaml(path, "master database")
    claims = {
        item["id"]: item
        for item in data.get("claim_registry", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    roles = set(data.get("role_families", {})) if isinstance(data.get("role_families"), dict) else set()
    return claims, roles


def new_manifest(
    application_id: str,
    company: str,
    title: str,
    role: str,
    jd_path: str,
    jd_hash: str,
    profile: str,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "application_id": application_id,
        "stage": "analysis",
        "created_at": today(),
        "updated_at": today(),
        "target": {
            "company": company,
            "title": title,
            "role_family": role,
            "profile": profile,
        },
        "job_description": {
            "path": jd_path,
            "sha256": jd_hash,
            "source_url": "",
        },
        "decision": {
            "recommendation": "review",
            "reason": "",
            "must_have_gaps": 0,
            "user_confirmed": False,
            "confirmed_at": "",
        },
        "questions": [],
        "requirements": [],
        "selected_claims": [],
        "adjacent_differentiators": [],
        "final_bullets": [],
        "artifacts": {
            "profile": profile,
            "cv_pdf": "",
            "cover_letter_pdf": "",
            "cv_sha256": "",
            "page_count": 0,
        },
        "quality": {
            "claim_audit": "pending",
            "ats_text_check": "pending",
            "visual_check": "pending",
            "privacy_check": "pending",
        },
    }


def validate_manifest(
    data: dict[str, Any],
    master_path: Path,
    project_root: Path,
    strict: bool = False,
) -> list[str]:
    errors: list[str] = []
    if str(data.get("schema_version", "")) != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION!r}")

    application_id = data.get("application_id")
    if not isinstance(application_id, str) or not ID_PATTERN.fullmatch(application_id):
        errors.append("application_id must contain lowercase letters, numbers, dots, underscores, or hyphens")

    stage = data.get("stage")
    if stage not in MANIFEST_STAGES:
        errors.append(f"stage must be one of: {', '.join(MANIFEST_STAGES)}")

    target = data.get("target")
    if not isinstance(target, dict):
        errors.append("target must be a mapping")
        target = {}
    for field in ("company", "title", "role_family"):
        if not isinstance(target.get(field), str) or not target.get(field, "").strip():
            errors.append(f"target.{field} is required")
    profile = target.get("profile")
    if not isinstance(profile, str) or not ID_PATTERN.fullmatch(profile):
        errors.append("target.profile must be a safe profile ID")

    claims, roles = master_index(master_path)
    role = target.get("role_family")
    if role and role not in roles:
        errors.append(f"unknown role family: {role}")

    job = data.get("job_description")
    if not isinstance(job, dict):
        errors.append("job_description must be a mapping")
        job = {}
    jd_path = job.get("path")
    expected_hash = job.get("sha256")
    if not isinstance(jd_path, str) or not jd_path:
        errors.append("job_description.path is required")
    else:
        candidate = (project_root / jd_path).resolve() if not Path(jd_path).is_absolute() else Path(jd_path).resolve()
        private_root = (project_root / "meta").resolve()
        if not candidate.is_relative_to(private_root):
            errors.append("job_description.path must stay under private meta/")
        elif not candidate.is_file():
            errors.append(f"job description file not found: {jd_path}")
        elif not isinstance(expected_hash, str) or sha256(candidate) != expected_hash:
            errors.append("job_description.sha256 does not match the saved JD")

    adjacent = data.get("adjacent_differentiators", [])
    if not isinstance(adjacent, list):
        errors.append("adjacent_differentiators must be a list")
        adjacent = []
    if len(adjacent) > 2:
        errors.append("adjacent_differentiators may contain at most two claims")
    adjacent_ids: set[str] = set()
    adjacent_placements: dict[str, str] = {}
    for index, item in enumerate(adjacent, 1):
        prefix = f"adjacent_differentiators[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be a mapping")
            continue
        claim_id = item.get("claim_id")
        if not isinstance(claim_id, str) or not ID_PATTERN.fullmatch(claim_id):
            errors.append(f"{prefix}.claim_id is invalid")
            continue
        if claim_id in adjacent_ids:
            errors.append(f"duplicate adjacent differentiator: {claim_id}")
        adjacent_ids.add(claim_id)
        value = item.get("value")
        if value not in ADJACENT_VALUES:
            errors.append(
                f"{prefix}.value must be one of: {', '.join(sorted(ADJACENT_VALUES))}"
            )
        placement = item.get("placement")
        if placement not in ADJACENT_SECTIONS:
            errors.append(f"{prefix}.placement must be projects, experience, or skills")
        else:
            adjacent_placements[claim_id] = placement
        if not isinstance(item.get("reason"), str) or not item.get("reason", "").strip():
            errors.append(f"{prefix}.reason is required")

    selected = data.get("selected_claims")
    if not isinstance(selected, list) or not all(isinstance(item, str) for item in selected):
        errors.append("selected_claims must be a list of claim IDs")
        selected = []
    selected_set = set(selected)
    if len(selected_set) != len(selected):
        errors.append("selected_claims contains duplicates")
    for claim_id in sorted(selected_set):
        claim = claims.get(claim_id)
        if claim is None:
            errors.append(f"selected_claims references unknown claim: {claim_id}")
            continue
        if claim.get("cv_eligible") is not True or claim.get("status") not in {"verified", "self_reported"}:
            errors.append(f"selected claim is not CV-eligible: {claim_id}")
        if role and role not in claim.get("role_families", []) and claim_id not in adjacent_ids:
            errors.append(f"selected claim {claim_id} is outside role family {role}")
    for claim_id in sorted(adjacent_ids):
        if claim_id not in selected_set:
            errors.append(
                f"adjacent differentiator is not present in selected_claims: {claim_id}"
            )

    requirements = data.get("requirements")
    if not isinstance(requirements, list):
        errors.append("requirements must be a list")
        requirements = []
    seen_requirements: set[str] = set()
    for index, requirement in enumerate(requirements, 1):
        prefix = f"requirements[{index}]"
        if not isinstance(requirement, dict):
            errors.append(f"{prefix} must be a mapping")
            continue
        requirement_id = requirement.get("id")
        if not isinstance(requirement_id, str) or not ID_PATTERN.fullmatch(requirement_id):
            errors.append(f"{prefix}.id is invalid")
        elif requirement_id in seen_requirements:
            errors.append(f"duplicate requirement ID: {requirement_id}")
        else:
            seen_requirements.add(requirement_id)
        if requirement.get("priority") not in PRIORITIES:
            errors.append(f"{prefix}.priority must be must, should, or nice")
        match = requirement.get("match")
        if match not in MATCH_LEVELS:
            errors.append(f"{prefix}.match must be direct, adjacent, or gap")
        mapped = requirement.get("claim_ids", [])
        if not isinstance(mapped, list) or not all(isinstance(item, str) for item in mapped):
            errors.append(f"{prefix}.claim_ids must be a list")
            mapped = []
        if match == "gap" and mapped:
            errors.append(f"{prefix} is a gap and cannot map claims")
        if match in {"direct", "adjacent"} and not mapped:
            errors.append(f"{prefix} needs at least one mapped claim")
        for claim_id in mapped:
            if claim_id not in selected_set:
                errors.append(f"{prefix} uses claim not present in selected_claims: {claim_id}")

    bullets = data.get("final_bullets")
    if not isinstance(bullets, list):
        errors.append("final_bullets must be a list")
        bullets = []
    seen_bullets: set[str] = set()
    for index, bullet in enumerate(bullets, 1):
        prefix = f"final_bullets[{index}]"
        if not isinstance(bullet, dict):
            errors.append(f"{prefix} must be a mapping")
            continue
        bullet_id = bullet.get("id")
        if not isinstance(bullet_id, str) or not ID_PATTERN.fullmatch(bullet_id):
            errors.append(f"{prefix}.id is invalid")
        elif bullet_id in seen_bullets:
            errors.append(f"duplicate bullet ID: {bullet_id}")
        else:
            seen_bullets.add(bullet_id)
        if bullet.get("section") not in SECTIONS:
            errors.append(f"{prefix}.section is invalid")
        if not isinstance(bullet.get("text"), str) or not bullet.get("text", "").strip():
            errors.append(f"{prefix}.text is required")
        mapped = bullet.get("claim_ids", [])
        if not isinstance(mapped, list) or not mapped:
            errors.append(f"{prefix}.claim_ids must contain at least one claim")
            mapped = []
        for claim_id in mapped:
            if claim_id not in selected_set:
                errors.append(f"{prefix} uses claim not present in selected_claims: {claim_id}")
            placement = adjacent_placements.get(claim_id)
            if placement and bullet.get("section") != placement:
                errors.append(
                    f"{prefix} places adjacent claim {claim_id} in {bullet.get('section')}; "
                    f"approved placement is {placement}"
                )

    decision = data.get("decision")
    if not isinstance(decision, dict):
        errors.append("decision must be a mapping")
        decision = {}
    if decision.get("recommendation") not in {"review", "apply", "stretch", "defer"}:
        errors.append("decision.recommendation must be review, apply, stretch, or defer")

    if strict:
        if not requirements:
            errors.append("strict validation requires parsed requirements")
        if not selected:
            errors.append("strict validation requires selected_claims")
        if stage in {"approved", "drafted", "validated", "sent", "closed"} and not decision.get("user_confirmed"):
            errors.append(f"stage {stage} requires decision.user_confirmed=true")
        if stage in {"drafted", "validated", "sent", "closed"} and not bullets:
            errors.append(f"stage {stage} requires final_bullets")

    return errors


def save_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    temporary.replace(path)
    os.chmod(path, 0o600)


def command_init(args: argparse.Namespace, root: Path) -> int:
    _, roles = master_index(args.master)
    if args.role not in roles:
        raise ValueError(f"unknown role family {args.role!r}; available: {', '.join(sorted(roles))}")
    if not args.jd.is_file():
        raise ValueError(f"JD file not found: {args.jd}")
    application_id = args.id or f"{today().replace('-', '')}-{slug(args.company)}-{slug(args.title)}"
    if not ID_PATTERN.fullmatch(application_id):
        raise ValueError("application ID is unsafe")
    application_dir = root / "meta" / "applications" / application_id
    if application_dir.exists() or application_dir.is_symlink():
        raise ValueError(f"application already exists: {application_dir}")
    application_dir.mkdir(parents=True, mode=0o700)
    jd_target = application_dir / "jd.md"
    shutil.copyfile(args.jd, jd_target)
    os.chmod(jd_target, 0o600)
    relative_jd = jd_target.relative_to(root).as_posix()
    profile = args.profile or application_id
    if not ID_PATTERN.fullmatch(profile):
        raise ValueError("profile name is unsafe")
    manifest = new_manifest(
        application_id,
        args.company,
        args.title,
        args.role,
        relative_jd,
        sha256(jd_target),
        profile,
    )
    manifest_path = application_dir / "application.yaml"
    save_yaml(manifest_path, manifest)
    print(manifest_path.relative_to(root))
    return 0


def command_validate(args: argparse.Namespace, root: Path) -> int:
    data = load_yaml(args.manifest, "application manifest")
    errors = validate_manifest(data, args.master, root, strict=args.strict)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(
        f"OK: {data.get('application_id')} stage={data.get('stage')} "
        f"requirements={len(data.get('requirements', []))} claims={len(data.get('selected_claims', []))} "
        f"bullets={len(data.get('final_bullets', []))}"
    )
    return 0


def main() -> int:
    root = find_project_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--master", type=Path, default=root / "meta" / "master_cv.yaml")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init", help="Create a private application/JD workspace")
    init.add_argument("--company", required=True)
    init.add_argument("--title", required=True)
    init.add_argument("--role", required=True)
    init.add_argument("--jd", required=True, type=Path)
    init.add_argument("--profile")
    init.add_argument("--id")

    validate = subparsers.add_parser("validate", help="Validate one application manifest")
    validate.add_argument("manifest", type=Path)
    validate.add_argument("--strict", action="store_true")

    args = parser.parse_args()
    try:
        if args.command == "init":
            return command_init(args, root)
        return command_validate(args, root)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
