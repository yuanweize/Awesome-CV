from __future__ import annotations

import copy
import json
import tempfile
from pathlib import Path
from typing import Any

import yaml

from engine.application_manifest import ID_PATTERN, new_manifest, sha256, slug, validate_manifest
from engine.generate_ai_context import build_context
from engine.validate_master_cv import validate_master_cv


def parse_master(master_yaml: str) -> dict[str, Any]:
    try:
        data = yaml.safe_load(master_yaml)
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid master YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("Master YAML root must be a mapping")
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "master.yaml"
        path.write_text(master_yaml, encoding="utf-8")
        result = validate_master_cv(path)
    if not result["ok"]:
        raise ValueError("Master validation failed: " + "; ".join(result["errors"][:8]))
    return data


def memory_summary(data: dict[str, Any]) -> dict[str, Any]:
    claims = [item for item in data.get("claim_registry", []) if isinstance(item, dict)]
    eligible = [
        item
        for item in claims
        if item.get("cv_eligible") is True and item.get("status") in {"verified", "self_reported"}
    ]
    return {
        "schema_version": str(data.get("schema_version", "")),
        "claims": len(claims),
        "eligible_claims": len(eligible),
        "evidence": len(data.get("evidence_registry", [])),
        "role_families": sorted(data.get("role_families", {})),
    }


def storage_yaml(data: dict[str, Any], store_contact: bool = False) -> str:
    """Serialize validated memory for storage, redacting direct contact data by default."""
    stored = copy.deepcopy(data)
    personal = stored.get("personal_information")
    if isinstance(personal, dict) and not store_contact:
        personal["email"] = "redacted@example.org"
        for field in ("phone", "phone_cz", "street_address", "date_of_birth"):
            if field in personal:
                personal[field] = "redacted"
    return yaml.safe_dump(stored, sort_keys=False, allow_unicode=True)


def context_from_memory(master_yaml: str, jd: str, role: str, max_claims: int) -> str:
    data = parse_master(master_yaml)
    return build_context(data, jd, role, max_claims, include_contact=False, explain_scores=False)


def new_application_text(
    master_yaml: str,
    company: str,
    title: str,
    role: str,
    jd: str,
    application_id: str = "",
) -> str:
    master = parse_master(master_yaml)
    if role not in set(master.get("role_families", {})):
        raise ValueError(f"Unknown role family: {role}")
    generated_id = application_id.strip() or f"dify-{slug(company)}-{slug(title)}"
    if not ID_PATTERN.fullmatch(generated_id):
        raise ValueError("Application ID must use lowercase letters, numbers, dots, underscores, or hyphens")
    with tempfile.TemporaryDirectory() as directory:
        jd_path = Path(directory) / "jd.md"
        jd_path.write_text(jd, encoding="utf-8")
        manifest = new_manifest(
            generated_id,
            company.strip(),
            title.strip(),
            role,
            f"meta/applications/{generated_id}/jd.md",
            sha256(jd_path),
            generated_id,
        )
    return yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True)


def validate_application_text(
    master_yaml: str,
    application_yaml: str,
    jd: str,
    strict: bool,
) -> list[str]:
    parse_master(master_yaml)
    try:
        application = yaml.safe_load(application_yaml)
    except yaml.YAMLError as exc:
        return [f"Invalid application YAML: {exc}"]
    if not isinstance(application, dict):
        return ["Application YAML root must be a mapping"]
    job = application.get("job_description", {})
    if not isinstance(job, dict):
        return ["job_description must be a mapping"]
    raw_path = job.get("path")
    if not isinstance(raw_path, str) or not raw_path:
        return ["job_description.path is required"]
    relative = Path(raw_path)
    if relative.is_absolute() or ".." in relative.parts:
        return ["job_description.path must be a safe relative path under meta/"]

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        master_path = root / "master.yaml"
        master_path.write_text(master_yaml, encoding="utf-8")
        jd_path = root / relative
        jd_path.parent.mkdir(parents=True, exist_ok=True)
        jd_path.write_text(jd, encoding="utf-8")
        return validate_manifest(application, master_path, root, strict=strict)


def result_json(ok: bool, **values: Any) -> str:
    return json.dumps({"ok": ok, **values}, ensure_ascii=False)
