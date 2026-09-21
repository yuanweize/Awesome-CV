#!/usr/bin/env python3
"""Build and audit the deterministic application delivery matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path
from typing import Any

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from cover_letter_audit import PLACEHOLDER_PATTERN, audit_text, extract_text


MATRIX = (
    ("cv", "CV", ("cv",)),
    ("portfolio", "Portfolio", ("portfolio",)),
    ("cover_letter", "Cover_Letter", ("cover_letter",)),
    ("cv_cover_letter", "CV_Cover_Letter", ("cv", "cover_letter")),
    ("cv_portfolio", "CV_Portfolio", ("cv", "portfolio")),
    ("cover_letter_portfolio", "Cover_Letter_Portfolio", ("cover_letter", "portfolio")),
    ("complete_application", "Complete_Application", ("cover_letter", "cv", "portfolio")),
)
MATRIX_KINDS = tuple(item[0] for item in MATRIX)
CONTENT_LABELS = {
    "cv": "CV",
    "portfolio": "Portfolio",
    "cover_letter": "Cover Letter",
}
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
SAFE_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


class GoldenIntegrityError(ValueError):
    """The selected approved Pack cannot safely be reused."""


def find_project_root() -> Path:
    candidates = [Path.cwd(), *Path.cwd().parents, Path(__file__).resolve(), *Path(__file__).resolve().parents]
    for candidate in candidates:
        if candidate.is_file():
            candidate = candidate.parent
        if (candidate / "templates" / "master_cv.yaml.example").is_file():
            return candidate.resolve()
    raise ValueError("cannot locate the Awesome-CV repository root")


def load_yaml(path: Path, label: str) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError(f"cannot read {label} {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{label} root must be a mapping")
    return data


def save_yaml(path: Path, data: dict[str, Any]) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )
    temporary.replace(path)
    os.chmod(path, 0o600)


def save_text(path: Path, value: str) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    if temporary.is_symlink():
        raise ValueError(f"refusing to use symbolic-link temporary file: {temporary}")
    temporary.write_text(value, encoding="utf-8")
    temporary.replace(path)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
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


def qpdf_check(path: Path) -> None:
    completed = subprocess.run(
        ["qpdf", "--check", str(path)], check=False, capture_output=True, text=True
    )
    if completed.returncode != 0:
        raise ValueError(completed.stderr.strip() or f"qpdf check failed for {path}")


def resolve_application(root: Path, raw: str) -> Path:
    candidate = Path(raw)
    if candidate.is_file():
        path = candidate.resolve()
    elif SAFE_ID_PATTERN.fullmatch(raw):
        path = (root / "meta" / "applications" / raw / "application.yaml").resolve()
    else:
        raise ValueError("application must be a safe ID or a manifest path")
    private_root = (root / "meta" / "applications").resolve()
    if not path.is_relative_to(private_root) or path.name != "application.yaml":
        raise ValueError("application manifest must stay under meta/applications/<id>/")
    if not path.is_file():
        raise ValueError(f"application manifest not found: {path}")
    return path


def resolve_repo_path(root: Path, raw: Any, *, allowed: tuple[str, ...], field: str) -> Path:
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError(f"{field} is required")
    candidate = (root / raw).resolve() if not Path(raw).is_absolute() else Path(raw).resolve()
    if not any(candidate.is_relative_to((root / prefix).resolve()) for prefix in allowed):
        raise ValueError(f"{field} is outside its allowed repository scope")
    return candidate


def relative_path(root: Path, path: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def candidate_prefix(name: str) -> str:
    ascii_name = (
        unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    )
    value = re.sub(r"[^A-Za-z0-9]+", "_", ascii_name).strip("_")
    if not value:
        raise ValueError("candidate name cannot produce a safe filename prefix")
    return value


def default_output_dir(root: Path, manifest: dict[str, Any]) -> Path:
    application_id = str(manifest.get("application_id", ""))
    if not SAFE_ID_PATTERN.fullmatch(application_id):
        raise ValueError("application_id cannot produce a safe output directory")
    return root / "output" / "pdf" / "applications" / application_id


def selected_pack(
    root: Path, manifest: dict[str, Any], registry_path: Path
) -> tuple[str, dict[str, Any], dict[str, dict[str, Any]]]:
    registry = load_yaml(registry_path, "Golden Pack registry")
    packs = registry.get("packs")
    if not isinstance(packs, dict):
        raise GoldenIntegrityError("GOLDEN INTEGRITY FAILURE: registry packs are invalid")
    binding = manifest.get("golden_pack")
    if not isinstance(binding, dict):
        raise GoldenIntegrityError("GOLDEN INTEGRITY FAILURE: manifest has no Pack binding")
    pack_id = binding.get("selected_pack")
    pack = packs.get(pack_id) if isinstance(pack_id, str) else None
    if not isinstance(pack, dict):
        raise GoldenIntegrityError("GOLDEN INTEGRITY FAILURE: selected Pack is missing")
    if pack.get("status") != "approved":
        raise GoldenIntegrityError("GOLDEN INTEGRITY FAILURE: selected Pack is not approved")
    if binding.get("version") != pack.get("version"):
        raise GoldenIntegrityError("GOLDEN INTEGRITY FAILURE: Pack version mismatch")

    artifacts = pack.get("artifacts")
    if not isinstance(artifacts, dict):
        raise GoldenIntegrityError("GOLDEN INTEGRITY FAILURE: Pack artifacts are invalid")
    verified: dict[str, dict[str, Any]] = {}
    for kind in ("cv", "portfolio", "combined"):
        item = artifacts.get(kind)
        if not isinstance(item, dict):
            raise GoldenIntegrityError(f"GOLDEN INTEGRITY FAILURE: {kind} artifact is missing")
        path = resolve_repo_path(
            root,
            item.get("path"),
            allowed=("output/pdf/golden-packs",),
            field=f"packs.{pack_id}.artifacts.{kind}.path",
        )
        if not path.is_file() or path.is_symlink():
            raise GoldenIntegrityError(f"GOLDEN INTEGRITY FAILURE: {kind} PDF is missing or unsafe")
        actual_hash = file_sha256(path)
        actual_pages = pdf_page_count(path)
        if item.get("sha256") != actual_hash:
            raise GoldenIntegrityError(f"GOLDEN INTEGRITY FAILURE: {kind} hash mismatch")
        if item.get("page_count") != actual_pages:
            raise GoldenIntegrityError(f"GOLDEN INTEGRITY FAILURE: {kind} page-count mismatch")
        qpdf_check(path)
        verified[kind] = {
            "path": path,
            "sha256": actual_hash,
            "page_count": actual_pages,
        }

    if binding.get("cv_sha256") != verified["cv"]["sha256"]:
        raise GoldenIntegrityError("GOLDEN INTEGRITY FAILURE: manifest CV binding mismatch")
    bound_portfolio = binding.get("portfolio_sha256", "")
    if bound_portfolio and bound_portfolio != verified["portfolio"]["sha256"]:
        raise GoldenIntegrityError("GOLDEN INTEGRITY FAILURE: manifest Portfolio binding mismatch")
    return str(pack_id), pack, verified


def atomic_copy(source: Path, destination: Path) -> None:
    if destination.exists() and source.resolve() == destination.resolve():
        return
    if destination.is_symlink():
        raise ValueError(f"refusing to overwrite symbolic link: {destination}")
    temporary = destination.with_name(f".{destination.name}.tmp")
    if temporary.is_symlink():
        raise ValueError(f"refusing to use symbolic-link temporary file: {temporary}")
    shutil.copyfile(source, temporary)
    temporary.replace(destination)


def merge_pdfs(inputs: tuple[Path, ...], destination: Path) -> None:
    if destination.is_symlink():
        raise ValueError(f"refusing to overwrite symbolic link: {destination}")
    temporary = destination.with_name(f".{destination.stem}.tmp.pdf")
    if temporary.is_symlink():
        raise ValueError(f"refusing to use symbolic-link temporary file: {temporary}")
    temporary.unlink(missing_ok=True)
    command = ["qpdf", "--deterministic-id", "--empty", "--pages"]
    for source in inputs:
        command.extend((str(source), "1-z"))
    command.extend(("--", str(temporary)))
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        temporary.unlink(missing_ok=True)
        raise ValueError(completed.stderr.strip() or "qpdf merge failed")
    temporary.replace(destination)


def recommendation_defaults(prefix: str, portal_note: bool) -> dict[str, str]:
    return {
        "cv": f"{prefix}_CV.pdf",
        "portfolio": f"{prefix}_Portfolio.pdf when an additional work-sample slot exists",
        "cover_letter": (
            "paste portal_note.md or the cover-letter text"
            if portal_note
            else f"paste the letter text or attach {prefix}_Cover_Letter.pdf"
        ),
        "recommended_upload": f"{prefix}_CV.pdf for an ATS CV field",
        "single_recruiter_attachment": f"{prefix}_Complete_Application.pdf",
    }


def verify_portal_note(
    root: Path,
    artifacts: dict[str, Any],
    *,
    application_dir: Path | None = None,
    bind_hash: bool = False,
) -> list[str]:
    raw_path = artifacts.get("portal_note_path", "")
    expected_hash = artifacts.get("portal_note_sha256", "")
    if not raw_path and not expected_hash:
        return []
    if not raw_path:
        return ["portal-note hash is present but portal_note_path is missing"]
    try:
        path = resolve_repo_path(
            root,
            raw_path,
            allowed=("meta/applications",),
            field="artifacts.portal_note_path",
        )
        if application_dir is not None and path.parent != application_dir.resolve():
            raise ValueError("portal note must stay in the current application directory")
        if not path.is_file() or path.is_symlink():
            raise ValueError("portal note is missing or unsafe")
        actual_hash = file_sha256(path)
        if expected_hash and expected_hash != actual_hash:
            raise ValueError("portal-note hash does not match the manifest")
        if PLACEHOLDER_PATTERN.search(path.read_text(encoding="utf-8")):
            raise ValueError("portal note contains placeholder text")
        if bind_hash:
            artifacts["portal_note_sha256"] = actual_hash
        return []
    except (OSError, UnicodeError, ValueError) as exc:
        return [str(exc)]


def render_readme(
    manifest: dict[str, Any], pack_id: str, pack: dict[str, Any], entries: list[dict[str, Any]]
) -> str:
    target = manifest.get("target", {})
    recommendation = manifest.get("submission_recommendation", {})
    if not isinstance(recommendation, dict):
        recommendation = {}
    lines = [
        f"# {target.get('company', '')} - {target.get('title', '')}",
        "",
        f"Status: {manifest.get('stage', 'draft')} (not submitted unless submission metadata says otherwise)",
        f"Selected Pack: {pack_id} {pack.get('version', '')} ({pack.get('status', '')})",
        "",
        "## Artifact matrix",
        "",
        "| Filename | Contents | Pages | SHA-256 | Intended use |",
        "|---|---|---:|---|---|",
    ]
    uses = {
        "cv": "ATS CV field",
        "portfolio": "Additional work-sample field",
        "cover_letter": "Separate letter field or source for pasted introduction",
        "cv_cover_letter": "Single field requesting CV and letter",
        "cv_portfolio": "Explicit CV plus Portfolio request",
        "cover_letter_portfolio": "Supporting-material field with no separate letter slot",
        "complete_application": "Single direct recruiter or hiring-manager attachment",
    }
    for entry in entries:
        contents = " -> ".join(CONTENT_LABELS[item] for item in entry["contents"])
        lines.append(
            f"| `{Path(entry['path']).name}` | {contents} | {entry['page_count']} | "
            f"`{entry['sha256']}` | {uses[entry['kind']]} |"
        )
    lines.extend(("", "## Recommended submission", ""))
    for key in ("cv", "portfolio", "cover_letter", "recommended_upload", "single_recruiter_attachment"):
        value = recommendation.get(key)
        if isinstance(value, str) and value.strip():
            lines.append(f"- {key.replace('_', ' ').title()}: {value.strip()}")
    lines.extend(
        (
            "",
            "Choose the smallest artifact that matches the portal's actual fields; do not upload all seven.",
            "Validation is not submission.",
            "",
        )
    )
    return "\n".join(lines)


def audit_matrix_data(
    root: Path, manifest: dict[str, Any], registry_path: Path
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        pack_id, pack, golden = selected_pack(root, manifest, registry_path)
    except (OSError, ValueError) as exc:
        return {"ok": False, "errors": [str(exc)], "warnings": [], "artifacts": []}

    artifacts = manifest.get("artifacts")
    matrix = artifacts.get("delivery_matrix") if isinstance(artifacts, dict) else None
    if not isinstance(matrix, list):
        return {
            "ok": False,
            "errors": ["delivery matrix is missing from the application manifest"],
            "warnings": [],
            "artifacts": [],
        }
    errors.extend(verify_portal_note(root, artifacts))
    if [item.get("kind") for item in matrix if isinstance(item, dict)] != list(MATRIX_KINDS):
        errors.append("delivery matrix kinds/order do not match the canonical seven artifacts")

    component_pages = {
        "cv": golden["cv"]["page_count"],
        "portfolio": golden["portfolio"]["page_count"],
    }
    cover_letter_text = ""
    audited_entries: list[dict[str, Any]] = []
    expected_specs = {kind: contents for kind, _suffix, contents in MATRIX}
    for item in matrix:
        if not isinstance(item, dict):
            errors.append("delivery matrix entry must be a mapping")
            continue
        kind = item.get("kind")
        contents = item.get("contents")
        if kind not in expected_specs or tuple(contents or ()) != expected_specs.get(kind):
            errors.append(f"delivery matrix contents/order are invalid for {kind}")
            continue
        try:
            path = resolve_repo_path(
                root,
                item.get("path"),
                allowed=("output/pdf",),
                field=f"delivery_matrix.{kind}.path",
            )
            if not path.is_file() or path.is_symlink():
                raise ValueError(f"delivery artifact is missing or unsafe: {path}")
            qpdf_check(path)
            actual_hash = file_sha256(path)
            actual_pages = pdf_page_count(path)
            if item.get("sha256") != actual_hash:
                errors.append(f"delivery artifact hash mismatch: {kind}")
            expected_pages = sum(
                component_pages.get(component, 0) for component in expected_specs[kind]
            )
            if "cover_letter" in expected_specs[kind]:
                declared_cover_pages = artifacts.get("cover_letter_page_count", 0)
                expected_pages += int(declared_cover_pages) if isinstance(declared_cover_pages, int) else 0
            if item.get("page_count") != actual_pages or actual_pages != expected_pages:
                errors.append(f"delivery artifact page-count/order contract failed: {kind}")
            audited_entries.append(
                {"kind": kind, "path": relative_path(root, path), "sha256": actual_hash, "page_count": actual_pages}
            )
            if kind == "cover_letter":
                cover_letter_text, cover_pages = extract_text(path)
                target = manifest.get("target", {})
                cl_report = audit_text(
                    cover_letter_text,
                    company=str(target.get("company", "")),
                    role=str(target.get("title", "")),
                    pages=cover_pages,
                )
                warnings.extend(cl_report["warnings"])
        except (OSError, ValueError) as exc:
            errors.append(str(exc))

    if cover_letter_text and PLACEHOLDER_PATTERN.search(cover_letter_text):
        errors.append("cover letter contains placeholder text")
    return {
        "ok": not errors,
        "pack": pack_id,
        "version": pack.get("version"),
        "errors": errors,
        "warnings": warnings,
        "artifacts": audited_entries,
    }


def build_matrix(
    root: Path,
    manifest_path: Path,
    *,
    registry_path: Path,
    output_dir: Path | None = None,
    name: str = "",
) -> dict[str, Any]:
    manifest = load_yaml(manifest_path, "application manifest")
    pack_id, pack, golden = selected_pack(root, manifest, registry_path)
    master = load_yaml(root / "meta" / "master_cv.yaml", "master CV")
    full_name = name or str(master.get("personal_information", {}).get("full_name", ""))
    prefix = candidate_prefix(full_name)

    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict):
        raise ValueError("manifest artifacts must be a mapping")
    portal_note_errors = verify_portal_note(
        root,
        artifacts,
        application_dir=manifest_path.parent,
        bind_hash=True,
    )
    if portal_note_errors:
        raise ValueError("; ".join(portal_note_errors))
    cover_source = resolve_repo_path(
        root,
        artifacts.get("cover_letter_pdf"),
        allowed=("workspace/build", "workspace/profiles", "output/pdf"),
        field="artifacts.cover_letter_pdf",
    )
    if not cover_source.is_file() or cover_source.is_symlink():
        raise ValueError("cover-letter PDF is missing or unsafe")
    if artifacts.get("cover_letter_sha256") and artifacts.get("cover_letter_sha256") != file_sha256(cover_source):
        raise ValueError("cover-letter hash does not match the manifest")
    qpdf_check(cover_source)

    destination = (output_dir or default_output_dir(root, manifest)).resolve()
    output_root = (root / "output" / "pdf").resolve()
    golden_root = (output_root / "golden-packs").resolve()
    if not destination.is_relative_to(output_root) or destination.is_relative_to(golden_root):
        raise ValueError("application output must stay under output/pdf/ and outside golden-packs/")
    if destination.is_symlink():
        raise ValueError("application output directory must not be a symbolic link")
    destination.mkdir(parents=True, exist_ok=True)

    paths = {
        kind: destination / f"{prefix}_{suffix}.pdf" for kind, suffix, _contents in MATRIX
    }
    before = {kind: file_sha256(item["path"]) for kind, item in golden.items()}
    atomic_copy(golden["cv"]["path"], paths["cv"])
    atomic_copy(golden["portfolio"]["path"], paths["portfolio"])
    atomic_copy(cover_source, paths["cover_letter"])
    merge_pdfs((paths["cv"], paths["cover_letter"]), paths["cv_cover_letter"])
    atomic_copy(golden["combined"]["path"], paths["cv_portfolio"])
    merge_pdfs((paths["cover_letter"], paths["portfolio"]), paths["cover_letter_portfolio"])
    merge_pdfs(
        (paths["cover_letter"], paths["cv"], paths["portfolio"]),
        paths["complete_application"],
    )
    after = {kind: file_sha256(item["path"]) for kind, item in golden.items()}
    if before != after:
        raise GoldenIntegrityError("GOLDEN INTEGRITY FAILURE: application build mutated approved artifacts")

    entries: list[dict[str, Any]] = []
    for kind, _suffix, contents in MATRIX:
        path = paths[kind]
        qpdf_check(path)
        entries.append(
            {
                "kind": kind,
                "contents": list(contents),
                "path": relative_path(root, path),
                "sha256": file_sha256(path),
                "page_count": pdf_page_count(path),
            }
        )

    binding = manifest.setdefault("golden_pack", {})
    binding["portfolio_sha256"] = golden["portfolio"]["sha256"]
    artifacts.update(
        {
            "cv_pdf": relative_path(root, paths["cv"]),
            "cv_sha256": entries[0]["sha256"],
            "page_count": entries[0]["page_count"],
            "portfolio_pdf": relative_path(root, paths["portfolio"]),
            "portfolio_sha256": entries[1]["sha256"],
            "portfolio_page_count": entries[1]["page_count"],
            "cover_letter_pdf": relative_path(root, paths["cover_letter"]),
            "cover_letter_sha256": entries[2]["sha256"],
            "cover_letter_page_count": entries[2]["page_count"],
            "application_pdf": relative_path(root, paths["cv_cover_letter"]),
            "application_sha256": entries[3]["sha256"],
            "application_page_count": entries[3]["page_count"],
            "delivery_matrix": entries,
        }
    )
    portal_note = artifacts.get("portal_note_path")
    defaults = recommendation_defaults(prefix, bool(portal_note))
    recommendation = manifest.get("submission_recommendation")
    if not isinstance(recommendation, dict):
        recommendation = {}
    for key, value in defaults.items():
        if not isinstance(recommendation.get(key), str) or not recommendation[key].strip():
            recommendation[key] = value
    manifest["submission_recommendation"] = recommendation
    readme = destination / "README.md"
    save_text(readme, render_readme(manifest, pack_id, pack, entries))

    report = audit_matrix_data(root, manifest, registry_path)
    if not report["ok"]:
        raise ValueError("; ".join(report["errors"]))
    save_yaml(manifest_path, manifest)
    report.update({"manifest": relative_path(root, manifest_path), "readme": relative_path(root, readme)})
    return report


def render_report(report: dict[str, Any]) -> str:
    lines = [
        f"Application delivery matrix: {'PASS' if report.get('ok') else 'FAIL'}",
        f"Pack: {report.get('pack', '')} {report.get('version', '')}",
    ]
    for item in report.get("artifacts", []):
        lines.append(
            f"- {item['kind']}: {item['page_count']} pages · {item['sha256']} · {item['path']}"
        )
    lines.extend(f"WARNING: {message}" for message in report.get("warnings", []))
    lines.extend(f"ERROR: {message}" for message in report.get("errors", []))
    return "\n".join(lines)


def main() -> int:
    root = find_project_root()
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("build", "audit", "status"):
        child = subparsers.add_parser(command)
        child.add_argument("application", help="application ID or manifest path")
        child.add_argument("--registry", type=Path, default=root / "meta" / "golden_packs.yaml")
        child.add_argument("--json", action="store_true")
        if command == "build":
            child.add_argument("--output-dir", type=Path)
            child.add_argument("--candidate-name", default="")
    args = parser.parse_args()
    try:
        manifest_path = resolve_application(root, args.application)
        if args.command == "build":
            output_dir = args.output_dir
            if output_dir and not output_dir.is_absolute():
                output_dir = root / output_dir
            report = build_matrix(
                root,
                manifest_path,
                registry_path=args.registry,
                output_dir=output_dir,
                name=args.candidate_name,
            )
        else:
            manifest = load_yaml(manifest_path, "application manifest")
            report = audit_matrix_data(root, manifest, args.registry)
            if args.command == "status":
                report = {
                    **report,
                    "stage": manifest.get("stage"),
                    "company": manifest.get("target", {}).get("company"),
                    "role": manifest.get("target", {}).get("title"),
                }
        print(json.dumps(report, indent=2) if args.json else render_report(report))
        return 0 if report.get("ok") else 1
    except GoldenIntegrityError as exc:
        print(str(exc), file=sys.stderr)
        print("Escalate to Deep Maintenance; do not rebuild or replace the approved Pack.", file=sys.stderr)
        return 3
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
