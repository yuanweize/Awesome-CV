from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from engine_adapter import result_json, validate_application_text


class ValidateApplicationTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        stored = self.session.storage.get("career/master_cv.yaml")
        if not stored:
            yield self.create_text_message(result_json(False, error="Career memory is not initialized"))
            return
        errors = validate_application_text(
            stored.decode("utf-8"),
            str(tool_parameters.get("application_yaml", "")),
            str(tool_parameters.get("job_description", "")),
            bool(tool_parameters.get("strict", True)),
        )
        if not errors:
            self.session.storage.set(
                "career/current_application.yaml",
                str(tool_parameters.get("application_yaml", "")).encode("utf-8"),
            )
        yield self.create_json_message({"ok": not errors, "errors": errors})
