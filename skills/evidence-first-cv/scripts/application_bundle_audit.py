#!/usr/bin/env python3
"""Audit every PDF declared in an application manifest as one delivery bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from resume_pdf_audit import audit_pdf


DOCUMENTS = {
    "cv": {
        "path": "cv_pdf",
        "sha256": "cv_sha256",
        "pages": "page_count",
        "max_pages": 1,
        "min_bottom_coverage": 0.75,
    },
    "cover_letter": {
        "path": "cover_letter_pdf",
        "sha256": "cover_letter_sha256",
        "pages": "cover_letter_page_count",
        "max_pages": 1,
        "min_bottom_coverage": 0.65,
    },
    "application": {
        "path": "application_pdf",
        "sha256": "application_sha256",
        "pages": "application_page_count",
        "max_pages": 2,
        "min_bottom_coverage": 0.65,
    },
}


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_project_root(manifest: Path) -> Path:
    for candidate in [Path.cwd(), *Path.cwd().parents, manifest.resolve(), *manifest.resolve().parents]:
        if candidate.is_file():
            candidate = candidate.parent
        if (candidate / "templates" / "master_cv.yaml.example").is_file():
            return candidate
    raise ValueError("cannot locate project root containing templates/master_cv.yaml.example")


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError(f"cannot read manifest {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("manifest root must be a mapping")
    return data


def audit_bundle(manifest_path: Path, project_root: Path | None = None) -> dict[str, Any]:
    data = load_manifest(manifest_path)
    root = (project_root or find_project_root(manifest_path)).resolve()
    deliverables = data.get("deliverables", ["cv"])
    if not isinstance(deliverables, list) or not deliverables:
        raise ValueError("manifest deliverables must be a non-empty list")
    artifacts = data.get("artifacts")
    if not isinstance(artifacts, dict):
        raise ValueError("manifest artifacts must be a mapping")

    errors: list[str] = []
    documents: dict[str, Any] = {}
    documents_to_check = list(deliverables)
    if isinstance(artifacts.get("application_pdf"), str) and artifacts.get("application_pdf", "").strip():
        documents_to_check.append("application")
    for kind in documents_to_check:
        config = DOCUMENTS.get(kind)
        if config is None:
            errors.append(f"unsupported deliverable: {kind}")
            continue
        raw_path = artifacts.get(config["path"])
        if not isinstance(raw_path, str) or not raw_path.strip():
            errors.append(f"missing artifacts.{config['path']} for {kind}")
            continue
        path = Path(raw_path)
        path = path.resolve() if path.is_absolute() else (root / path).resolve()
        allowed_roots = [
            (root / "workspace" / "profiles").resolve(),
            (root / "workspace" / "build").resolve(),
        ]
        if not any(path.is_relative_to(candidate) for candidate in allowed_roots):
            errors.append(
                f"{kind} artifact must stay under workspace/profiles/ or workspace/build/"
            )
            continue
        if not path.is_file():
            errors.append(f"{kind} artifact not found: {raw_path}")
            continue

        expected_hash = artifacts.get(config["sha256"])
        actual_hash = file_sha256(path)
        if expected_hash != actual_hash:
            errors.append(f"{kind} SHA-256 does not match the manifest")
        expected_pages = artifacts.get(config["pages"])
        result = audit_pdf(
            path,
            max_pages=int(config["max_pages"]),
            min_bottom_coverage=float(config["min_bottom_coverage"]),
            min_median_word_height=12.0,
        )
        if expected_pages != result["pages"]:
            errors.append(
                f"{kind} page count {result['pages']} does not match manifest value {expected_pages}"
            )
        errors.extend(f"{kind}: {message}" for message in result["errors"])
        documents[kind] = result

    return {
        "ok": not errors,
        "manifest": str(manifest_path),
        "deliverables": deliverables,
        "documents": documents,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--project-root", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        result = audit_bundle(args.manifest, args.project_root)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for kind, document in result["documents"].items():
            first_page = document["page_metrics"][0]["bottom_coverage"]
            print(
                f"{kind}: pages={document['pages']} words={document['words']} "
                f"median_word_height={document['median_word_height']:.2f}pt "
                f"first_page_bottom={first_page:.1%}"
            )
        for error in result["errors"]:
            print(f"ERROR: {error}", file=sys.stderr)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
