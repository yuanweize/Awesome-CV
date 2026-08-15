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


SCHEMA_VERSION = "1.3"
SUPPORTED_SCHEMA_VERSIONS = {"1.0", "1.1", "1.2", "1.3"}
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
IDENTITY_SECTIONS = {"headline", "summary", "education", "experience", "projects", "skills"}
DELIVERABLES = {"cv", "cover_letter"}
CAPABILITY_DECISIONS = {"include", "omit"}
CAPABILITY_PLACEMENTS = ADJACENT_SECTIONS | {"cover_letter", "none"}
VACANCY_STATUSES = {"open", "closed", "unverified"}
APPLICATION_ROUTES = {"form", "email", "official_instruction", "unverified"}
EMPLOYER_PORTFOLIO_STRATEGIES = {"standalone", "primary", "backup", "excluded"}
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
HTTP_URL_PATTERN = re.compile(r"^https?://\S+$")


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


def reviewable_skill_claim_ids(path: Path) -> set[str]:
    """Return claim IDs that back groups allowed in the visible Skills section."""
    data = load_yaml(path, "master CV")
    technical_skills = data.get("technical_skills", {})
    if not isinstance(technical_skills, dict):
        return set()
    claim_ids: set[str] = set()
    for group in technical_skills.get("evidenced", []):
        if not isinstance(group, dict) or group.get("cv_usage") != "skill":
            continue
        claim_ids.update(
            item for item in group.get("claim_ids", []) if isinstance(item, str)
        )
    return claim_ids


def new_manifest(
    application_id: str,
    company: str,
    title: str,
    role: str,
    jd_path: str,
    jd_hash: str,
    profile: str,
    deliverables: list[str] | None = None,
) -> dict[str, Any]:
    declared_deliverables = list(deliverables or ["cv", "cover_letter"])
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
            "availability": {
                "status": "unverified",
                "official_url": "",
                "verified_at": "",
                "application_route": "unverified",
            },
        },
        "employer_portfolio": {
            "strategy": "standalone",
            "compared_application_ids": [],
            "reason": "First role at this employer; compare before adding another application.",
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
        "deliverables": declared_deliverables,
        "selected_claims": [],
        "identity_anchors": [],
        "adjacent_differentiators": [],
        "capability_review": {
            "completed": False,
            "entries": [],
        },
        "final_bullets": [],
        "cover_letter_paragraphs": [],
        "post_submission_corrections": [],
        "artifacts": {
            "profile": profile,
            "cv_pdf": "",
            "cover_letter_pdf": "",
            "cv_sha256": "",
            "cover_letter_sha256": "",
            "page_count": 0,
            "cover_letter_page_count": 0,
            "application_pdf": "",
            "application_sha256": "",
            "application_page_count": 0,
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
    schema_version = str(data.get("schema_version", ""))
    if schema_version not in SUPPORTED_SCHEMA_VERSIONS:
        errors.append(
            "schema_version must be one of: "
            + ", ".join(sorted(SUPPORTED_SCHEMA_VERSIONS))
        )

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

    deliverables = data.get("deliverables", [])
    if schema_version in {"1.2", "1.3"}:
        if not isinstance(deliverables, list) or not deliverables or not all(
            isinstance(item, str) for item in deliverables
        ):
            errors.append("deliverables must be a non-empty list for schema 1.2+")
            deliverables = []
        elif len(set(deliverables)) != len(deliverables):
            errors.append("deliverables contains duplicates")
        unknown_deliverables = sorted(set(deliverables) - DELIVERABLES)
        if unknown_deliverables:
            errors.append(
                "deliverables contains unknown values: " + ", ".join(unknown_deliverables)
            )
        if "cv" not in deliverables:
            errors.append("deliverables must include cv")
    elif not isinstance(deliverables, list):
        deliverables = []

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

    availability = job.get("availability", {})
    vacancy_status = ""
    official_url = ""
    verified_at = ""
    application_route = ""
    if schema_version == "1.3":
        if not isinstance(availability, dict):
            errors.append("job_description.availability must be a mapping")
            availability = {}
        vacancy_status = availability.get("status")
        official_url = availability.get("official_url")
        verified_at = availability.get("verified_at")
        application_route = availability.get("application_route")
        if vacancy_status not in VACANCY_STATUSES:
            errors.append(
                "job_description.availability.status must be open, closed, or unverified"
            )
        if not isinstance(official_url, str):
            errors.append("job_description.availability.official_url must be a string")
            official_url = ""
        elif official_url and not HTTP_URL_PATTERN.fullmatch(official_url):
            errors.append("job_description.availability.official_url must be an HTTP(S) URL")
        if not isinstance(verified_at, str):
            errors.append("job_description.availability.verified_at must be an ISO date")
            verified_at = ""
        elif verified_at:
            try:
                dt.date.fromisoformat(verified_at)
            except ValueError:
                errors.append("job_description.availability.verified_at must be an ISO date")
        if application_route not in APPLICATION_ROUTES:
            errors.append(
                "job_description.availability.application_route must be form, email, "
                "official_instruction, or unverified"
            )

    employer_portfolio = data.get("employer_portfolio", {})
    portfolio_strategy = ""
    compared_application_ids: list[Any] = []
    if schema_version == "1.3":
        if not isinstance(employer_portfolio, dict):
            errors.append("employer_portfolio must be a mapping")
            employer_portfolio = {}
        portfolio_strategy = employer_portfolio.get("strategy")
        compared_application_ids = employer_portfolio.get("compared_application_ids", [])
        portfolio_reason = employer_portfolio.get("reason")
        if portfolio_strategy not in EMPLOYER_PORTFOLIO_STRATEGIES:
            errors.append(
                "employer_portfolio.strategy must be standalone, primary, backup, or excluded"
            )
        if not isinstance(compared_application_ids, list):
            errors.append("employer_portfolio.compared_application_ids must be a list")
            compared_application_ids = []
        else:
            for compared_id in compared_application_ids:
                if not isinstance(compared_id, str) or not ID_PATTERN.fullmatch(compared_id):
                    errors.append("employer_portfolio.compared_application_ids contains an invalid ID")
                elif compared_id == application_id:
                    errors.append("employer_portfolio cannot compare the application with itself")
        if portfolio_strategy in {"primary", "backup"} and not compared_application_ids:
            errors.append(
                f"employer_portfolio strategy {portfolio_strategy} requires a compared application ID"
            )
        if not isinstance(portfolio_reason, str) or not portfolio_reason.strip():
            errors.append("employer_portfolio.reason is required")

    identity = data.get("identity_anchors", [])
    if not isinstance(identity, list):
        errors.append("identity_anchors must be a list")
        identity = []
    if len(identity) > 3:
        errors.append("identity_anchors may contain at most three claims")
    identity_ids: set[str] = set()
    identity_placements: dict[str, str] = {}
    for index, item in enumerate(identity, 1):
        prefix = f"identity_anchors[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be a mapping")
            continue
        claim_id = item.get("claim_id")
        if not isinstance(claim_id, str) or not ID_PATTERN.fullmatch(claim_id):
            errors.append(f"{prefix}.claim_id is invalid")
            continue
        if claim_id in identity_ids:
            errors.append(f"duplicate identity anchor: {claim_id}")
        identity_ids.add(claim_id)
        placement = item.get("placement")
        if placement not in IDENTITY_SECTIONS:
            errors.append(f"{prefix}.placement is invalid")
        else:
            identity_placements[claim_id] = placement
        if not isinstance(item.get("reason"), str) or not item.get("reason", "").strip():
            errors.append(f"{prefix}.reason is required")

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

    corrections = data.get("post_submission_corrections", [])
    if not isinstance(corrections, list):
        errors.append("post_submission_corrections must be a list")
        corrections = []
    if corrections and stage not in {"sent", "closed"}:
        errors.append("post_submission_corrections are allowed only for sent or closed manifests")
    corrected_ids: set[str] = set()
    for index, item in enumerate(corrections, 1):
        prefix = f"post_submission_corrections[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be a mapping")
            continue
        claim_id = item.get("claim_id")
        if not isinstance(claim_id, str) or not ID_PATTERN.fullmatch(claim_id):
            errors.append(f"{prefix}.claim_id is invalid")
            continue
        if claim_id in corrected_ids:
            errors.append(f"duplicate post-submission correction: {claim_id}")
        corrected_ids.add(claim_id)
        if claim_id not in claims:
            errors.append(f"{prefix} references unknown claim: {claim_id}")
        for field in ("corrected_on", "reason"):
            if not isinstance(item.get(field), str) or not item.get(field, "").strip():
                errors.append(f"{prefix}.{field} is required")

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
        current_claim_is_eligible = (
            claim.get("cv_eligible") is True
            and claim.get("status") in {"verified", "self_reported"}
        )
        historical_exception = stage in {"sent", "closed"} and claim_id in corrected_ids
        if not current_claim_is_eligible and not historical_exception:
            errors.append(f"selected claim is not CV-eligible: {claim_id}")
        if (
            role
            and role not in claim.get("role_families", [])
            and claim_id not in adjacent_ids
            and claim_id not in identity_ids
            and not historical_exception
        ):
            errors.append(f"selected claim {claim_id} is outside role family {role}")
    for claim_id in sorted(adjacent_ids):
        if claim_id not in selected_set:
            errors.append(
                f"adjacent differentiator is not present in selected_claims: {claim_id}"
            )
    for claim_id in sorted(identity_ids):
        if claim_id not in selected_set:
            errors.append(f"identity anchor is not present in selected_claims: {claim_id}")
        claim = claims.get(claim_id)
        if claim is None:
            errors.append(f"identity anchor references unknown claim: {claim_id}")
        elif claim.get("cv_eligible") is not True or claim.get("status") not in {
            "verified",
            "self_reported",
        }:
            errors.append(f"identity anchor is not CV-eligible: {claim_id}")
        if claim_id in adjacent_ids:
            errors.append(f"claim cannot be both identity anchor and adjacent differentiator: {claim_id}")
    for claim_id in sorted(corrected_ids - selected_set):
        errors.append(
            f"post-submission correction is not present in selected_claims: {claim_id}"
        )

    capability_review = data.get("capability_review", {})
    capability_entries: list[dict[str, Any]] = []
    seen_capabilities: set[str] = set()
    if schema_version in {"1.2", "1.3"}:
        if not isinstance(capability_review, dict):
            errors.append("capability_review must be a mapping for schema 1.2+")
            capability_review = {}
        if not isinstance(capability_review.get("completed"), bool):
            errors.append("capability_review.completed must be true or false")
        raw_entries = capability_review.get("entries", [])
        if not isinstance(raw_entries, list):
            errors.append("capability_review.entries must be a list")
            raw_entries = []
        for index, item in enumerate(raw_entries, 1):
            prefix = f"capability_review.entries[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{prefix} must be a mapping")
                continue
            claim_id = item.get("claim_id")
            if not isinstance(claim_id, str) or not ID_PATTERN.fullmatch(claim_id):
                errors.append(f"{prefix}.claim_id is invalid")
                continue
            if claim_id in seen_capabilities:
                errors.append(f"duplicate capability review claim: {claim_id}")
            seen_capabilities.add(claim_id)
            if claim_id not in claims:
                errors.append(f"{prefix} references unknown claim: {claim_id}")
            decision_value = item.get("decision")
            if decision_value not in CAPABILITY_DECISIONS:
                errors.append(f"{prefix}.decision must be include or omit")
            placement = item.get("placement")
            if placement not in CAPABILITY_PLACEMENTS:
                errors.append(f"{prefix}.placement is invalid")
            if not isinstance(item.get("reason"), str) or not item.get("reason", "").strip():
                errors.append(f"{prefix}.reason is required")
            if decision_value == "include":
                if claim_id not in selected_set:
                    errors.append(f"included capability is not in selected_claims: {claim_id}")
                if placement == "none":
                    errors.append(f"included capability needs a visible placement: {claim_id}")
            elif decision_value == "omit":
                if claim_id in selected_set:
                    errors.append(f"omitted capability is still in selected_claims: {claim_id}")
                if placement != "none":
                    errors.append(f"omitted capability placement must be none: {claim_id}")
            capability_entries.append(item)

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

    letter_paragraphs = data.get("cover_letter_paragraphs", [])
    if not isinstance(letter_paragraphs, list):
        errors.append("cover_letter_paragraphs must be a list")
        letter_paragraphs = []
    seen_paragraphs: set[str] = set()
    for index, paragraph in enumerate(letter_paragraphs, 1):
        prefix = f"cover_letter_paragraphs[{index}]"
        if not isinstance(paragraph, dict):
            errors.append(f"{prefix} must be a mapping")
            continue
        paragraph_id = paragraph.get("id")
        if not isinstance(paragraph_id, str) or not ID_PATTERN.fullmatch(paragraph_id):
            errors.append(f"{prefix}.id is invalid")
        elif paragraph_id in seen_paragraphs:
            errors.append(f"duplicate cover-letter paragraph ID: {paragraph_id}")
        else:
            seen_paragraphs.add(paragraph_id)
        if not isinstance(paragraph.get("text"), str) or not paragraph.get("text", "").strip():
            errors.append(f"{prefix}.text is required")
        mapped = paragraph.get("claim_ids", [])
        if not isinstance(mapped, list) or not mapped:
            errors.append(f"{prefix}.claim_ids must contain at least one claim")
            mapped = []
        for claim_id in mapped:
            if claim_id not in selected_set:
                errors.append(f"{prefix} uses claim not present in selected_claims: {claim_id}")

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
        if schema_version == "1.3" and stage in {"approved", "drafted", "validated"}:
            if vacancy_status != "open":
                errors.append(f"stage {stage} requires an officially verified open vacancy")
            if not official_url:
                errors.append(f"stage {stage} requires an official vacancy URL")
            if not verified_at:
                errors.append(f"stage {stage} requires a vacancy verification date")
            if application_route == "unverified":
                errors.append(f"stage {stage} requires a verified application route")
            if portfolio_strategy == "excluded":
                errors.append(f"stage {stage} cannot use an excluded employer-portfolio strategy")
        if schema_version in {"1.2", "1.3"} and stage in {
            "approved",
            "drafted",
            "validated",
            "sent",
            "closed",
        } and not capability_review.get("completed"):
            errors.append(f"stage {stage} requires a completed capability_review")
        if schema_version in {"1.2", "1.3"} and stage in {
            "approved",
            "drafted",
            "validated",
            "sent",
            "closed",
        }:
            missing_capability_decisions = sorted(
                (selected_set & reviewable_skill_claim_ids(master_path))
                - seen_capabilities
            )
            for claim_id in missing_capability_decisions:
                errors.append(
                    "selected skill-backed claim is missing from capability_review: "
                    + claim_id
                )
        if (
            schema_version in {"1.2", "1.3"}
            and "cover_letter" in deliverables
            and stage in {"drafted", "validated", "sent", "closed"}
            and not (2 <= len(letter_paragraphs) <= 6)
        ):
            errors.append(
                f"stage {stage} requires two to six evidence-bound cover_letter_paragraphs"
            )
        if (
            schema_version in {"1.1", "1.2", "1.3"}
            and stage in {"approved", "drafted", "validated", "sent", "closed"}
            and not identity
        ):
            errors.append(f"stage {stage} requires one to three identity_anchors")
        for claim_id, placement in identity_placements.items():
            if stage in {"drafted", "validated", "sent", "closed"} and not any(
                isinstance(bullet, dict)
                and bullet.get("section") == placement
                and claim_id in bullet.get("claim_ids", [])
                for bullet in bullets
            ):
                errors.append(
                    f"identity anchor {claim_id} has no final bullet in approved placement {placement}"
                )
        if schema_version in {"1.2", "1.3"} and stage in {"drafted", "validated", "sent", "closed"}:
            for item in capability_entries:
                if item.get("decision") != "include":
                    continue
                claim_id = item.get("claim_id")
                placement = item.get("placement")
                if placement == "cover_letter":
                    present = any(
                        isinstance(paragraph, dict)
                        and claim_id in paragraph.get("claim_ids", [])
                        for paragraph in letter_paragraphs
                    )
                else:
                    present = any(
                        isinstance(bullet, dict)
                        and bullet.get("section") == placement
                        and claim_id in bullet.get("claim_ids", [])
                        for bullet in bullets
                    )
                if not present:
                    errors.append(
                        f"included capability {claim_id} has no content in approved placement {placement}"
                    )

        if schema_version in {"1.2", "1.3"} and stage in {"validated", "sent", "closed"}:
            artifacts = data.get("artifacts")
            if not isinstance(artifacts, dict):
                errors.append("artifacts must be a mapping")
                artifacts = {}

            def validate_artifact(kind: str, path_field: str, hash_field: str, pages_field: str) -> None:
                raw_path = artifacts.get(path_field)
                expected = artifacts.get(hash_field)
                pages = artifacts.get(pages_field)
                if not isinstance(raw_path, str) or not raw_path.strip():
                    errors.append(f"artifacts.{path_field} is required for {kind}")
                    return
                candidate = (
                    (project_root / raw_path).resolve()
                    if not Path(raw_path).is_absolute()
                    else Path(raw_path).resolve()
                )
                allowed_roots = [
                    (project_root / "workspace" / "profiles").resolve(),
                    (project_root / "workspace" / "build").resolve(),
                ]
                if not any(candidate.is_relative_to(root) for root in allowed_roots):
                    errors.append(
                        f"artifacts.{path_field} must stay under workspace/profiles/ "
                        "or workspace/build/"
                    )
                elif not candidate.is_file():
                    errors.append(f"artifact file not found: {raw_path}")
                elif not isinstance(expected, str) or sha256(candidate) != expected:
                    errors.append(f"artifacts.{hash_field} does not match {raw_path}")
                if not isinstance(pages, int) or pages < 1:
                    errors.append(f"artifacts.{pages_field} must be a positive integer")

            if "cv" in deliverables:
                validate_artifact("cv", "cv_pdf", "cv_sha256", "page_count")
            if "cover_letter" in deliverables:
                validate_artifact(
                    "cover_letter",
                    "cover_letter_pdf",
                    "cover_letter_sha256",
                    "cover_letter_page_count",
                )
            if isinstance(artifacts.get("application_pdf"), str) and artifacts.get(
                "application_pdf", ""
            ).strip():
                validate_artifact(
                    "application",
                    "application_pdf",
                    "application_sha256",
                    "application_page_count",
                )

    return errors


def save_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    temporary.replace(path)
    os.chmod(path, 0o600)


def command_init(args: argparse.Namespace, root: Path) -> int:
    master = load_yaml(args.master, "master CV")
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
    application_defaults = master.get("application_defaults", {})
    deliverables = (
        application_defaults.get("deliverables", ["cv", "cover_letter"])
        if isinstance(application_defaults, dict)
        else ["cv", "cover_letter"]
    )
    manifest = new_manifest(
        application_id,
        args.company,
        args.title,
        args.role,
        relative_jd,
        sha256(jd_target),
        profile,
        deliverables,
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
