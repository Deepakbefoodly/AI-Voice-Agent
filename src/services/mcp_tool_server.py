# src/services/mcp_tool_server.py

import re
from typing import Any

import requests
from fastmcp import FastMCP

from config import EXTERNAL_API_BASE_URL, EXTERNAL_API_KEY, EXTERNAL_API_TIMEOUT_SECONDS, MCP_TOOLS_HOST, MCP_TOOLS_PORT

mcp = FastMCP("ai-voice-agent-tools")


def _clean_text(text: str) -> str:
    return " ".join((text or "").split()).strip()


@mcp.tool
def detect_intent(text: str) -> dict[str, Any]:
    """
    Detects the user's high-level intent.

    This is intentionally deterministic and safe.
    You can later replace this with an LLM-based classifier if needed.
    """
    clean_text = _clean_text(text)
    lowered = clean_text.lower()

    if not clean_text:
        return {
            "intent": "empty_input",
            "confidence": 1.0,
            "entities": {},
            "requires_external_api": False,
        }

    tracking_match = re.search(
        r"\b(?:order|ticket|case|request)\s*(?:id|number|#)?\s*[:\-]?\s*([a-zA-Z0-9_-]+)",
        clean_text,
    )

    if tracking_match:
        return {
            "intent": "external_status_lookup",
            "confidence": 0.9,
            "entities": {
                "reference_id": tracking_match.group(1),
            },
            "requires_external_api": True,
        }

    if any(keyword in lowered for keyword in ["status", "track", "lookup", "check my"]):
        return {
            "intent": "external_status_lookup",
            "confidence": 0.7,
            "entities": {},
            "requires_external_api": True,
        }

    if any(keyword in lowered for keyword in ["summarize", "explain", "what is", "how do"]):
        return {
            "intent": "rag_question",
            "confidence": 0.75,
            "entities": {},
            "requires_external_api": False,
        }

    return {
        "intent": "general_question",
        "confidence": 0.5,
        "entities": {},
        "requires_external_api": False,
    }


@mcp.tool
def fetch_external_status(reference_id: str) -> dict[str, Any]:
    """
    Calls an external API using a whitelisted operation.

    Replace the endpoint path with the real external API route.
    """
    clean_reference_id = _clean_text(reference_id)

    if not clean_reference_id:
        return {
            "ok": False,
            "error": "Missing reference_id.",
            "data": None,
        }

    base_url = EXTERNAL_API_BASE_URL.rstrip("/")
    api_key = EXTERNAL_API_KEY
    timeout_seconds = int(EXTERNAL_API_TIMEOUT_SECONDS)

    if not base_url:
        return {
            "ok": False,
            "error": "External API base URL is not configured.",
            "data": None,
        }

    if not api_key:
        return {
            "ok": False,
            "error": "External API key is not configured.",
            "data": None,
        }

    url = f"{base_url}/status/{clean_reference_id}"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=timeout_seconds,
        )
    except requests.RequestException:
        return {
            "ok": False,
            "error": "External API request failed.",
            "data": None,
        }

    if response.status_code >= 400:
        return {
            "ok": False,
            "error": f"External API returned status code {response.status_code}.",
            "data": None,
        }

    try:
        data = response.json()
    except ValueError:
        return {
            "ok": False,
            "error": "External API returned a non-JSON response.",
            "data": None,
        }

    return {
        "ok": True,
        "error": None,
        "data": data,
    }


if __name__ == "__main__":
    host = MCP_TOOLS_HOST
    port = int(MCP_TOOLS_PORT)

    mcp.run(
        transport="http",
        host=host,
        port=port,
        path="/mcp",
    )