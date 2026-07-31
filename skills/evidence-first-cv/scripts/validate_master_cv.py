#!/usr/bin/env python3
"""Validate the evidence-first Awesome-CV master database."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml


ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
ALLOWED_STATUSES = {"verified", "self_reported", "planned", "unverified", "expired"}
ALLOWED_DEPTHS = {"strong", "moderate", "limited"}
ALLOWED_VISIBILITY = {"public", "private", "self_reported"}
INELIGIBLE_STATUSES = {"planned", "unverified", "expired"}
REQUIRED_TOP_LEVEL = {
    "personal_information",
    "education",
    "work_experience",
    "technical_skills",
    "languages",
}


def find_project_root() -> Path:
    candidates = [Path.cwd(), *Path.cwd().parents, Path(__file__).resolve(), *Path(__file__).resolve().parents]
    for candidate in candidates:
        if candidate.is_file():
            candidate = candidate.parent
        if (candidate / "templates" / "master_cv.yaml.example").is_file():
            return candidate
    return Path.cwd()


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _list_of_strings(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(_is_nonempty_string(item) for item in value)


def _validate_identifier(value: Any, label: str, errors: list[str]) -> None:
    if not _is_nonempty_string(value) or not ID_PATTERN.fullmatch(value):
        errors.append(f"{label} must match {ID_PATTERN.pattern!r}: {value!r}")


def validate_master_cv(yaml_path: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    if not yaml_path.exists():
        return {"ok": False, "errors": [f"File not found: {yaml_path}"], "warnings": []}

    try:
        data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        return {"ok": False, "errors": [f"Invalid YAML: {exc}"], "warnings": []}

    if not isinstance(data, dict):
        return {"ok": False, "errors": ["The YAML root must be a mapping"], "warnings": []}

    missing = sorted(REQUIRED_TOP_LEVEL - set(data))
    errors.extend(f"Missing required top-level section: {key}" for key in missing)

    personal = data.get("personal_information", {})
    if not isinstance(personal, dict):
        errors.append("personal_information must be a mapping")
        personal = {}
    for field in ("full_name", "email", "location"):
        if not _is_nonempty_string(personal.get(field)):
            errors.append(f"personal_information.{field} is required")

    education = data.get("education", {})
    if not isinstance(education, dict):
        errors.append("education must be a mapping")
        education = {}
    for field in ("institution", "degree"):
        if not _is_nonempty_string(education.get(field)):
            errors.append(f"education.{field} is required")

    experience = data.get("work_experience", [])
    if not isinstance(experience, list):
        errors.append("work_experience must be a list")
        experience = []
    else:
        for index, item in enumerate(experience, 1):
            if not isinstance(item, dict):
                errors.append(f"work_experience[{index}] must be a mapping")
                continue
            for field in ("company", "dates"):
                if not _is_nonempty_string(item.get(field)):
                    errors.append(f"work_experience[{index}].{field} is required")

    skills = data.get("technical_skills", {})
    if not isinstance(skills, dict) or not skills:
        errors.append("technical_skills must be a non-empty mapping")

    languages = data.get("languages", [])
    if not isinstance(languages, list) or not languages:
        errors.append("languages must be a non-empty list")

    schema_version = str(data.get("schema_version", "legacy"))
    is_v3 = schema_version.startswith("3.")
    if not is_v3:
        warnings.append(
            "Legacy master database: add schema_version 3.x, role_families, "
            "evidence_registry, and claim_registry for safe JD targeting"
        )

    metadata = data.get("metadata", {})
    if is_v3 and not isinstance(metadata, dict):
        errors.append("metadata must be a mapping for schema 3.x")
        metadata = {}
    if is_v3:
        for field in ("owner", "last_updated", "default_language"):
            if not _is_nonempty_string(metadata.get(field)):
                errors.append(f"metadata.{field} is required")

    privacy = data.get("privacy", {})
    if is_v3 and not isinstance(privacy, dict):
        errors.append("privacy must be a mapping for schema 3.x")
        privacy = {}
    if is_v3 and not isinstance(privacy.get("ai_context_include_contact"), bool):
        errors.append("privacy.ai_context_include_contact must be true or false")
    elif is_v3 and privacy.get("ai_context_include_contact"):
        errors.append("privacy.ai_context_include_contact must remain false; contact export requires an explicit CLI flag")
    if is_v3 and not _list_of_strings(privacy.get("sensitive_fields", [])):
        errors.append("privacy.sensitive_fields must be a non-empty list of strings")

    role_families = data.get("role_families", {})
    if is_v3 and (not isinstance(role_families, dict) or not role_families):
        errors.append("role_families must be a non-empty mapping for schema 3.x")
        role_families = {}
    elif not isinstance(role_families, dict):
        errors.append("role_families must be a mapping")
        role_families = {}
    for role_id, role in role_families.items():
        _validate_identifier(role_id, "role family ID", errors)
        if not isinstance(role, dict) or not _is_nonempty_string(role.get("label")):
            errors.append(f"role_families.{role_id}.label is required")
        keywords = role.get("keywords", []) if isinstance(role, dict) else []
        titles = role.get("target_titles", []) if isinstance(role, dict) else []
        if not _list_of_strings(keywords):
            errors.append(f"role_families.{role_id}.keywords must be a non-empty list of strings")
        if not _list_of_strings(titles):
            errors.append(f"role_families.{role_id}.target_titles must be a non-empty list of strings")

    evidence_items = data.get("evidence_registry", [])
    if is_v3 and (not isinstance(evidence_items, list) or not evidence_items):
        errors.append("evidence_registry must be a non-empty list for schema 3.x")
        evidence_items = []
    elif not isinstance(evidence_items, list):
        errors.append("evidence_registry must be a list")
        evidence_items = []

    evidence_by_id: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(evidence_items, 1):
        if not isinstance(item, dict):
            errors.append(f"evidence_registry[{index}] must be a mapping")
            continue
        evidence_id = item.get("id")
        _validate_identifier(evidence_id, f"evidence_registry[{index}].id", errors)
        if evidence_id in evidence_by_id:
            errors.append(f"Duplicate evidence ID: {evidence_id}")
        elif _is_nonempty_string(evidence_id):
            evidence_by_id[evidence_id] = item
        for field in ("type", "title", "locator", "visibility"):
            if not _is_nonempty_string(item.get(field)):
                errors.append(f"evidence_registry[{index}].{field} is required")
        visibility = item.get("visibility")
        if visibility not in ALLOWED_VISIBILITY:
            errors.append(
                f"evidence_registry[{index}].visibility must be one of {sorted(ALLOWED_VISIBILITY)}"
            )
        if not _is_nonempty_string(item.get("verified_on")):
            errors.append(f"evidence_registry[{index}].verified_on is required")
        locator = item.get("locator", "")
        if visibility == "public" and not str(locator).startswith(("https://", "http://")):
            errors.append(f"evidence_registry[{index}].locator must be an HTTP(S) URL for public evidence")
        if visibility in {"private", "self_reported"} and not str(locator).startswith("private:"):
            errors.append(f"evidence_registry[{index}].locator must use a private: symbolic locator")

    claims = data.get("claim_registry", [])
    if is_v3 and (not isinstance(claims, list) or not claims):
        errors.append("claim_registry must be a non-empty list for schema 3.x")
        claims = []
    elif not isinstance(claims, list):
        errors.append("claim_registry must be a list")
        claims = []

    claim_ids: set[str] = set()
    statements: set[str] = set()
    eligible_count = 0
    for index, claim in enumerate(claims, 1):
        prefix = f"claim_registry[{index}]"
        if not isinstance(claim, dict):
            errors.append(f"{prefix} must be a mapping")
            continue

        claim_id = claim.get("id")
        _validate_identifier(claim_id, f"{prefix}.id", errors)
        if claim_id in claim_ids:
            errors.append(f"Duplicate claim ID: {claim_id}")
        elif _is_nonempty_string(claim_id):
            claim_ids.add(claim_id)

        for field in ("type", "subject", "statement", "dates", "scope", "status", "interview_depth"):
            if not _is_nonempty_string(claim.get(field)):
                errors.append(f"{prefix}.{field} is required")

        statement = claim.get("statement", "")
        if _is_nonempty_string(statement):
            normalized = " ".join(statement.lower().split())
            if normalized in statements:
                warnings.append(f"Duplicate claim statement near {claim_id}")
            statements.add(normalized)

        status = claim.get("status")
        if status not in ALLOWED_STATUSES:
            errors.append(f"{prefix}.status must be one of {sorted(ALLOWED_STATUSES)}")

        depth = claim.get("interview_depth")
        if depth not in ALLOWED_DEPTHS:
            errors.append(f"{prefix}.interview_depth must be one of {sorted(ALLOWED_DEPTHS)}")

        eligible = claim.get("cv_eligible")
        if not isinstance(eligible, bool):
            errors.append(f"{prefix}.cv_eligible must be true or false")
        elif eligible:
            eligible_count += 1
            if status in INELIGIBLE_STATUSES:
                errors.append(f"{claim_id} is CV-eligible but has status {status}")

        claim_roles = claim.get("role_families", [])
        if not _list_of_strings(claim_roles):
            errors.append(f"{prefix}.role_families must be a non-empty list of strings")
        else:
            for role_id in claim_roles:
                if role_id not in role_families:
                    errors.append(f"{claim_id} references unknown role family: {role_id}")

        tags = claim.get("tags", [])
        if tags and not _list_of_strings(tags):
            errors.append(f"{prefix}.tags must be a list of strings")

        evidence_refs = claim.get("evidence", [])
        if not _list_of_strings(evidence_refs):
            errors.append(f"{prefix}.evidence must be a non-empty list of IDs")
        else:
            for evidence_id in evidence_refs:
                if evidence_id not in evidence_by_id:
                    errors.append(f"{claim_id} references unknown evidence: {evidence_id}")

        if status == "verified" and evidence_refs and all(
            evidence_by_id.get(evidence_id, {}).get("visibility") == "self_reported"
            for evidence_id in evidence_refs
        ):
            errors.append(f"{claim_id} is verified but all supporting evidence is self-reported")

        if claim.get("scope") == "personal" and "personal" not in statement.lower():
            warnings.append(f"{claim_id} has personal scope but the statement does not label it personal")

    exclusions = data.get("exclusions")
    if is_v3 and not isinstance(exclusions, list):
        errors.append("exclusions must be a list")
        exclusions = []
    elif exclusions is None:
        exclusions = []
    elif not isinstance(exclusions, list):
        errors.append("exclusions must be a list")
        exclusions = []
    for index, exclusion in enumerate(exclusions, 1):
        if not isinstance(exclusion, dict):
            errors.append(f"exclusions[{index}] must be a mapping")
            continue
        for field in ("item", "reason"):
            if not _is_nonempty_string(exclusion.get(field)):
                errors.append(f"exclusions[{index}].{field} is required")

    return {
        "ok": not errors,
        "schema_version": schema_version,
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "name": personal.get("full_name", ""),
            "work_entries": len(experience),
            "role_families": len(role_families),
            "evidence_items": len(evidence_by_id),
            "claims": len(claims),
            "eligible_claims": eligible_count,
        },
    }


def main() -> int:
    project_root = find_project_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "yaml_file",
        nargs="?",
        type=Path,
        default=project_root / "meta" / "master_cv.yaml",
        help="Master YAML path (default: meta/master_cv.yaml)",
    )
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Print JSON result")
    args = parser.parse_args()

    result = validate_master_cv(args.yaml_file)
    if args.as_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Validating master database: {args.yaml_file}")
        for warning in result.get("warnings", []):
            print(f"WARNING: {warning}")
        for error in result.get("errors", []):
            print(f"ERROR: {error}")
        if result.get("ok"):
            summary = result["summary"]
            print(
                "OK: schema {schema}; {claims} claims ({eligible} eligible), "
                "{evidence} evidence items, {roles} role families".format(
                    schema=result["schema_version"],
                    claims=summary["claims"],
                    eligible=summary["eligible_claims"],
                    evidence=summary["evidence_items"],
                    roles=summary["role_families"],
                )
            )

    failed = not result.get("ok") or (args.strict and bool(result.get("warnings")))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
