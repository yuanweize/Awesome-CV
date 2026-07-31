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
    def test_safe_system_inventory_redacts_hostname(self) -> None:
        with (
            mock.patch.object(collector.socket, "gethostname", return_value="private-host"),
            mock.patch.object(collector, "run", return_value=""),
        ):
            _, content = collector.collect_system(include_sensitive=False)
        self.assertIn("[redacted in safe mode]", content)
        self.assertNotIn("private-host", content)

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

        self.assertIn("private-app:latest", safe)
        self.assertNotIn("registry.internal", safe)
        self.assertNotIn("customer-container", safe)
        self.assertNotIn("8443", safe)
        self.assertNotIn("customer-database", safe)
        self.assertNotIn("customer-network", safe)
        self.assertIn("customer-container", full)
        self.assertIn("8443", full)


if __name__ == "__main__":
    unittest.main()
