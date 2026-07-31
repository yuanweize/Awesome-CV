from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parent.parent
COLLECTOR_PATH = ROOT / "tools" / "tech-stack-collector" / "collector.py"
SPEC = importlib.util.spec_from_file_location("tech_stack_collector", COLLECTOR_PATH)
assert SPEC and SPEC.loader
collector = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(collector)


class CollectorPrivacyTests(unittest.TestCase):
    def test_version_filter_rejects_errors_and_keeps_real_version(self) -> None:
        output = "WARNING: deprecated flag\npermission denied\nClient Version: v1.33.9"
        self.assertEqual("Client Version: v1.33.9", collector.first_usable_line(output))
        self.assertEqual(
            "",
            collector.first_usable_line(
                'Traceback: failed\n  File "/usr/local/bin/tool", line 5, in <module>\nPermission denied'
            ),
        )

    def test_safe_system_inventory_redacts_hostname(self) -> None:
        with (
            mock.patch.object(collector.socket, "gethostname", return_value="private-host"),
            mock.patch.object(collector, "run", return_value=""),
        ):
            _, content = collector.collect_system(include_sensitive=False)
        self.assertIn("[redacted in safe mode]", content)
        self.assertNotIn("private-host", content)
        self.assertNotIn("Kernel", content)
        self.assertNotIn("Disk", content)
        self.assertNotIn("Uptime", content)

    def test_safe_docker_inventory_hides_topology_and_registry(self) -> None:
        def fake_run(command: str, timeout: int | None = None) -> str:
            del timeout
            if "images --format" in command:
                return "registry.internal/team/private-app:latest\t120MB"
            if " ps " in command:
                return "customer-container\tprivate-app\t0.0.0.0:8443->443/tcp\tUp"
            if "volume ls" in command:
                return "customer-database"
            if "network ls" in command:
                return "customer-network\tbridge"
            return ""

        with (
            mock.patch.object(collector, "has", side_effect=lambda command: command == "docker"),
            mock.patch.object(collector, "run", side_effect=fake_run),
        ):
            _, safe = collector.collect_docker(safe=True)
            _, full = collector.collect_docker(safe=False)

        self.assertIn("Docker", safe)
        self.assertNotIn("private-app", safe)
        self.assertNotIn("registry.internal", safe)
        self.assertNotIn("120MB", safe)
        self.assertNotIn("customer-container", safe)
        self.assertNotIn("8443", safe)
        self.assertNotIn("customer-database", safe)
        self.assertNotIn("customer-network", safe)
        self.assertIn("customer-container", full)
        self.assertIn("8443", full)

    def test_safe_package_inventory_omits_package_names(self) -> None:
        def fake_run(command: str, timeout: int | None = None) -> str:
            del timeout
            if "pip3 list --format" in command:
                return "private-customer-sdk 1.0\nrequests 2.0"
            if "pip3 list" in command and "wc -l" in command:
                return "2"
            return ""

        with (
            mock.patch.object(collector, "has", return_value=False),
            mock.patch.object(collector, "run", side_effect=fake_run),
        ):
            _, safe = collector.collect_package_managers(include_details=False)
            _, full = collector.collect_package_managers(include_details=True)

        self.assertIn("2 packages", safe)
        self.assertNotIn("private-customer-sdk", safe)
        self.assertIn("private-customer-sdk", full)

    def test_tag_extraction_uses_only_first_table_column(self) -> None:
        tags = collector.TagStore()
        sections = {
            "Databases": collector.md_table(
                ["Database", "Version", "Status"],
                [["SQLite3", "3.51", "installed"]],
            )
        }
        collector._extract_tags_from_sections(tags, sections)
        self.assertIn("SQLite", tags.flat_tags())
        self.assertNotIn("installed", tags.flat_tags())

    def test_command_output_strips_terminal_escape_codes(self) -> None:
        completed = mock.Mock(stdout="\x1b[1mtool 1.0\x1b[0m\n")
        with mock.patch.object(collector.subprocess, "run", return_value=completed):
            self.assertEqual("tool 1.0", collector.run("tool --version"))

    def test_safe_service_inventory_omits_custom_unit_names(self) -> None:
        raw = "postgresql.service\ncustomer-secret-worker.service\nssh.service"
        with mock.patch.object(collector, "run", return_value=raw):
            _, safe = collector.collect_services(safe=True)
            _, full = collector.collect_services(safe=False)

        self.assertIn("PostgreSQL", safe)
        self.assertNotIn("customer-secret-worker", safe)
        self.assertIn("customer-secret-worker", full)


if __name__ == "__main__":
    unittest.main()
