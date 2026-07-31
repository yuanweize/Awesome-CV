from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from engine_adapter import new_application_text


class StartApplicationTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        stored = self.session.storage.get("career/master_cv.yaml")
        if not stored:
            yield self.create_json_message({"ok": False, "error": "Career memory is not initialized"})
            return
        try:
            manifest = new_application_text(
                stored.decode("utf-8"),
                str(tool_parameters.get("company", "")),
                str(tool_parameters.get("title", "")),
                str(tool_parameters.get("role_family", "")),
                str(tool_parameters.get("job_description", "")),
                str(tool_parameters.get("application_id", "")),
            )
            self.session.storage.set("career/current_application.yaml", manifest.encode("utf-8"))
            yield self.create_variable_message("application_yaml", manifest)
            yield self.create_text_message(manifest)
        except (UnicodeDecodeError, ValueError) as exc:
            yield self.create_json_message({"ok": False, "error": str(exc)})
