#!/usr/bin/env python3
"""Validate the evidence-first Awesome-CV master database."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

import yaml
from yaml.constructor import ConstructorError


ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
ALLOWED_STATUSES = {"verified", "self_reported", "planned", "unverified", "expired"}
ALLOWED_DEPTHS = {"strong", "moderate", "limited"}
ALLOWED_VISIBILITY = {"public", "private", "self_reported"}
ALLOWED_ROLE_READINESS = {"core", "credible", "stretch"}
ALLOWED_INTEREST_LEVELS = {"high", "medium", "low"}
ALLOWED_APPLICATION_PRIORITIES = {"active", "selective", "explore", "paused"}
ALLOWED_APPLICATION_DELIVERABLES = {"cv", "cover_letter"}
ALLOWED_THESIS_REPOSITORY_POLICIES = {"required_when_public", "preferred_when_public", "omit"}
ALLOWED_PROJECT_LINK_STYLES = {"canonical_project_link"}
ALLOWED_POSITIONING_PLACEMENTS = {"cover_letter", "interview"}
ALLOWED_DELIVERY_MODES = {"direct", "ai_assisted", "mixed", "not_applicable"}
ALLOWED_OWNER_ACTIONS = {
    "requirements",
    "architecture",
    "implementation",
    "integration",
    "review",
    "testing",
    "debugging",
    "deployment",
    "operation",
    "documentation",
    "analysis",
    "training",
}
ALLOWED_SKILL_USAGES = {"skill", "project_only", "exclude"}
ALLOWED_ADJACENT_VALUES = {
    "execution_leverage",
    "delivery_risk_reduction",
    "cross_functional_bridge",
    "autonomy",
}
ALLOWED_IDENTITY_VALUES = {
    "credential",
    "domain_identity",
    "market_bridge",
    "local_fit",
    "autonomy",
}
ALLOWED_SCOPES = {
    "academic",
    "academic_benchmark",
    "academic_project",
    "contractor",
    "employee",
    "internship",
    "intermittent_contract_assignment",
    "legal_status",
    "personal",
    "personal_infrastructure",
    "personal_open_source",
    "public_repository_metrics",
    "self_reported_language",
}
INELIGIBLE_STATUSES = {"planned", "unverified", "expired"}
PORTFOLIO_TIERS = {"primary", "supporting", "catalog"}
REQUIRED_TOP_LEVEL = {
    "personal_information",
    "education",
    "work_experience",
    "technical_skills",
    "languages",
}


class UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects silent duplicate mapping keys."""


def _construct_unique_mapping(
    loader: UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False
) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


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


def _validate_unique_strings(value: Any, label: str, errors: list[str]) -> None:
    if not isinstance(value, list) or not all(_is_nonempty_string(item) for item in value):
        return
    duplicates = sorted({item for item in value if value.count(item) > 1})
    if duplicates:
        errors.append(f"{label} contains duplicate values: {', '.join(duplicates)}")


def _normalize_repo_url(value: Any) -> str:
    if not _is_nonempty_string(value):
        return ""
    parsed = urlsplit(value.strip())
    path = parsed.path.rstrip("/")
    if path.endswith(".git"):
        path = path[:-4]
    return urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(), path.lower(), "", ""))


def validate_master_cv(yaml_path: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    if not yaml_path.exists():
        return {"ok": False, "errors": [f"File not found: {yaml_path}"], "warnings": []}

    try:
        data = yaml.load(yaml_path.read_text(encoding="utf-8"), Loader=UniqueKeyLoader)
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
    version_match = re.fullmatch(r"(\d+)\.(\d+)", schema_version)
    governed_roles = bool(
        version_match
        and (int(version_match.group(1)), int(version_match.group(2))) >= (3, 1)
    )
    governed_preferences = bool(
        version_match
        and (int(version_match.group(1)), int(version_match.group(2))) >= (3, 2)
    )
    governed_delivery = bool(
        version_match
        and (int(version_match.group(1)), int(version_match.group(2))) >= (3, 3)
    )
    governed_identity = bool(
        version_match
        and (int(version_match.group(1)), int(version_match.group(2))) >= (3, 4)
    )
    governed_application_defaults = bool(
        version_match
        and (int(version_match.group(1)), int(version_match.group(2))) >= (3, 5)
    )
    governed_project_links = bool(
        version_match
        and (int(version_match.group(1)), int(version_match.group(2))) >= (3, 6)
    )
    governed_reusable_positioning = bool(
        version_match
        and (int(version_match.group(1)), int(version_match.group(2))) >= (3, 7)
    )
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
    else:
        _validate_unique_strings(privacy.get("sensitive_fields", []), "privacy.sensitive_fields", errors)

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
        if governed_roles and isinstance(role, dict):
            readiness = role.get("readiness")
            if readiness not in ALLOWED_ROLE_READINESS:
                errors.append(
                    f"role_families.{role_id}.readiness must be one of: "
                    f"{', '.join(sorted(ALLOWED_ROLE_READINESS))}"
                )
            for field in ("strengths", "boundaries"):
                values = role.get(field)
                if not _list_of_strings(values):
                    errors.append(
                        f"role_families.{role_id}.{field} must be a non-empty list of strings"
                    )
                else:
                    _validate_unique_strings(
                        values, f"role_families.{role_id}.{field}", errors
                    )
        keywords = role.get("keywords", []) if isinstance(role, dict) else []
        titles = role.get("target_titles", []) if isinstance(role, dict) else []
        if not _list_of_strings(keywords):
            errors.append(f"role_families.{role_id}.keywords must be a non-empty list of strings")
        else:
            _validate_unique_strings(keywords, f"role_families.{role_id}.keywords", errors)
        if not _list_of_strings(titles):
            errors.append(f"role_families.{role_id}.target_titles must be a non-empty list of strings")
        else:
            _validate_unique_strings(titles, f"role_families.{role_id}.target_titles", errors)
        stretch_titles = role.get("stretch_titles", []) if isinstance(role, dict) else []
        if governed_preferences:
            if not isinstance(stretch_titles, list) or not all(
                _is_nonempty_string(title) for title in stretch_titles
            ):
                errors.append(
                    f"role_families.{role_id}.stretch_titles must be a list of strings"
                )
            else:
                _validate_unique_strings(
                    stretch_titles, f"role_families.{role_id}.stretch_titles", errors
                )
                unknown_stretch_titles = sorted(set(stretch_titles) - set(titles))
                if unknown_stretch_titles:
                    errors.append(
                        f"role_families.{role_id}.stretch_titles must also appear in target_titles: "
                        + ", ".join(unknown_stretch_titles)
                    )

    career_preferences = data.get("career_preferences")
    if governed_preferences:
        if not isinstance(career_preferences, dict):
            errors.append("career_preferences must be a mapping for schema 3.2+")
            career_preferences = {}
        role_interests = career_preferences.get("role_interests")
        if not isinstance(role_interests, list) or not role_interests:
            errors.append("career_preferences.role_interests must be a non-empty list")
            role_interests = []
        seen_interest_roles: set[str] = set()
        for index, item in enumerate(role_interests, 1):
            prefix = f"career_preferences.role_interests[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{prefix} must be a mapping")
                continue
            role_id = item.get("role_family")
            if role_id not in role_families:
                errors.append(f"{prefix}.role_family references unknown role: {role_id}")
            elif role_id in seen_interest_roles:
                errors.append(f"{prefix}.role_family is duplicated: {role_id}")
            else:
                seen_interest_roles.add(str(role_id))
            if item.get("interest") not in ALLOWED_INTEREST_LEVELS:
                errors.append(
                    f"{prefix}.interest must be one of: "
                    + ", ".join(sorted(ALLOWED_INTEREST_LEVELS))
                )
            if item.get("application_priority") not in ALLOWED_APPLICATION_PRIORITIES:
                errors.append(
                    f"{prefix}.application_priority must be one of: "
                    + ", ".join(sorted(ALLOWED_APPLICATION_PRIORITIES))
                )
            if not _is_nonempty_string(item.get("notes")):
                errors.append(f"{prefix}.notes is required")

    application_defaults = data.get("application_defaults")
    if governed_application_defaults:
        if not isinstance(application_defaults, dict):
            errors.append("application_defaults must be a mapping for schema 3.5+")
            application_defaults = {}
        deliverables = application_defaults.get("deliverables")
        if not _list_of_strings(deliverables):
            errors.append(
                "application_defaults.deliverables must be a non-empty list of strings"
            )
            deliverables = []
        else:
            _validate_unique_strings(
                deliverables, "application_defaults.deliverables", errors
            )
            unknown_deliverables = sorted(
                set(deliverables) - ALLOWED_APPLICATION_DELIVERABLES
            )
            if unknown_deliverables:
                errors.append(
                    "application_defaults.deliverables has unknown values: "
                    + ", ".join(unknown_deliverables)
                )
            if "cv" not in deliverables:
                errors.append("application_defaults.deliverables must include cv")
        if not isinstance(application_defaults.get("complement_review"), bool):
            errors.append("application_defaults.complement_review must be true or false")
        if governed_project_links:
            project_link_policy = application_defaults.get("project_link_policy")
            if not isinstance(project_link_policy, dict):
                errors.append(
                    "application_defaults.project_link_policy must be a mapping for schema 3.6+"
                )
                project_link_policy = {}
            thesis_repository = project_link_policy.get("thesis_repository")
            if thesis_repository not in ALLOWED_THESIS_REPOSITORY_POLICIES:
                errors.append(
                    "application_defaults.project_link_policy.thesis_repository must be one of: "
                    + ", ".join(sorted(ALLOWED_THESIS_REPOSITORY_POLICIES))
                )
            style = project_link_policy.get("style")
            if style not in ALLOWED_PROJECT_LINK_STYLES:
                errors.append(
                    "application_defaults.project_link_policy.style must be one of: "
                    + ", ".join(sorted(ALLOWED_PROJECT_LINK_STYLES))
                )
        reusable_positioning = application_defaults.get("reusable_positioning")
        if governed_reusable_positioning and (
            not isinstance(reusable_positioning, list) or not reusable_positioning
        ):
            errors.append(
                "application_defaults.reusable_positioning must be a non-empty list for schema 3.7+"
            )
            reusable_positioning = []
        elif reusable_positioning is None:
            reusable_positioning = []
        elif not isinstance(reusable_positioning, list):
            errors.append("application_defaults.reusable_positioning must be a list")
            reusable_positioning = []
    else:
        reusable_positioning = []

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
    claims_by_id: dict[str, dict[str, Any]] = {}
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
            claims_by_id[claim_id] = claim

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

        scope = claim.get("scope")
        if scope not in ALLOWED_SCOPES:
            errors.append(f"{prefix}.scope must be one of {sorted(ALLOWED_SCOPES)}")

        delivery = claim.get("delivery")
        requires_delivery = (
            governed_delivery
            and claim.get("type") == "project"
            and scope == "personal_open_source"
        )
        if requires_delivery and not isinstance(delivery, dict):
            errors.append(
                f"{prefix}.delivery is required for schema 3.3+ personal open-source projects"
            )
        if delivery is not None:
            if not isinstance(delivery, dict):
                errors.append(f"{prefix}.delivery must be a mapping")
            else:
                mode = delivery.get("mode")
                if mode not in ALLOWED_DELIVERY_MODES:
                    errors.append(
                        f"{prefix}.delivery.mode must be one of: "
                        + ", ".join(sorted(ALLOWED_DELIVERY_MODES))
                    )
                owned_actions = delivery.get("owned_actions")
                if not _list_of_strings(owned_actions):
                    errors.append(
                        f"{prefix}.delivery.owned_actions must be a non-empty list of strings"
                    )
                else:
                    _validate_unique_strings(
                        owned_actions, f"{prefix}.delivery.owned_actions", errors
                    )
                    unknown_actions = sorted(set(owned_actions) - ALLOWED_OWNER_ACTIONS)
                    if unknown_actions:
                        errors.append(
                            f"{prefix}.delivery.owned_actions has unknown values: "
                            + ", ".join(unknown_actions)
                        )
                boundaries = delivery.get("boundaries")
                if not _list_of_strings(boundaries):
                    errors.append(
                        f"{prefix}.delivery.boundaries must be a non-empty list of strings"
                    )
                else:
                    _validate_unique_strings(
                        boundaries, f"{prefix}.delivery.boundaries", errors
                    )

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
            _validate_unique_strings(claim_roles, f"{prefix}.role_families", errors)
            for role_id in claim_roles:
                if role_id not in role_families:
                    errors.append(f"{claim_id} references unknown role family: {role_id}")

        tags = claim.get("tags", [])
        if tags and not _list_of_strings(tags):
            errors.append(f"{prefix}.tags must be a list of strings")
        elif tags:
            _validate_unique_strings(tags, f"{prefix}.tags", errors)

        adjacent_values = claim.get("adjacent_values")
        if adjacent_values is not None:
            if not _list_of_strings(adjacent_values):
                errors.append(f"{prefix}.adjacent_values must be a non-empty list of strings")
            else:
                _validate_unique_strings(
                    adjacent_values, f"{prefix}.adjacent_values", errors
                )
                unknown_values = sorted(set(adjacent_values) - ALLOWED_ADJACENT_VALUES)
                if unknown_values:
                    errors.append(
                        f"{prefix}.adjacent_values has unknown values: "
                        + ", ".join(unknown_values)
                    )

        evidence_refs = claim.get("evidence", [])
        if not _list_of_strings(evidence_refs):
            errors.append(f"{prefix}.evidence must be a non-empty list of IDs")
        else:
            _validate_unique_strings(evidence_refs, f"{prefix}.evidence", errors)
            for evidence_id in evidence_refs:
                if evidence_id not in evidence_by_id:
                    errors.append(f"{claim_id} references unknown evidence: {evidence_id}")

        if status == "verified" and evidence_refs and all(
            evidence_by_id.get(evidence_id, {}).get("visibility") == "self_reported"
            for evidence_id in evidence_refs
        ):
            errors.append(f"{claim_id} is verified but all supporting evidence is self-reported")

        if str(scope).startswith("personal"):
            lowered_statement = statement.lower()
            if "personal" not in lowered_statement and "open-source" not in lowered_statement:
                warnings.append(
                    f"{claim_id} has personal scope but the statement does not label it personal/open-source"
                )

    seen_positioning_ids: set[str] = set()
    for index, item in enumerate(reusable_positioning, 1):
        prefix = f"application_defaults.reusable_positioning[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be a mapping")
            continue
        positioning_id = item.get("id")
        _validate_identifier(positioning_id, f"{prefix}.id", errors)
        if positioning_id in seen_positioning_ids:
            errors.append(f"duplicate reusable positioning ID: {positioning_id}")
        elif _is_nonempty_string(positioning_id):
            seen_positioning_ids.add(positioning_id)
        for field in ("text", "usage"):
            if not _is_nonempty_string(item.get(field)):
                errors.append(f"{prefix}.{field} is required")
        role_ids = item.get("role_families")
        if not _list_of_strings(role_ids):
            errors.append(f"{prefix}.role_families must be a non-empty list of strings")
        else:
            _validate_unique_strings(role_ids, f"{prefix}.role_families", errors)
            for role_id in role_ids:
                if role_id not in role_families:
                    errors.append(f"{prefix} references unknown role family: {role_id}")
        positioning_claim_ids = item.get("claim_ids")
        if not _list_of_strings(positioning_claim_ids):
            errors.append(f"{prefix}.claim_ids must be a non-empty list of IDs")
        else:
            _validate_unique_strings(positioning_claim_ids, f"{prefix}.claim_ids", errors)
            for claim_id in positioning_claim_ids:
                claim = claims_by_id.get(claim_id)
                if claim is None:
                    errors.append(f"{prefix} references unknown claim: {claim_id}")
                elif claim.get("cv_eligible") is not True or claim.get("status") not in {
                    "verified",
                    "self_reported",
                }:
                    errors.append(f"{prefix} references a claim that is not CV-eligible: {claim_id}")
        placements = item.get("placements")
        if not _list_of_strings(placements):
            errors.append(f"{prefix}.placements must be a non-empty list of strings")
        else:
            _validate_unique_strings(placements, f"{prefix}.placements", errors)
            unknown_placements = sorted(set(placements) - ALLOWED_POSITIONING_PLACEMENTS)
            if unknown_placements:
                errors.append(
                    f"{prefix}.placements has unknown values: "
                    + ", ".join(unknown_placements)
                )
        max_uses = item.get("max_uses_per_application")
        if not isinstance(max_uses, int) or isinstance(max_uses, bool) or max_uses < 1:
            errors.append(f"{prefix}.max_uses_per_application must be a positive integer")

    identity_anchors = data.get("identity_anchors")
    if governed_identity and (
        not isinstance(identity_anchors, list) or not identity_anchors
    ):
        errors.append("identity_anchors must contain one to five entries for schema 3.4+")
        identity_anchors = []
    elif identity_anchors is None:
        identity_anchors = []
    elif not isinstance(identity_anchors, list):
        errors.append("identity_anchors must be a list")
        identity_anchors = []
    if len(identity_anchors) > 5:
        errors.append("identity_anchors may contain at most five entries")
    seen_anchor_claims: set[str] = set()
    for index, item in enumerate(identity_anchors, 1):
        prefix = f"identity_anchors[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be a mapping")
            continue
        claim_id = item.get("claim_id")
        if not _is_nonempty_string(claim_id):
            errors.append(f"{prefix}.claim_id is required")
            continue
        if claim_id in seen_anchor_claims:
            errors.append(f"duplicate identity anchor: {claim_id}")
        seen_anchor_claims.add(claim_id)
        claim = claims_by_id.get(claim_id)
        if claim is None:
            errors.append(f"{prefix} references unknown claim: {claim_id}")
        elif claim.get("cv_eligible") is not True or claim.get("status") not in {
            "verified",
            "self_reported",
        }:
            errors.append(f"{prefix} references a claim that is not CV-eligible: {claim_id}")
        if item.get("value") not in ALLOWED_IDENTITY_VALUES:
            errors.append(
                f"{prefix}.value must be one of: "
                + ", ".join(sorted(ALLOWED_IDENTITY_VALUES))
            )
        if not _is_nonempty_string(item.get("usage")):
            errors.append(f"{prefix}.usage is required")

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

    portfolio_management = data.get("portfolio_management")
    governed_portfolio = portfolio_management is not None
    excluded_repo_urls: set[str] = set()
    if governed_portfolio:
        if not isinstance(portfolio_management, dict):
            errors.append("portfolio_management must be a mapping")
            portfolio_management = {}
        for field in ("last_reviewed", "inventory_evidence_id"):
            if not _is_nonempty_string(portfolio_management.get(field)):
                errors.append(f"portfolio_management.{field} is required")
        inventory_evidence_id = portfolio_management.get("inventory_evidence_id")
        if _is_nonempty_string(inventory_evidence_id) and inventory_evidence_id not in evidence_by_id:
            errors.append(
                "portfolio_management.inventory_evidence_id references unknown evidence: "
                f"{inventory_evidence_id}"
            )
        excluded_repositories = portfolio_management.get("excluded_repositories")
        if not isinstance(excluded_repositories, list):
            errors.append("portfolio_management.excluded_repositories must be a list")
            excluded_repositories = []
        for index, exclusion in enumerate(excluded_repositories, 1):
            prefix = f"portfolio_management.excluded_repositories[{index}]"
            if not isinstance(exclusion, dict):
                errors.append(f"{prefix} must be a mapping")
                continue
            repo_url = _normalize_repo_url(exclusion.get("repo"))
            if not repo_url or "github.com/" not in repo_url:
                errors.append(f"{prefix}.repo must be a GitHub repository URL")
            elif repo_url in excluded_repo_urls:
                errors.append(f"{prefix}.repo is duplicated")
            else:
                excluded_repo_urls.add(repo_url)
            if not _is_nonempty_string(exclusion.get("reason")):
                errors.append(f"{prefix}.reason is required")

    def validate_claim_classification(item: dict[str, Any], prefix: str) -> None:
        references = item.get("claim_ids")
        if references is None:
            if item.get("cv_eligible") is False:
                reason = (
                    item.get("eligibility_reason")
                    or item.get("exclusion_reason")
                    or item.get("details")
                )
                if not _is_nonempty_string(reason):
                    errors.append(
                        f"{prefix} is CV-ineligible but has no eligibility_reason"
                    )
            else:
                warnings.append(
                    f"{prefix} is not classified: add claim_ids or set cv_eligible: false"
                )
            return
        if not _list_of_strings(references):
            errors.append(f"{prefix}.claim_ids must be a non-empty list of IDs")
            return
        _validate_unique_strings(references, f"{prefix}.claim_ids", errors)
        for claim_id in references:
            if claim_id not in claim_ids:
                errors.append(f"{prefix} references unknown claim: {claim_id}")

    def validate_history_links(items: Any, label: str) -> None:
        if items is None:
            return
        if not isinstance(items, list):
            errors.append(f"{label} must be a list")
            return
        for index, item in enumerate(items, 1):
            prefix = f"{label}[{index}]"
            if not isinstance(item, dict):
                continue
            if governed_portfolio and label == "open_source_and_projects":
                repo_url = _normalize_repo_url(item.get("repo"))
                if not repo_url or "github.com/" not in repo_url:
                    errors.append(f"{prefix}.repo must be a GitHub repository URL")
                elif repo_url in excluded_repo_urls:
                    errors.append(f"{prefix}.repo is also listed as a portfolio exclusion")
                tier = item.get("portfolio_tier")
                if tier not in PORTFOLIO_TIERS:
                    errors.append(
                        f"{prefix}.portfolio_tier must be one of: {', '.join(sorted(PORTFOLIO_TIERS))}"
                    )
                if not _is_nonempty_string(item.get("last_reviewed")):
                    errors.append(f"{prefix}.last_reviewed is required")
                project_evidence = item.get("evidence_ids")
                if not _list_of_strings(project_evidence):
                    errors.append(f"{prefix}.evidence_ids must be a non-empty list of IDs")
                else:
                    _validate_unique_strings(project_evidence, f"{prefix}.evidence_ids", errors)
                    matched_repo_evidence = False
                    for evidence_id in project_evidence:
                        evidence = evidence_by_id.get(evidence_id)
                        if evidence is None:
                            errors.append(f"{prefix} references unknown evidence: {evidence_id}")
                        elif _normalize_repo_url(evidence.get("locator")) == repo_url:
                            matched_repo_evidence = True
                    if repo_url and not matched_repo_evidence:
                        errors.append(
                            f"{prefix}.evidence_ids must include public evidence for its repository URL"
                        )
            validate_claim_classification(item, prefix)

    def validate_nested_history_links(value: Any, label: str) -> None:
        if value is None:
            return
        if isinstance(value, list):
            for index, item in enumerate(value, 1):
                prefix = f"{label}[{index}]"
                if not isinstance(item, dict):
                    errors.append(f"{prefix} must be a mapping")
                    continue
                validate_claim_classification(item, prefix)
            return
        if not isinstance(value, dict):
            errors.append(f"{label} must be a mapping or list")
            return
        if "title" in value or "code" in value:
            validate_claim_classification(value, label)
            return
        for key, child in value.items():
            validate_nested_history_links(child, f"{label}.{key}")

    validate_history_links(data.get("work_experience"), "work_experience")
    validate_history_links(data.get("open_source_and_projects"), "open_source_and_projects")
    validate_history_links(
        data.get("certifications_and_qualifications"),
        "certifications_and_qualifications",
    )
    validate_nested_history_links(
        education.get("bachelor_thesis"),
        "education.bachelor_thesis",
    )
    validate_nested_history_links(
        education.get("thesis"),
        "education.thesis",
    )
    validate_nested_history_links(
        education.get("relevant_coursework"),
        "education.relevant_coursework",
    )
    validate_nested_history_links(
        data.get("honors_and_achievements"),
        "honors_and_achievements",
    )

    evidenced_skills = skills.get("evidenced") if isinstance(skills, dict) else None
    if is_v3 and not isinstance(evidenced_skills, list):
        warnings.append(
            "technical_skills.evidenced is missing; skill inventory is not mapped to atomic claims"
        )
    elif isinstance(evidenced_skills, list):
        for index, item in enumerate(evidenced_skills, 1):
            prefix = f"technical_skills.evidenced[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{prefix} must be a mapping")
                continue
            if not _is_nonempty_string(item.get("name")):
                errors.append(f"{prefix}.name is required")
            if governed_delivery:
                if item.get("cv_usage") not in ALLOWED_SKILL_USAGES:
                    errors.append(
                        f"{prefix}.cv_usage must be one of: "
                        + ", ".join(sorted(ALLOWED_SKILL_USAGES))
                    )
                if not _is_nonempty_string(item.get("level")):
                    errors.append(f"{prefix}.level is required for schema 3.3+")
                boundaries = item.get("boundaries")
                if not _list_of_strings(boundaries):
                    errors.append(
                        f"{prefix}.boundaries must be a non-empty list of strings for schema 3.3+"
                    )
                else:
                    _validate_unique_strings(boundaries, f"{prefix}.boundaries", errors)
            references = item.get("claim_ids")
            if not _list_of_strings(references):
                errors.append(f"{prefix}.claim_ids must be a non-empty list of IDs")
                continue
            _validate_unique_strings(references, f"{prefix}.claim_ids", errors)
            for claim_id in references:
                if claim_id not in claim_ids:
                    errors.append(f"{prefix} references unknown claim: {claim_id}")

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
