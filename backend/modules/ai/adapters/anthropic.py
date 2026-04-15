"""
Anthropic Claude adapter.
https://docs.anthropic.com/en/docs/api-overview
"""

import json
import os
import requests
import logging
from typing import Dict, List, Any

from .base import LLMAdapter, LLMResponse, ToolCall

logger = logging.getLogger(__name__)


class AnthropicAdapter(LLMAdapter):
    """
    Adapter per Anthropic Claude API.
    Supporta Claude 3.5 Sonnet, Claude 3 Opus, Haiku, etc.
    """

    API_URL = "https://api.anthropic.com/v1/messages"
    API_VERSION = "2023-06-01"

    DEFAULT_MODELS = {
        "sonnet": "claude-sonnet-4-20250514",
        "opus": "claude-opus-4-6-20250514",
        "haiku": "claude-haiku-3-5-20250514",
    }

    def __init__(
        self, api_key: str = None, default_model: str = "claude-sonnet-4-20250514"
    ):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self.default_model = default_model

    @property
    def provider_name(self) -> str:
        return "anthropic"

    def chat(
        self,
        messages: List[Dict],
        tools: List[Dict] = None,
        model: str = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        **kwargs,
    ) -> LLMResponse:
        """Invia richiesta a Anthropic."""
        if not self.api_key:
            return LLMResponse(
                content="Error: ANTHROPIC_API_KEY not configured",
                raw={"error": "missing_api_key"},
            )

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": self.API_VERSION,
            "content-type": "application/json",
        }

        system_message = ""
        filtered_messages = []

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                system_message = content
            else:
                filtered_messages.append({"role": role, "content": content})

        payload = {
            "model": model or self.default_model,
            "messages": filtered_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if system_message:
            payload["system"] = system_message

        if tools:
            formatted_tools = self.format_tools(tools)
            payload["tools"] = formatted_tools

        payload.update(kwargs)

        try:
            response = requests.post(
                self.API_URL,
                headers=headers,
                json=payload,
                timeout=kwargs.get("timeout", 60),
            )

            if response.status_code != 200:
                logger.error(
                    f"Anthropic error: {response.status_code} - {response.text}"
                )
                return LLMResponse(
                    content=f"API Error: {response.status_code}",
                    raw={"error": response.text},
                )

            data = response.json()
            return self._parse_response(data)

        except requests.Timeout:
            return LLMResponse(content="Request timeout", raw={"error": "timeout"})
        except Exception as e:
            logger.error(f"Anthropic exception: {e}")
            return LLMResponse(content=str(e), raw={"error": str(e)})

    def _parse_response(self, data: Dict) -> LLMResponse:
        """Parsa la risposta Anthropic."""
        try:
            content_blocks = data.get("content", [])
            text_content = ""
            tool_calls = []

            for block in content_blocks:
                block_type = block.get("type")

                if block_type == "text":
                    text_content += block.get("text", "")

                elif block_type == "tool_use":
                    tool_name = block.get("name")
                    tool_input = block.get("input", {})
                    tool_id = block.get("id")

                    tool_calls.append(
                        ToolCall(name=tool_name, arguments=tool_input, tool_id=tool_id)
                    )

            return LLMResponse(
                content=text_content if text_content else None,
                tool_calls=tool_calls,
                stop_reason=data.get("stop_reason"),
                raw=data,
            )

        except (KeyError, IndexError) as e:
            logger.error(f"Error parsing Anthropic response: {e}")
            return LLMResponse(content="Error parsing response", raw=data)

    def extract_tool_calls(self, response_data: Dict) -> List[ToolCall]:
        """Estrae tool calls dalla risposta Anthropic."""
        tool_calls = []

        if not isinstance(response_data, dict):
            return tool_calls

        content_blocks = response_data.get("content", [])

        for block in content_blocks:
            if block.get("type") == "tool_use":
                try:
                    tool_calls.append(
                        ToolCall(
                            name=block.get("name"),
                            arguments=block.get("input", {}),
                            tool_id=block.get("id"),
                        )
                    )
                except Exception as e:
                    logger.warning(f"Error extracting tool call: {e}")
                    continue

        return tool_calls

    def format_tools(self, tools: List[Dict]) -> List[Dict]:
        """
        Anthropic usa il formato con input_schema.
        """
        from backend.modules.ai.tool_registry import tool_registry

        return tool_registry.to_anthropic_format(tools)

    def continue_conversation(
        self,
        messages: List[Dict],
        tool_results: List[Dict],
        model: str = None,
        max_tokens: int = 2000,
    ) -> LLMResponse:
        """
        Continua una conversione con i risultati dei tool.

        tool_results: [{"tool_use_id": "...", "content": "..."}]
        """
        all_messages = []

        for msg in messages:
            role = msg.get("role")
            content = msg.get("content")

            if role == "system":
                continue

            if isinstance(content, str):
                all_messages.append(
                    {"role": role, "content": [{"type": "text", "text": content}]}
                )
            else:
                all_messages.append({"role": role, "content": content})

        for result in tool_results:
            all_messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": result.get("tool_use_id"),
                            "content": result.get("content", ""),
                        }
                    ],
                }
            )

        return self.chat(
            messages=[
                {
                    "role": m["role"],
                    "content": m["content"][0]["text"]
                    if isinstance(m["content"], list)
                    and m["content"][0].get("type") == "text"
                    else str(m["content"]),
                }
                for m in all_messages
                if m.get("role") != "system"
            ],
            model=model,
            max_tokens=max_tokens,
        )


anthropic_adapter = AnthropicAdapter()
