from __future__ import annotations

import copy
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "evidence-first-cv" / "scripts"
ADDED_SCRIPTS_PATH = str(SCRIPTS) not in sys.path
if ADDED_SCRIPTS_PATH:
    sys.path.insert(0, str(SCRIPTS))

import application_delivery_matrix as matrix  # noqa: E402

if ADDED_SCRIPTS_PATH:
    sys.path.remove(str(SCRIPTS))


class FastApplicationTests(unittest.TestCase):
    def make_runtime(self, root: Path, selected: str = "research") -> tuple[Path, dict[str, Path]]:
        (root / "templates").mkdir(parents=True)
        (root / "templates" / "master_cv.yaml.example").write_text("schema_version: '3.10'\n")
        (root / "meta").mkdir()
        (root / "meta" / "master_cv.yaml").write_text(
            yaml.safe_dump({"personal_information": {"full_name": "Alex Example"}}),
            encoding="utf-8",
        )
        golden_dir = root / "output" / "pdf" / "golden-packs" / "v1.0"
        golden_dir.mkdir(parents=True)
        packs: dict[str, dict[str, object]] = {}
        selected_paths: dict[str, Path] = {}
        for pack_id in ("platform", "research", "field"):
            artifacts: dict[str, dict[str, object]] = {}
            for kind, pages in (("cv", 2), ("portfolio", 3), ("combined", 5)):
                path = golden_dir / f"{pack_id}-{kind}.pdf"
                path.write_bytes(f"%PDF-{pack_id}-{kind}".encode())
                artifacts[kind] = {
                    "path": path.relative_to(root).as_posix(),
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "page_count": pages,
                }
                if pack_id == selected:
                    selected_paths[kind] = path
            packs[pack_id] = {
                "version": "v1.0",
                "status": "approved",
                "approved_at": "2026-09-21",
                "role_families": [pack_id],
                "artifacts": artifacts,
            }
        registry = root / "meta" / "golden_packs.yaml"
        registry.write_text(
            yaml.safe_dump({"schema_version": "1.0", "packs": packs}, sort_keys=False),
            encoding="utf-8",
        )

        app_dir = root / "meta" / "applications" / "20260921-example-role"
        app_dir.mkdir(parents=True)
        cover = root / "workspace" / "build" / "Alex_Example_Cover_Letter.pdf"
        cover.parent.mkdir(parents=True)
        cover.write_bytes(b"%PDF-cover-letter")
        selected_pack = packs[selected]
        manifest = {
            "schema_version": "1.4",
            "application_id": "20260921-example-role",
            "stage": "drafted",
            "target": {"company": "Example", "title": "Systems Engineer"},
            "golden_pack": {
                "selected_pack": selected,
                "version": "v1.0",
                "cv_sha256": selected_pack["artifacts"]["cv"]["sha256"],
            },
            "submission_recommendation": {
                "cv": "",
                "portfolio": "",
                "cover_letter": "",
                "recommended_upload": "",
                "single_recruiter_attachment": "",
            },
            "artifacts": {
                "cover_letter_pdf": cover.relative_to(root).as_posix(),
                "cover_letter_sha256": hashlib.sha256(cover.read_bytes()).hexdigest(),
                "cover_letter_page_count": 1,
            },
        }
        manifest_path = app_dir / "application.yaml"
        manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
        return manifest_path, selected_paths

    @staticmethod
    def page_count_for(path: Path) -> int:
        name = path.name.lower()
        if "complete_application" in name:
            return 6
        if "cover_letter_portfolio" in name:
            return 4
        if "cv_cover_letter" in name:
            return 3
        if "cv_portfolio" in name or "combined" in name:
            return 5
        if "portfolio" in name:
            return 3
        if "cover_letter" in name:
            return 1
        if "cv" in name:
            return 2
        raise AssertionError(f"unexpected PDF name: {name}")

    def fake_subprocess(self, commands: list[list[str]]):
        def run(command, **_kwargs):
            command = [str(item) for item in command]
            commands.append(command)
            if command[0] == "pdfinfo":
                pages = self.page_count_for(Path(command[1]))
                return subprocess.CompletedProcess(command, 0, f"Pages: {pages}\n", "")
            if command[:2] == ["qpdf", "--check"]:
                return subprocess.CompletedProcess(command, 0, "", "")
            if command[0] == "qpdf" and "--pages" in command:
                destination = Path(command[-1])
                destination.write_bytes(("%PDF-merged:" + "|".join(command)).encode())
                return subprocess.CompletedProcess(command, 0, "", "")
            raise AssertionError(f"Fast Path invoked an unexpected command: {command}")

        return run

    def test_build_reuses_n_pack_artifacts_and_creates_canonical_matrix(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest_path, golden_paths = self.make_runtime(root, selected="research")
            before = {kind: path.read_bytes() for kind, path in golden_paths.items()}
            commands: list[list[str]] = []
            with mock.patch.object(matrix.subprocess, "run", side_effect=self.fake_subprocess(commands)), mock.patch.object(
                matrix, "extract_text", return_value=("Example Systems Engineer " + "evidence " * 150, 1)
            ):
                report = matrix.build_matrix(
                    root,
                    manifest_path,
                    registry_path=root / "meta" / "golden_packs.yaml",
                )

            self.assertTrue(report["ok"], report["errors"])
            self.assertEqual("research", report["pack"])
            self.assertEqual(list(matrix.MATRIX_KINDS), [item["kind"] for item in report["artifacts"]])
            self.assertEqual(7, len(report["artifacts"]))
            self.assertTrue(
                all(
                    item["path"].startswith(
                        "output/pdf/applications/20260921-example-role/"
                    )
                    for item in report["artifacts"]
                )
            )
            self.assertEqual(before, {kind: path.read_bytes() for kind, path in golden_paths.items()})
            self.assertEqual({"qpdf", "pdfinfo"}, {command[0] for command in commands})
            self.assertFalse(any("make" in command or "privacy" in command for command in commands))
            complete_merge = next(
                command
                for command in commands
                if command[0] == "qpdf"
                and command[-1].endswith(".Alex_Example_Complete_Application.tmp.pdf")
            )
            complete_inputs = [
                Path(complete_merge[index]).name
                for index in range(
                    complete_merge.index("--pages") + 1,
                    complete_merge.index("--"),
                    2,
                )
            ]
            self.assertEqual(
                [
                    "Alex_Example_Cover_Letter.pdf",
                    "Alex_Example_CV.pdf",
                    "Alex_Example_Portfolio.pdf",
                ],
                complete_inputs,
            )

            saved = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(
                saved["golden_pack"]["portfolio_sha256"],
                hashlib.sha256(golden_paths["portfolio"].read_bytes()).hexdigest(),
            )
            self.assertEqual(
                ["cover_letter", "cv", "portfolio"],
                saved["artifacts"]["delivery_matrix"][-1]["contents"],
            )
            self.assertEqual("", saved["artifacts"].get("portal_note_path", ""))
            readme = root / report["readme"]
            text = readme.read_text(encoding="utf-8")
            self.assertIn("Alex_Example_Complete_Application.pdf", text)
            self.assertIn("Cover Letter -> CV -> Portfolio", text)

    def test_hash_mismatch_escalates_without_building_or_mutating_golden(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest_path, golden_paths = self.make_runtime(root)
            golden_paths["cv"].write_bytes(b"changed-after-approval")
            changed = golden_paths["cv"].read_bytes()
            commands: list[list[str]] = []
            with mock.patch.object(matrix.subprocess, "run", side_effect=self.fake_subprocess(commands)):
                with self.assertRaisesRegex(matrix.GoldenIntegrityError, "GOLDEN INTEGRITY FAILURE"):
                    matrix.build_matrix(
                        root,
                        manifest_path,
                        registry_path=root / "meta" / "golden_packs.yaml",
                    )
            self.assertEqual(changed, golden_paths["cv"].read_bytes())
            self.assertFalse(
                (
                    root
                    / "output"
                    / "pdf"
                    / "applications"
                    / "20260921-example-role"
                ).exists()
            )

    def test_optional_portal_note_is_hash_bound_without_changing_the_matrix(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest_path, _golden_paths = self.make_runtime(root)
            note = manifest_path.parent / "portal_note.md"
            note.write_text("A short, role-specific introduction.", encoding="utf-8")
            manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
            manifest["artifacts"]["portal_note_path"] = note.relative_to(root).as_posix()
            manifest_path.write_text(
                yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8"
            )
            commands: list[list[str]] = []
            with mock.patch.object(
                matrix.subprocess,
                "run",
                side_effect=self.fake_subprocess(commands),
            ), mock.patch.object(
                matrix,
                "extract_text",
                return_value=("Example Systems Engineer " + "evidence " * 150, 1),
            ):
                report = matrix.build_matrix(
                    root,
                    manifest_path,
                    registry_path=root / "meta" / "golden_packs.yaml",
                )

            self.assertTrue(report["ok"], report["errors"])
            saved = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(
                hashlib.sha256(note.read_bytes()).hexdigest(),
                saved["artifacts"]["portal_note_sha256"],
            )
            self.assertEqual(7, len(saved["artifacts"]["delivery_matrix"]))
            self.assertIn(
                "paste portal_note.md",
                saved["submission_recommendation"]["cover_letter"],
            )


if __name__ == "__main__":
    unittest.main()
