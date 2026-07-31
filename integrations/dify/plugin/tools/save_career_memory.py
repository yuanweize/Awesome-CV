from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from engine_adapter import memory_summary, parse_master, storage_yaml


class SaveCareerMemoryTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        master_yaml = str(tool_parameters.get("master_yaml", ""))
        store_contact = bool(tool_parameters.get("store_contact", False))
        try:
            data = parse_master(master_yaml)
            serialized = storage_yaml(data, store_contact=store_contact)
            self.session.storage.set("career/master_cv.yaml", serialized.encode("utf-8"))
            yield self.create_json_message(
                {"ok": True, "contact_stored": store_contact, **memory_summary(data)}
            )
        except ValueError as exc:
            yield self.create_json_message({"ok": False, "error": str(exc)})
