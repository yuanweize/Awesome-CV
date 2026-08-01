from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "integrations" / "dify" / "plugin"
SKILL_SCRIPTS = ROOT / "skills" / "evidence-first-cv" / "scripts"
if str(PLUGIN) not in sys.path:
    sys.path.insert(0, str(PLUGIN))
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

from engine_adapter import (  # noqa: E402
    context_from_memory,
    memory_summary,
    new_application_text,
    parse_master,
    storage_yaml,
    validate_application_text,
)
from package_dify_plugin import inspect_package  # noqa: E402


class DifyIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.master_text = (ROOT / "templates" / "master_cv.yaml.example").read_text(encoding="utf-8")

    def test_vendored_engine_matches_skill_scripts(self) -> None:
        for name in ("validate_master_cv.py", "generate_ai_context.py", "application_manifest.py"):
            self.assertEqual(
                (SKILL_SCRIPTS / name).read_bytes(),
                (PLUGIN / "engine" / name).read_bytes(),
                f"Dify engine copy drifted: {name}",
            )

    def test_plugin_manifest_references_existing_provider(self) -> None:
        manifest = yaml.safe_load((PLUGIN / "manifest.yaml").read_text(encoding="utf-8"))
        self.assertEqual("plugin", manifest["type"])
        providers = manifest["plugins"]["tools"]
        self.assertTrue(providers)
        for provider in providers:
            self.assertTrue((PLUGIN / provider).is_file())

    def test_package_inspector_rejects_local_virtual_environment(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / "example.difypkg"
            with zipfile.ZipFile(package, "w") as archive:
                for required in ("manifest.yaml", "main.py", "pyproject.toml", "uv.lock"):
                    archive.writestr(required, "example")
                archive.writestr(".venv/bin/python", "local")
            errors = inspect_package(package)
        self.assertTrue(any("forbidden local path" in error for error in errors))

    def test_memory_validation_and_context_remain_private(self) -> None:
        master = parse_master(self.master_text)
        summary = memory_summary(master)
        self.assertGreater(summary["eligible_claims"], 0)
        context = context_from_memory(
            self.master_text,
            "Troubleshoot Linux services with systemd and Python.",
            "systems",
            5,
        )
        self.assertIn("experience.northstar-linux-support", context)
        self.assertIn("- Market readiness: credible", context)
        self.assertIn("Personal infrastructure is not enterprise production experience", context)
        self.assertNotIn("alex@example.org", context)
        self.assertNotIn("private:employment-reference", context)

    def test_dify_storage_redacts_contact_by_default(self) -> None:
        master = parse_master(self.master_text)
        redacted = storage_yaml(master)
        self.assertNotIn("alex@example.org", redacted)
        self.assertNotIn('phone: "insert locally"', redacted)
        self.assertIn("redacted@example.org", redacted)
        self.assertIn("alex@example.org", storage_yaml(master, store_contact=True))

    def test_portable_application_uses_same_strict_validator(self) -> None:
        jd = "Troubleshoot Linux services with systemd."
        application = {
            "schema_version": "1.0",
            "application_id": "example-systems",
            "stage": "drafted",
            "created_at": "2026-07-31",
            "updated_at": "2026-07-31",
            "target": {
                "company": "Example Corp",
                "title": "Systems Engineer",
                "role_family": "systems",
                "profile": "example-systems",
            },
            "job_description": {
                "path": "meta/applications/example-systems/jd.md",
                "sha256": hashlib.sha256(jd.encode("utf-8")).hexdigest(),
                "source_url": "",
            },
            "decision": {
                "recommendation": "apply",
                "reason": "Direct Linux evidence.",
                "must_have_gaps": 0,
                "user_confirmed": True,
                "confirmed_at": "2026-07-31",
            },
            "questions": [],
            "requirements": [
                {
                    "id": "req.linux",
                    "text": "Troubleshoot Linux services",
                    "priority": "must",
                    "match": "direct",
                    "claim_ids": ["experience.northstar-linux-support"],
                }
            ],
            "selected_claims": ["experience.northstar-linux-support"],
            "final_bullets": [
                {
                    "id": "bullet.linux",
                    "section": "experience",
                    "text": "Investigated Linux service failures and documented reproduction steps.",
                    "claim_ids": ["experience.northstar-linux-support"],
                }
            ],
            "artifacts": {},
            "quality": {},
        }
        errors = validate_application_text(
            self.master_text,
            yaml.safe_dump(application, sort_keys=False),
            jd,
            strict=True,
        )
        self.assertEqual([], errors)

        application["requirements"][0]["claim_ids"] = ["missing.claim"]
        errors = validate_application_text(
            self.master_text,
            yaml.safe_dump(application, sort_keys=False),
            jd,
            strict=True,
        )
        self.assertTrue(any("not present in selected_claims" in error for error in errors))

    def test_dify_starts_hash_bound_application_manifest(self) -> None:
        jd = "Operate and troubleshoot Linux services."
        rendered = new_application_text(
            self.master_text,
            "Example Corp",
            "Systems Engineer",
            "systems",
            jd,
            "example-systems",
        )
        manifest = yaml.safe_load(rendered)
        self.assertEqual("example-systems", manifest["application_id"])
        self.assertEqual(
            hashlib.sha256(jd.encode("utf-8")).hexdigest(),
            manifest["job_description"]["sha256"],
        )
        self.assertEqual("meta/applications/example-systems/jd.md", manifest["job_description"]["path"])


if __name__ == "__main__":
    unittest.main()
