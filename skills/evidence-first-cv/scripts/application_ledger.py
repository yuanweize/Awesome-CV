#!/usr/bin/env python3
"""Maintain a private application/outcome ledger for evidence-based iteration."""

from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import sys
from pathlib import Path
from typing import Any

import yaml


STAGES = (
    "drafted",
    "applied",
    "recruiter-screen",
    "technical",
    "final",
    "offer",
    "rejected",
    "withdrawn",
    "no-response",
)
FUNNEL_STAGES = ("drafted", "applied", "recruiter-screen", "technical", "final", "offer")
TERMINAL_STAGES = ("rejected", "withdrawn", "no-response")
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


def find_project_root() -> Path:
    for candidate in [Path.cwd(), *Path.cwd().parents]:
        if (candidate / "templates" / "master_cv.yaml.example").is_file():
            return candidate
    return Path.cwd()


def today() -> str:
    return dt.date.today().isoformat()


def slug(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return cleaned or "application"


def load_ledger(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"schema_version": "1.0", "applications": []}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("applications"), list):
        raise ValueError(f"Invalid application ledger: {path}")
    validate_ledger(data)
    return data


def save_ledger(path: Path, data: dict[str, Any]) -> None:
    validate_ledger(data)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    temporary.replace(path)
    os.chmod(path, 0o600)


def validate_ledger(data: dict[str, Any]) -> None:
    if str(data.get("schema_version", "")) != "1.0":
        raise ValueError("Application ledger schema_version must be '1.0'")
    applications = data.get("applications")
    if not isinstance(applications, list):
        raise ValueError("Application ledger applications must be a list")

    seen: set[str] = set()
    for index, record in enumerate(applications, 1):
        if not isinstance(record, dict):
            raise ValueError(f"Application #{index} must be a mapping")
        application_id = record.get("id")
        if not isinstance(application_id, str) or not ID_PATTERN.fullmatch(application_id):
            raise ValueError(f"Application #{index} has an invalid ID")
        if application_id in seen:
            raise ValueError(f"Duplicate application ID: {application_id}")
        seen.add(application_id)
        stage = record.get("stage")
        if stage not in STAGES:
            raise ValueError(f"Application {application_id} has invalid stage: {stage}")
        events = record.get("events", [])
        if not isinstance(events, list):
            raise ValueError(f"Application {application_id} events must be a list")
        for event in events:
            if not isinstance(event, dict) or event.get("stage") not in STAGES:
                raise ValueError(f"Application {application_id} has an invalid event")


def load_master_index(path: Path) -> tuple[set[str], set[str], set[str]]:
    if not path.is_file():
        raise ValueError(f"Master database not found: {path}; run make init first")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Invalid master database: {path}")
    claim_items = [item for item in data.get("claim_registry", []) if isinstance(item, dict)]
    claims = {item.get("id") for item in claim_items if isinstance(item.get("id"), str)}
    eligible_claims = {
        item.get("id")
        for item in claim_items
        if isinstance(item.get("id"), str)
        and item.get("cv_eligible") is True
        and item.get("status") in {"verified", "self_reported"}
    }
    roles = set(data.get("role_families", {})) if isinstance(data.get("role_families"), dict) else set()
    return claims, eligible_claims, roles


def validate_requested_references(
    args: argparse.Namespace,
    claim_ids: set[str],
    eligible_claim_ids: set[str],
    role_ids: set[str],
) -> None:
    if args.command == "add" and args.role not in role_ids:
        raise ValueError(f"Unknown role family: {args.role}")
    if args.command == "update" and args.claims is not None:
        requested = {item.strip() for item in args.claims.split(",") if item.strip()}
        unknown = sorted(requested - claim_ids)
        if unknown:
            raise ValueError("Unknown claim ID(s): " + ", ".join(unknown))
        ineligible = sorted(requested - eligible_claim_ids)
        if ineligible:
            raise ValueError("Claim ID(s) are not CV-eligible: " + ", ".join(ineligible))


def find_record(data: dict[str, Any], application_id: str) -> dict[str, Any]:
    for record in data["applications"]:
        if record.get("id") == application_id:
            return record
    raise ValueError(f"Unknown application ID: {application_id}")


def command_add(args: argparse.Namespace, data: dict[str, Any]) -> None:
    prefix = f"{today().replace('-', '')}-{slug(args.company)}-{slug(args.title)}"
    existing = {item.get("id") for item in data["applications"]}
    application_id = args.id or prefix
    if not ID_PATTERN.fullmatch(application_id):
        raise ValueError("Application ID must use lowercase letters, numbers, dots, underscores, or hyphens")
    if args.id and application_id in existing:
        raise ValueError(f"Duplicate application ID: {application_id}")
    suffix = 2
    while application_id in existing:
        application_id = f"{prefix}-{suffix}"
        suffix += 1
    record = {
        "id": application_id,
        "company": args.company,
        "title": args.title,
        "role_family": args.role,
        "jd_file": args.jd,
        "profile": args.profile or "",
        "source": args.source or "",
        "stage": "drafted",
        "claims_used": [],
        "created_at": args.date or today(),
        "updated_at": today(),
        "events": [{"date": args.date or today(), "stage": "drafted", "note": args.note or ""}],
    }
    data["applications"].append(record)
    print(application_id)


def command_update(args: argparse.Namespace, data: dict[str, Any]) -> None:
    record = find_record(data, args.id)
    if args.stage is None and args.note is None and args.profile is None and args.claims is None:
        raise ValueError("Update requires --stage, --note, --profile, or --claims")
    stage = args.stage or record.get("stage", "drafted")
    record["stage"] = stage
    record["updated_at"] = today()
    if args.profile is not None:
        record["profile"] = args.profile
    if args.claims is not None:
        record["claims_used"] = sorted({item.strip() for item in args.claims.split(",") if item.strip()})
    if args.note or args.stage:
        record.setdefault("events", []).append(
            {"date": args.date or today(), "stage": stage, "note": args.note or ""}
        )
    print(f"Updated {args.id}: {stage}")


def command_list(data: dict[str, Any]) -> None:
    print("ID\tSTAGE\tROLE\tCOMPANY\tTITLE")
    for item in sorted(data["applications"], key=lambda value: value.get("created_at", ""), reverse=True):
        print(
            f"{item.get('id', '')}\t{item.get('stage', '')}\t{item.get('role_family', '')}\t"
            f"{item.get('company', '')}\t{item.get('title', '')}"
        )


def command_show(args: argparse.Namespace, data: dict[str, Any]) -> None:
    print(yaml.safe_dump(find_record(data, args.id), sort_keys=False, allow_unicode=True))


def command_summary(data: dict[str, Any]) -> None:
    applications = data["applications"]
    reached = {stage: 0 for stage in STAGES}
    for item in applications:
        seen = {event.get("stage") for event in item.get("events", [])}
        seen.add(item.get("stage"))
        progress = [FUNNEL_STAGES.index(stage) for stage in seen if stage in FUNNEL_STAGES]
        if progress:
            furthest = max(progress)
            for stage in FUNNEL_STAGES[: furthest + 1]:
                reached[stage] += 1
        current_stage = item.get("stage")
        if current_stage in TERMINAL_STAGES:
            reached[current_stage] += 1
    applied = reached["applied"]
    screens = reached["recruiter-screen"]
    technical = reached["technical"]
    offers = reached["offer"]
    print(f"Applications recorded: {len(applications)}")
    print(f"Applied: {applied}")
    print(f"Recruiter screens: {screens} ({screens / applied:.1%} of applied)" if applied else "Recruiter screens: 0")
    print(f"Technical interviews: {technical} ({technical / screens:.1%} of screens)" if screens else "Technical interviews: 0")
    print(f"Offers: {offers} ({offers / technical:.1%} of technical)" if technical else "Offers: 0")
    print(f"Rejected: {reached['rejected']}")
    print(f"Withdrawn: {reached['withdrawn']}")
    print(f"Closed without response: {reached['no-response']}")


def main() -> int:
    project_root = find_project_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ledger",
        type=Path,
        default=project_root / "meta" / "applications.yaml",
        help="Private ledger path (default: meta/applications.yaml)",
    )
    parser.add_argument(
        "--master",
        type=Path,
        default=project_root / "meta" / "master_cv.yaml",
        help="Master YAML used to verify new role/claim references",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    add = subparsers.add_parser("add", help="Create a drafted application record")
    add.add_argument("--company", required=True)
    add.add_argument("--title", required=True)
    add.add_argument("--role", required=True)
    add.add_argument("--jd", required=True)
    add.add_argument("--profile")
    add.add_argument("--source")
    add.add_argument("--note")
    add.add_argument("--id", help="Stable application ID; useful for importing legacy history")
    add.add_argument("--date", help="Original event date; use 'unknown' when it was not recorded")

    update = subparsers.add_parser("update", help="Record a stage, note, profile, or claims")
    update.add_argument("id")
    update.add_argument("--stage", choices=STAGES)
    update.add_argument("--note")
    update.add_argument("--profile")
    update.add_argument("--claims", help="Comma-separated claim IDs used in the CV")
    update.add_argument("--date", help="Original event date; use 'unknown' when it was not recorded")

    show = subparsers.add_parser("show", help="Show one application")
    show.add_argument("id")
    subparsers.add_parser("list", help="List applications")
    subparsers.add_parser("summary", help="Show funnel metrics")

    args = parser.parse_args()
    try:
        data = load_ledger(args.ledger)
        if args.command in {"add", "update"}:
            claim_ids, eligible_claim_ids, role_ids = load_master_index(args.master)
            validate_requested_references(args, claim_ids, eligible_claim_ids, role_ids)
        if args.command == "add":
            command_add(args, data)
            save_ledger(args.ledger, data)
        elif args.command == "update":
            command_update(args, data)
            save_ledger(args.ledger, data)
        elif args.command == "show":
            command_show(args, data)
        elif args.command == "list":
            command_list(data)
        elif args.command == "summary":
            command_summary(data)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
