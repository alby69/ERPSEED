"""
Anthropic adapter - For Claude models.
https://docs.anthropic.com/
"""

import os
import requests
import logging
from typing import Dict, List

from .base_adapter import BaseLLMAdapter
from ..domain.ports.llm_port import ChatCompletion

logger = logging.getLogger(__name__)


class AnthropicAdapter(BaseLLMAdapter):
    """Adapter for Anthropic Claude API."""

    def __init__(
        self,
        api_key: str = None,
        base_url: str = "https://api.anthropic.com/v1",
        default_model: str = "claude-sonnet-4-20250514",
    ):
        super().__init__(api_key, default_model)
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.base_url = base_url

    @property
    def name(self) -> str:
        return "anthropic"

    def chat(
        self,
        messages: List[Dict],
        tools: List[Dict] = None,
        model: str = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        **kwargs,
    ) -> ChatCompletion:
        url = f"{self.base_url}/messages"

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if tools:
            payload["tools"] = tools

        payload.update(kwargs)

        try:
            response = requests.post(
                url, headers=headers, json=payload, timeout=kwargs.get("timeout", 60)
            )

            if response.status_code != 200:
                logger.error(
                    f"Anthropic error: {response.status_code} - {response.text}"
                )
                return self._error_response(f"API Error: {response.status_code}")

            data = response.json()
            return self._parse_response(data)

        except requests.Timeout:
            return self._error_response("Request timeout")
        except Exception as e:
            logger.error(f"Anthropic exception: {e}")
            return self._error_response(str(e))

    def _parse_response(self, data: Dict) -> ChatCompletion:
        try:
            content_blocks = data.get("content", [])

            content_parts = []
            tool_calls = []

            for block in content_blocks:
                if block.get("type") == "text":
                    content_parts.append(block.get("text", ""))
                elif block.get("type") == "tool_use":
                    tool_calls.append(block)

            content = "\n".join(content_parts)

            if tool_calls:
                parsed_calls = []
                for tc in tool_calls:
                    parsed_calls.append(
                        {
                            "id": tc.get("id"),
                            "function": {
                                "name": tc.get("name"),
                                "arguments": tc.get("input", {}),
                            },
                        }
                    )
                tool_calls = self._parse_tool_calls(parsed_calls)

            return ChatCompletion(
                content=content,
                tool_calls=tool_calls,
                finish_reason=data.get("stop_reason"),
                model=data.get("model"),
                raw=data,
            )
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            return self._error_response("Error parsing response")

    def extract_tool_calls(self, response_data: Dict) -> List:
        return []


anthropic_adapter = AnthropicAdapter()
