#!/usr/bin/env python3
"""Create and verify an application-scoped derivative, never edit a Golden Pack."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from application_delivery_matrix import (find_project_root, selected_pack, load_yaml,
    resolve_application, file_sha256, pdf_page_count, save_yaml, qpdf_check)
from golden_pack_audit import source_fingerprint
from presentation_model import derive_model, fingerprint, render_pdf, render_tex, audit_pdf, CHANGE_FIELDS


def selected_claim_ids(model):
    keys = set(model['summary'] + model['skills'])
    for entry in model['entry_catalog']:
        if entry['id'] in model['entries']:
            keys.update(entry.get('metadata_claims', []))
            keys.update(model.get('bullets', {}).get(entry['id'], entry['bullets']))
    return sorted({cid for key in keys for cid in model['catalog'][key]['claim_ids']})


def safe_path(root, raw, scope):
    path = root / raw
    if path.is_absolute() and not path.is_relative_to(root):
        raise ValueError("variant path escapes repository")
    for part in [path, *path.parents]:
        if part == root.parent:
            break
        if part.is_symlink():
            raise ValueError("symbolic links are forbidden for variant paths")
    path = path.resolve()
    if not path.is_relative_to((root / scope).resolve()):
        raise ValueError("variant path outside application scope")
    return path


def parent_model(root, pack):
    snapshot = safe_path(root, pack["source_snapshot"], "workspace/golden-packs")
    profile = safe_path(root, pack["source_profile"], "workspace/profiles")
    if source_fingerprint(snapshot) != pack["source_sha256"] or source_fingerprint(profile) != pack["source_sha256"]:
        raise ValueError("Golden source fingerprint mismatch")
    model_file = snapshot / "presentation.yaml"
    if not model_file.is_file():
        raise ValueError("legacy Pack has no reviewed presentation catalog; reuse unchanged or propose a new version")
    return load_yaml(model_file, "presentation catalog")


def verify_variant(root, manifest, pack, golden):
    binding = manifest.get("application_variant")
    if not binding:
        return golden["cv"]
    if str(manifest.get("schema_version")) != "1.5":
        raise ValueError("application variants require manifest schema 1.5")
    app_id = manifest["application_id"]
    record_path = safe_path(root, binding["record"], f"workspace/application-variants/{app_id}")
    if file_sha256(record_path) != binding["record_sha256"]:
        raise ValueError("variant record hash mismatch")
    record = load_yaml(record_path, "variant record")
    if record["parent"] != {"pack_id": manifest["golden_pack"]["selected_pack"],
                            "version": pack["version"], "golden_cv_sha256": golden["cv"]["sha256"],
                            "source_sha256": pack["source_sha256"]}:
        raise ValueError("variant immutable parent reference mismatch")
    if binding.get('golden_cv_sha256') != golden['cv']['sha256']:
        raise ValueError('variant binding parent hash mismatch')
    if record.get('application_id') != app_id:
        raise ValueError('variant belongs to another application')
    if record.get('mode') == 'legacy-title':
        from legacy_title_variant import verify
        return verify(root, manifest, pack, golden, record, record_path)
    if record.get("change_whitelist") != sorted(CHANGE_FIELDS):
        raise ValueError("variant change whitelist mismatch")
    parent = parent_model(root, pack)
    master = load_yaml(root / "meta/master_cv.yaml", "master")
    derived, diff = derive_model(parent, record["changes"], master)
    if record['selected_claim_ids'] != selected_claim_ids(derived):
        raise ValueError('variant selected claim mapping mismatch')
    if record["field_diff"] != diff or record["source_fingerprint"] != fingerprint(derived):
        raise ValueError("variant source/diff does not reproduce")
    model = load_yaml(record_path.parent / "presentation.yaml", "derived presentation")
    if model != derived:
        raise ValueError("variant model differs from allowed derivation")
    pdf = safe_path(root, record["artifact"]["path"], f"workspace/application-variants/{app_id}")
    if pdf.with_suffix(".tex").read_text() != render_tex(derived):
        raise ValueError("variant rendered source mismatch")
    digest = file_sha256(pdf)
    if digest != record["artifact"]["variant_cv_sha256"] or digest != binding["variant_cv_sha256"]:
        raise ValueError("variant artifact hash mismatch")
    if record["artifact"]["page_count"] != pdf_page_count(pdf):
        raise ValueError("variant page count mismatch")
    if diff and digest == golden["cv"]["sha256"]:
        raise ValueError("changed variant cannot impersonate the Golden binary")
    qpdf_check(pdf)
    return {"path": pdf, "sha256": digest, "page_count": record["artifact"]["page_count"]}


def build_variant(root, manifest_path, changes_path):
    root = root.resolve()
    manifest = load_yaml(manifest_path, "manifest")
    if manifest.get("stage") in {"sent", "closed"}:
        raise ValueError("cannot modify a submitted application")
    pack_id, pack, golden = selected_pack(root, manifest, root / "meta/golden_packs.yaml")
    changes = load_yaml(changes_path, "variant request")
    if not (root / pack['source_snapshot'] / 'presentation.yaml').is_file():
        from legacy_title_variant import build
        return build(root, manifest_path, manifest, pack_id, pack, golden, changes)
    parent = parent_model(root, pack)
    master = load_yaml(root / "meta/master_cv.yaml", "master")
    derived, diff = derive_model(parent, changes, master)
    if not diff:
        if manifest.get("application_variant"):
            raise ValueError("existing variant cannot be silently replaced by an unchanged request")
        return {"mode": "golden-copy", "golden_cv_sha256": golden["cv"]["sha256"]}
    revision = fingerprint({"parent": pack["source_sha256"], "changes": changes})[:16]
    destination = safe_path(root, f"workspace/application-variants/{manifest['application_id']}/{revision}",
                            "workspace/application-variants")
    if destination.exists():
        expected_record = destination / 'variant.yaml'
        if manifest.get('application_variant', {}).get('record') != expected_record.relative_to(root).as_posix():
            raise ValueError('existing revision is not the manifest-bound variant; review before reuse')
        verify_variant(root, manifest, pack, golden)
        return {"mode": "variant", "record": manifest["application_variant"]["record"]}
    destination.mkdir(parents=True)
    save_yaml(destination / "presentation.yaml", derived)
    pdf = render_pdf(root, derived, destination / "CV.pdf")
    qpdf_check(pdf)
    pages = pdf_page_count(pdf)
    if pages > 2:
        raise ValueError("variant exceeds two-page CV contract; revise selection")
    audit = audit_pdf(derived, pdf)
    if not audit['ok']:
        raise ValueError('; '.join(audit['errors']))
    record = {"schema_version": "1.0", "application_id": manifest["application_id"],
              "parent": {"pack_id": pack_id, "version": pack["version"],
                         "golden_cv_sha256": golden["cv"]["sha256"], "source_sha256": pack["source_sha256"]},
              "requested_target_title": manifest["target"]["title"],
              "rendered_headline": derived["headline"], "changes": changes,
              "change_whitelist": sorted(CHANGE_FIELDS), "field_diff": diff,
              "source_fingerprint": fingerprint(derived),
              "selected_claim_ids": selected_claim_ids(derived),
              "artifact": {"path": pdf.relative_to(root).as_posix(),
                           "variant_cv_sha256": file_sha256(pdf), "page_count": pages},
              "quality": {"ats": "passed deterministic text checks", "visual": "pending", "first_screen": "pending editorial review"}}
    record_path = destination / "variant.yaml"
    save_yaml(record_path, record)
    manifest["schema_version"] = "1.5"
    manifest["application_variant"] = {"record": record_path.relative_to(root).as_posix(),
        "record_sha256": file_sha256(record_path), "golden_cv_sha256": golden["cv"]["sha256"],
        "variant_cv_sha256": file_sha256(pdf)}
    manifest["stage"] = "drafted"
    manifest["quality"] = {key: "pending" for key in ("claim_audit", "ats_text_check", "visual_check", "privacy_check")}
    verify_variant(root, manifest, pack, golden)
    save_yaml(manifest_path, manifest)
    return {"mode": "variant", **manifest["application_variant"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("application")
    parser.add_argument("changes", type=Path)
    args = parser.parse_args()
    root = find_project_root()
    try:
        print(json.dumps(build_variant(root, resolve_application(root, args.application), args.changes), indent=2))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(f"VARIANT REJECTED: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
