#!/usr/bin/env python3
"""Validate the lightweight Golden Pack registry and protected artifacts."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml


SUPPORTED_SCHEMA_VERSIONS = {"1.0"}
STATUSES = {"draft", "freeze-candidate", "approved", "retired"}
ARTIFACT_KINDS = {"cv", "portfolio", "combined"}
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
PACK_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


def find_project_root() -> Path:
    for candidate in [Path.cwd(), *Path.cwd().parents, Path(__file__).resolve(), *Path(__file__).resolve().parents]:
        if candidate.is_file():
            candidate = candidate.parent
        if (candidate / "templates" / "master_cv.yaml.example").is_file():
            return candidate
    raise ValueError("cannot locate the Awesome-CV repository root")


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError(f"cannot read Golden Pack registry {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("Golden Pack registry root must be a mapping")
    return data


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_fingerprint(path: Path) -> str:
    """Hash relative paths and bytes for a symlink-free Golden source tree."""
    if not path.is_dir() or path.is_symlink():
        raise ValueError(f"Golden Pack source is missing or unsafe: {path}")
    digest = hashlib.sha256()
    files = sorted(item for item in path.rglob("*") if item.is_file())
    if not files:
        raise ValueError(f"Golden Pack source is empty: {path}")
    for item in files:
        if item.is_symlink():
            raise ValueError(f"Golden Pack source contains a symbolic link: {item}")
        relative = item.relative_to(path).as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(4, "big"))
        digest.update(relative)
        digest.update(bytes.fromhex(file_sha256(item)))
    return digest.hexdigest()


def pdf_page_count(path: Path) -> int:
    completed = subprocess.run(
        ["pdfinfo", str(path)], check=False, capture_output=True, text=True
    )
    if completed.returncode != 0:
        raise ValueError(completed.stderr.strip() or f"pdfinfo failed for {path}")
    for line in completed.stdout.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":", 1)[1].strip())
    raise ValueError(f"pdfinfo did not report a page count for {path}")


def resolve_scoped_path(root: Path, raw: Any, scope: str, field: str) -> Path:
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError(f"{field} is required")
    candidate = (root / raw).resolve() if not Path(raw).is_absolute() else Path(raw).resolve()
    allowed = (root / scope).resolve()
    if not candidate.is_relative_to(allowed):
        raise ValueError(f"{field} must stay under {scope}/")
    return candidate


def audit_registry(root: Path, registry_path: Path) -> dict[str, Any]:
    root = root.resolve()
    data = load_yaml(registry_path)
    errors: list[str] = []
    warnings: list[str] = []
    results: dict[str, Any] = {}

    if str(data.get("schema_version", "")) not in SUPPORTED_SCHEMA_VERSIONS:
        errors.append("schema_version must be 1.0")
    packs = data.get("packs")
    if not isinstance(packs, dict):
        errors.append("packs must be a mapping")
        packs = {}
    if not packs:
        errors.append("packs must contain at least one Golden Pack")
    for pack_id in packs:
        if not isinstance(pack_id, str) or not PACK_ID_PATTERN.fullmatch(pack_id):
            errors.append(
                f"invalid Golden Pack ID {pack_id!r}; use lowercase letters, numbers, underscores, or hyphens"
            )

    for pack_id in sorted(key for key in packs if isinstance(key, str) and PACK_ID_PATTERN.fullmatch(key)):
        item = packs.get(pack_id)
        prefix = f"packs.{pack_id}"
        pack_errors: list[str] = []
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be a mapping")
            continue
        version = item.get("version")
        status = item.get("status")
        if not isinstance(version, str) or not re.fullmatch(r"v\d+\.\d+", version):
            pack_errors.append(f"{prefix}.version must look like v2.0")
        if status not in STATUSES:
            pack_errors.append(f"{prefix}.status is invalid")
        roles = item.get("role_families")
        if not isinstance(roles, list) or not roles or not all(isinstance(role, str) and role for role in roles):
            pack_errors.append(f"{prefix}.role_families must be a non-empty string list")
        approved_at = item.get("approved_at", "")
        if status == "approved":
            try:
                dt.date.fromisoformat(approved_at)
            except (TypeError, ValueError):
                pack_errors.append(f"{prefix}.approved_at must be an ISO date when approved")
        elif approved_at:
            pack_errors.append(f"{prefix}.approved_at must stay empty until Owner approval")

        snapshot: Path | None = None
        profile: Path | None = None
        actual_source_hash = ""
        try:
            snapshot = resolve_scoped_path(root, item.get("source_snapshot"), "workspace/golden-packs", f"{prefix}.source_snapshot")
            actual_source_hash = source_fingerprint(snapshot)
        except ValueError as exc:
            pack_errors.append(str(exc))
        expected_source_hash = item.get("source_sha256")
        if actual_source_hash and expected_source_hash != actual_source_hash:
            pack_errors.append(f"{prefix}.source_sha256 does not match the frozen source")
        try:
            profile = resolve_scoped_path(root, item.get("source_profile"), "workspace/profiles", f"{prefix}.source_profile")
            profile_hash = source_fingerprint(profile)
            if actual_source_hash and profile_hash != actual_source_hash:
                message = f"{prefix}.source_profile differs from the frozen source snapshot"
                if status == "approved":
                    pack_errors.append(message)
                else:
                    warnings.append(message)
        except ValueError as exc:
            pack_errors.append(str(exc))

        artifacts = item.get("artifacts")
        artifact_results: dict[str, Any] = {}
        if not isinstance(artifacts, dict):
            pack_errors.append(f"{prefix}.artifacts must be a mapping")
            artifacts = {}
        if set(artifacts) != ARTIFACT_KINDS:
            pack_errors.append(f"{prefix}.artifacts must contain cv, portfolio, and combined")
        for kind in sorted(ARTIFACT_KINDS & set(artifacts)):
            artifact = artifacts.get(kind)
            artifact_prefix = f"{prefix}.artifacts.{kind}"
            if not isinstance(artifact, dict):
                pack_errors.append(f"{artifact_prefix} must be a mapping")
                continue
            try:
                pdf = resolve_scoped_path(root, artifact.get("path"), "output/pdf/golden-packs", f"{artifact_prefix}.path")
                if not pdf.is_file() or pdf.is_symlink():
                    raise ValueError(f"{artifact_prefix}.path is missing or unsafe")
                actual_hash = file_sha256(pdf)
                actual_pages = pdf_page_count(pdf)
            except (OSError, ValueError) as exc:
                pack_errors.append(str(exc))
                continue
            expected_hash = artifact.get("sha256")
            expected_pages = artifact.get("page_count")
            if not isinstance(expected_hash, str) or not SHA256_PATTERN.fullmatch(expected_hash):
                pack_errors.append(f"{artifact_prefix}.sha256 must be a lowercase SHA-256")
            elif expected_hash != actual_hash:
                pack_errors.append(f"{artifact_prefix}.sha256 does not match the PDF")
            if not isinstance(expected_pages, int) or expected_pages < 1:
                pack_errors.append(f"{artifact_prefix}.page_count must be positive")
            elif expected_pages != actual_pages:
                pack_errors.append(f"{artifact_prefix}.page_count does not match the PDF")
            artifact_results[kind] = {
                "path": str(pdf.relative_to(root)),
                "sha256": actual_hash,
                "page_count": actual_pages,
            }

        errors.extend(pack_errors)
        results[pack_id] = {
            "version": version,
            "status": status,
            "source_sha256": actual_source_hash,
            "artifacts": artifact_results,
            "ok": not pack_errors,
        }

    return {
        "ok": not errors,
        "registry": str(registry_path),
        "packs": results,
        "warnings": warnings,
        "errors": errors,
    }


def render_text(report: dict[str, Any]) -> str:
    lines = [f"Golden Pack registry: {'PASS' if report['ok'] else 'FAIL'}"]
    for pack_id, item in report["packs"].items():
        lines.append(f"- {pack_id}: {item['version']} · {item['status']} · {'PASS' if item['ok'] else 'FAIL'}")
        for kind, artifact in item["artifacts"].items():
            lines.append(f"  {kind}: {artifact['page_count']} pages · {artifact['sha256']}")
    lines.extend(f"WARNING: {message}" for message in report["warnings"])
    lines.extend(f"ERROR: {message}" for message in report["errors"])
    return "\n".join(lines)


def main() -> int:
    root = find_project_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=root / "meta" / "golden_packs.yaml")
    parser.add_argument("--project-root", type=Path, default=root)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    try:
        report = audit_registry(args.project_root, args.registry)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2) if args.json else render_text(report))
    return 1 if args.strict and not report["ok"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
