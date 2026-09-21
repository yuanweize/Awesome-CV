from __future__ import annotations

import copy
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "evidence-first-cv" / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from application_manifest import new_manifest, validate_manifest  # noqa: E402
from cover_letter_audit import audit_text  # noqa: E402
from golden_pack_audit import audit_registry, file_sha256, source_fingerprint  # noqa: E402


class GoldenPackGovernanceTests(unittest.TestCase):
    def make_registry(
        self,
        root: Path,
        *,
        status: str = "freeze-candidate",
        pack_ids: tuple[str, ...] = ("platform", "research", "field"),
    ) -> Path:
        output = root / "output" / "pdf" / "golden-packs" / "v2.0"
        output.mkdir(parents=True)
        packs: dict[str, dict[str, object]] = {}
        for pack_id in pack_ids:
            snapshot = root / "workspace" / "golden-packs" / "v2.0" / pack_id
            profile = root / "workspace" / "profiles" / f"golden-{pack_id}-v2.0"
            snapshot.mkdir(parents=True)
            profile.mkdir(parents=True)
            (snapshot / "config.tex").write_text(f"{pack_id}\n", encoding="utf-8")
            (profile / "config.tex").write_text(f"{pack_id}\n", encoding="utf-8")
            artifacts: dict[str, dict[str, object]] = {}
            for kind, pages in (("cv", 2), ("portfolio", 3), ("combined", 5)):
                pdf = output / f"{pack_id}-{kind}.pdf"
                pdf.write_bytes(f"{pack_id}-{kind}".encode())
                artifacts[kind] = {
                    "path": pdf.relative_to(root).as_posix(),
                    "sha256": file_sha256(pdf),
                    "page_count": pages,
                }
            packs[pack_id] = {
                "version": "v2.0",
                "status": status,
                "approved_at": "2026-09-11" if status == "approved" else "",
                "role_families": [pack_id],
                "source_profile": profile.relative_to(root).as_posix(),
                "source_snapshot": snapshot.relative_to(root).as_posix(),
                "source_sha256": source_fingerprint(snapshot),
                "artifacts": artifacts,
            }
        registry = root / "meta" / "golden_packs.yaml"
        registry.parent.mkdir(parents=True)
        registry.write_text(
            yaml.safe_dump({"schema_version": "1.0", "packs": packs}, sort_keys=False),
            encoding="utf-8",
        )
        return registry

    def test_public_registry_templates_are_identical(self) -> None:
        self.assertEqual(
            (ROOT / "templates" / "golden_packs.yaml.example").read_bytes(),
            (ROOT / "skills" / "evidence-first-cv" / "assets" / "golden_packs.yaml.example").read_bytes(),
        )

    def test_registry_audit_verifies_sources_hashes_and_pages(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = self.make_registry(root)
            with mock.patch(
                "golden_pack_audit.pdf_page_count",
                side_effect=lambda path: 2 if path.name.endswith("-cv.pdf") else (3 if path.name.endswith("-portfolio.pdf") else 5),
            ):
                report = audit_registry(root, registry)
            self.assertTrue(report["ok"], report["errors"])
            self.assertEqual([], report["warnings"])
            self.assertEqual({"platform", "research", "field"}, set(report["packs"]))

    def test_approved_pack_rejects_source_profile_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = self.make_registry(root, status="approved")
            profile = root / "workspace" / "profiles" / "golden-platform-v2.0" / "config.tex"
            profile.write_text("changed\n", encoding="utf-8")
            with mock.patch("golden_pack_audit.pdf_page_count", return_value=2):
                report = audit_registry(root, registry)
            self.assertFalse(report["ok"])
            self.assertTrue(any("source_profile differs" in item for item in report["errors"]))

    def test_approved_pack_rejects_artifact_hash_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = self.make_registry(root, status="approved")
            cv = root / "output" / "pdf" / "golden-packs" / "v2.0" / "platform-cv.pdf"
            cv.write_bytes(b"changed")
            with mock.patch(
                "golden_pack_audit.pdf_page_count",
                side_effect=lambda path: 2 if path.name.endswith("-cv.pdf") else (3 if path.name.endswith("-portfolio.pdf") else 5),
            ):
                report = audit_registry(root, registry)
            self.assertFalse(report["ok"])
            self.assertTrue(any("sha256 does not match" in item for item in report["errors"]))

    def test_application_manifest_binds_selected_pack_version_and_cv_hash(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry_path = self.make_registry(root)
            registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
            jd = root / "meta" / "applications" / "example" / "jd.md"
            jd.parent.mkdir(parents=True)
            jd.write_text("Systems Engineer\n", encoding="utf-8")
            data = new_manifest(
                "20260911-example-systems-engineer",
                "Example",
                "Systems Engineer",
                "systems",
                jd.relative_to(root).as_posix(),
                hashlib.sha256(jd.read_bytes()).hexdigest(),
                "example-systems-engineer",
            )
            cv_hash = registry["packs"]["research"]["artifacts"]["cv"]["sha256"]
            data["golden_pack"] = {
                "selected_pack": "research",
                "version": "v2.0",
                "cv_sha256": cv_hash,
            }
            errors = validate_manifest(data, ROOT / "templates" / "master_cv.yaml.example", root)
            self.assertEqual([], errors)

            changed = copy.deepcopy(data)
            changed["golden_pack"]["cv_sha256"] = "0" * 64
            errors = validate_manifest(changed, ROOT / "templates" / "master_cv.yaml.example", root)
            self.assertTrue(any("does not match the registry" in item for item in errors))

            historical = copy.deepcopy(data)
            historical["schema_version"] = "1.3"
            historical.pop("golden_pack")
            self.assertEqual(
                [],
                validate_manifest(
                    historical,
                    ROOT / "templates" / "master_cv.yaml.example",
                    root,
                ),
            )

    def test_application_workflow_does_not_mutate_approved_pack(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry_path = self.make_registry(root, status="approved")
            registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
            pack = registry["packs"]["platform"]
            protected_paths = [
                root / pack["source_profile"],
                root / pack["source_snapshot"],
                *(root / item["path"] for item in pack["artifacts"].values()),
            ]
            before = {
                path: (
                    sorted(
                        (child.relative_to(path).as_posix(), child.read_bytes())
                        for child in path.rglob("*")
                        if child.is_file()
                    )
                    if path.is_dir()
                    else path.read_bytes()
                )
                for path in protected_paths
            }

            jd = root / "meta" / "applications" / "example" / "jd.md"
            jd.parent.mkdir(parents=True)
            jd.write_text("Platform Engineer\n", encoding="utf-8")
            data = new_manifest(
                "20260913-example-platform-engineer",
                "Example",
                "Platform Engineer",
                "systems",
                jd.relative_to(root).as_posix(),
                hashlib.sha256(jd.read_bytes()).hexdigest(),
                "example-platform-engineer",
            )
            data["golden_pack"] = {
                "selected_pack": "platform",
                "version": pack["version"],
                "cv_sha256": pack["artifacts"]["cv"]["sha256"],
            }
            self.assertEqual(
                [],
                validate_manifest(
                    data,
                    ROOT / "templates" / "master_cv.yaml.example",
                    root,
                ),
            )
            after = {
                path: (
                    sorted(
                        (child.relative_to(path).as_posix(), child.read_bytes())
                        for child in path.rglob("*")
                        if child.is_file()
                    )
                    if path.is_dir()
                    else path.read_bytes()
                )
                for path in protected_paths
            }
            self.assertEqual(before, after)

    def test_new_manifest_records_submission_metadata_without_breaking_old_14(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            jd = root / "meta" / "applications" / "example" / "jd.md"
            jd.parent.mkdir(parents=True)
            jd.write_text("Systems Engineer\n", encoding="utf-8")
            data = new_manifest(
                "20260913-example-systems-engineer",
                "Example",
                "Systems Engineer",
                "systems",
                jd.relative_to(root).as_posix(),
                hashlib.sha256(jd.read_bytes()).hexdigest(),
                "example-systems-engineer",
            )
            self.assertEqual(
                {
                    "submitted_at": "",
                    "channel": "",
                    "delivered_artifacts": [],
                    "reference": "",
                },
                data["submission"],
            )
            self.assertEqual(
                [],
                validate_manifest(
                    data,
                    ROOT / "templates" / "master_cv.yaml.example",
                    root,
                ),
            )

            historical = copy.deepcopy(data)
            historical.pop("submission")
            historical.pop("submission_recommendation")
            historical["golden_pack"].pop("portfolio_sha256")
            for field in (
                "portfolio_pdf",
                "portfolio_sha256",
                "portfolio_page_count",
                "portal_note_path",
                "portal_note_sha256",
                "delivery_matrix",
            ):
                historical["artifacts"].pop(field)
            self.assertEqual(
                [],
                validate_manifest(
                    historical,
                    ROOT / "templates" / "master_cv.yaml.example",
                    root,
                ),
            )

            invalid = copy.deepcopy(data)
            invalid["submission"]["delivered_artifacts"] = ["cv", "mystery-file"]
            errors = validate_manifest(
                invalid,
                ROOT / "templates" / "master_cv.yaml.example",
                root,
            )
            self.assertTrue(any("unknown values" in item for item in errors))

            sent_without_metadata = copy.deepcopy(data)
            sent_without_metadata["stage"] = "sent"
            errors = validate_manifest(
                sent_without_metadata,
                ROOT / "templates" / "master_cv.yaml.example",
                root,
            )
            self.assertTrue(any("submission.submitted_at" in item for item in errors))
            self.assertTrue(any("submission.channel" in item for item in errors))
            self.assertTrue(any("submission.delivered_artifacts" in item for item in errors))

    def test_registry_rejects_empty_or_unsafe_pack_ids(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = root / "meta" / "golden_packs.yaml"
            registry.parent.mkdir(parents=True)
            registry.write_text(
                yaml.safe_dump({"schema_version": "1.0", "packs": {}}),
                encoding="utf-8",
            )
            report = audit_registry(root, registry)
            self.assertFalse(report["ok"])
            self.assertTrue(any("at least one" in item for item in report["errors"]))

            registry.write_text(
                yaml.safe_dump({"schema_version": "1.0", "packs": {"Bad Pack": {}}}),
                encoding="utf-8",
            )
            report = audit_registry(root, registry)
            self.assertFalse(report["ok"])
            self.assertTrue(any("invalid Golden Pack ID" in item for item in report["errors"]))

    def test_cover_letter_audit_is_advisory_and_flags_cliches(self) -> None:
        text = "I am excited to apply for the role at Example Corp. " + "evidence " * 170
        report = audit_text(text, company="Example Corp", role="Systems Engineer", pages=2)
        self.assertTrue(report["ok"])
        self.assertTrue(any("cliché" in item for item in report["warnings"]))
        self.assertTrue(any("role title is missing" in item for item in report["warnings"]))
        self.assertTrue(any("2 pages" in item for item in report["warnings"]))

    def test_cover_letter_audit_flags_empty_output(self) -> None:
        report = audit_text("", pages=1)
        self.assertTrue(report["ok"])
        self.assertTrue(any("no readable" in item for item in report["warnings"]))


if __name__ == "__main__":
    unittest.main()
