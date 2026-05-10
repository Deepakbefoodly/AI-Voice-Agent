# src/services/tool_orchestration_service.py

from dataclasses import dataclass
from typing import Any

from fastmcp import Client

from config import MCP_TOOLS_URL

DEFAULT_MCP_TOOLS_URL = MCP_TOOLS_URL

@dataclass(frozen=True)
class ToolOrchestrationResult:
    intent: dict[str, Any]
    external_result: dict[str, Any] | None

    def to_prompt_context(self) -> str:
        lines = [
            "Tool orchestration context:",
            f"- Intent: {self.intent.get('intent')}",
            f"- Intent confidence: {self.intent.get('confidence')}",
        ]

        entities = self.intent.get("entities") or {}
        if entities:
            lines.append(f"- Extracted entities: {entities}")

        if self.external_result is not None:
            lines.append(f"- External API result: {self.external_result}")

        return "\n".join(lines)


def _extract_tool_data(result: Any) -> Any:
    """
    FastMCP versions may expose structured tool results differently.
    This keeps the rest of the app isolated from that detail.
    """
    if hasattr(result, "data"):
        return result.data

    if hasattr(result, "structured_content"):
        return result.structured_content

    if isinstance(result, list) and result:
        first = result[0]

        if hasattr(first, "text"):
            return first.text

        if hasattr(first, "data"):
            return first.data

    return result


async def call_mcp_tool(tool_name: str, arguments: dict[str, Any]) -> Any:
    mcp_url = DEFAULT_MCP_TOOLS_URL

    async with Client(mcp_url) as client:
        result = await client.call_tool(tool_name, arguments)

    return _extract_tool_data(result)


async def orchestrate_tools_for_question(question: str) -> ToolOrchestrationResult:
    intent = await call_mcp_tool(
        "detect_intent",
        {
            "text": question,
        },
    )

    if not isinstance(intent, dict):
        intent = {
            "intent": "unknown",
            "confidence": 0.0,
            "entities": {},
            "requires_external_api": False,
        }

    external_result: dict[str, Any] | None = None

    if intent.get("requires_external_api"):
        entities = intent.get("entities") or {}
        reference_id = entities.get("reference_id")

        if reference_id:
            result = await call_mcp_tool(
                "fetch_external_status",
                {
                    "reference_id": reference_id,
                },
            )

            if isinstance(result, dict):
                external_result = result
            else:
                external_result = {
                    "ok": False,
                    "error": "Unexpected external tool result format.",
                    "data": None,
                }
        else:
            external_result = {
                "ok": False,
                "error": "The user requested an external lookup, but no reference ID was found.",
                "data": None,
            }

    return ToolOrchestrationResult(
        intent=intent,
        external_result=external_result,
    )