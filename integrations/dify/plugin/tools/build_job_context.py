from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from engine_adapter import context_from_memory, result_json


class BuildJobContextTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        stored = self.session.storage.get("career/master_cv.yaml")
        if not stored:
            yield self.create_text_message(result_json(False, error="Career memory is not initialized"))
            return
        jd = str(tool_parameters.get("job_description", ""))
        role = str(tool_parameters.get("role_family", ""))
        max_claims = int(tool_parameters.get("max_claims", 10))
        max_adjacent = int(tool_parameters.get("max_adjacent", 4))
        try:
            context = context_from_memory(
                stored.decode("utf-8"),
                jd,
                role,
                max(1, min(max_claims, 20)),
                max(0, min(max_adjacent, 6)),
            )
            yield self.create_variable_message("context", context)
            yield self.create_text_message(context)
        except (TypeError, ValueError) as exc:
            yield self.create_text_message(result_json(False, error=str(exc)))
