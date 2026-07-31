from typing import Any

from dify_plugin import ToolProvider


class EvidenceFirstCvProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        return None
