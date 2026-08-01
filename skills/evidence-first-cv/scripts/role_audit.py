#!/usr/bin/env python3
"""Audit career interests, role-family coverage, and evidence readiness."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from validate_master_cv import validate_master_cv


GENERIC_SUPPORT_TYPES = {"language", "work_authorization"}


def find_project_root() -> Path:
    candidates = [Path.cwd(), *Path.cwd().parents, Path(__file__).resolve(), *Path(__file__).resolve().parents]
    for candidate in candidates:
        if candidate.is_file():
            candidate = candidate.parent
        if (candidate / "templates" / "master_cv.yaml.example").is_file():
            return candidate
    return Path.cwd()


def load_master(path: Path) -> dict[str, Any]:
    result = validate_master_cv(path)
    if not result.get("ok"):
        raise ValueError("master validation failed: " + "; ".join(result.get("errors", [])))
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError(f"cannot read master database {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("master database root must be a mapping")
    return data


def audit_roles(data: dict[str, Any]) -> dict[str, Any]:
    role_families = data.get("role_families", {})
    preferences = {
        item.get("role_family"): item
        for item in data.get("career_preferences", {}).get("role_interests", [])
        if isinstance(item, dict)
    }
    claims = [item for item in data.get("claim_registry", []) if isinstance(item, dict)]
    roles: list[dict[str, Any]] = []
    warnings: list[str] = []

    for role_id, role in role_families.items():
        role_claims = [item for item in claims if role_id in item.get("role_families", [])]
        eligible = [
            item
            for item in role_claims
            if item.get("cv_eligible") is True
            and item.get("status") in {"verified", "self_reported"}
        ]
        substantive = [
            item for item in eligible if item.get("type") not in GENERIC_SUPPORT_TYPES
        ]
        depth_counts = {
            depth: sum(
                1 for item in substantive if item.get("interview_depth") == depth
            )
            for depth in ("strong", "moderate", "limited")
        }
        preference = preferences.get(role_id, {})
        row = {
            "id": role_id,
            "label": role.get("label", ""),
            "readiness": role.get("readiness", "unspecified"),
            "interest": preference.get("interest", "unspecified"),
            "application_priority": preference.get("application_priority", "unspecified"),
            "target_titles": role.get("target_titles", []),
            "stretch_titles": role.get("stretch_titles", []),
            "claim_count": len(role_claims),
            "eligible_claim_count": len(eligible),
            "substantive_claim_count": len(substantive),
            "generic_support_claim_count": len(eligible) - len(substantive),
            "substantive_depth": depth_counts,
            "eligible_claim_ids": [item.get("id", "") for item in eligible],
            "substantive_claim_ids": [item.get("id", "") for item in substantive],
        }
        roles.append(row)
        if preference.get("interest") == "high" and not eligible:
            warnings.append(f"high-interest role {role_id} has no eligible claims")
        elif preference.get("interest") == "high" and depth_counts["strong"] == 0:
            warnings.append(
                f"high-interest role {role_id} has no strong-depth substantive eligible claim"
            )

    roles.sort(
        key=lambda item: (
            {"high": 0, "medium": 1, "low": 2, "unspecified": 3}.get(item["interest"], 4),
            {"active": 0, "selective": 1, "explore": 2, "paused": 3, "unspecified": 4}.get(
                item["application_priority"], 5
            ),
            item["id"],
        )
    )
    return {
        "schema_version": "1.0",
        "roles": roles,
        "summary": {
            "role_families": len(roles),
            "high_interest": sum(1 for item in roles if item["interest"] == "high"),
            "active": sum(1 for item in roles if item["application_priority"] == "active"),
            "substantive_claim_links": sum(
                item["substantive_claim_count"] for item in roles
            ),
        },
        "warnings": warnings,
        "policy": {
            "interest_is_not_evidence": True,
            "readiness_does_not_forbid_applying": True,
            "automatic_claim_promotion": False,
        },
    }


def render_text(result: dict[str, Any]) -> str:
    lines = [
        "Role strategy audit",
        "Role | Readiness | Interest / priority | Substantive eligible (strong/moderate/limited) | Stretch titles",
    ]
    for role in result["roles"]:
        depth = role["substantive_depth"]
        lines.append(
            f"- {role['id']} | {role['readiness']} | {role['interest']} / "
            f"{role['application_priority']} | {role['substantive_claim_count']} "
            f"({depth['strong']}/{depth['moderate']}/{depth['limited']}) | "
            f"{', '.join(role['stretch_titles']) or 'none'}"
        )
    if result["warnings"]:
        lines.append("Warnings:")
        lines.extend(f"- {warning}" for warning in result["warnings"])
    lines.append(
        "Policy: interest guides targeting; only eligible atomic claims may enter a CV."
    )
    return "\n".join(lines)


def main() -> int:
    root = find_project_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--master", type=Path, default=root / "meta" / "master_cv.yaml")
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--strict", action="store_true", help="Fail when high-interest roles lack strong evidence")
    args = parser.parse_args()
    try:
        result = audit_roles(load_master(args.master))
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False) if args.as_json else render_text(result))
    return 1 if args.strict and result["warnings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
