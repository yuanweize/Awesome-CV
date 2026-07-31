from collections.abc import Generator
from typing import Any

import yaml

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from engine_adapter import memory_summary, parse_master


class CareerMemoryStatusTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        stored = self.session.storage.get("career/master_cv.yaml")
        if not stored:
            yield self.create_json_message({"ok": True, "initialized": False})
            return
        try:
            data = parse_master(stored.decode("utf-8"))
            result = {"ok": True, "initialized": True, **memory_summary(data)}
            current = self.session.storage.get("career/current_application.yaml")
            if current:
                application = yaml.safe_load(current.decode("utf-8"))
                if isinstance(application, dict):
                    result["current_application"] = {
                        "id": application.get("application_id", ""),
                        "stage": application.get("stage", ""),
                    }
            yield self.create_json_message(result)
        except (UnicodeDecodeError, ValueError, yaml.YAMLError) as exc:
            yield self.create_json_message({"ok": False, "initialized": True, "error": str(exc)})
