"""
OpenAI adapter - Supporto nativo per modelli GPT.
https://platform.openai.com/docs/api-reference
"""

import json
import os
import requests
import logging
from typing import Dict, List, Any

from .base import LLMAdapter, LLMResponse, ToolCall

logger = logging.getLogger(__name__)


class OpenAIAdapter(LLMAdapter):
    """
    Adapter per OpenAI API ufficiale.
    """

    def __init__(
        self,
        api_key: str = None,
        base_url: str = "https://api.openai.com/v1",
        default_model: str = "gpt-4o",
    ):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.base_url = base_url
        self.default_model = default_model

    @property
    def provider_name(self) -> str:
        return "openai"

    def chat(
        self,
        messages: List[Dict],
        tools: List[Dict] = None,
        model: str = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        **kwargs,
    ) -> LLMResponse:
        """Invia richiesta a OpenAI."""
        if not self.api_key:
            return LLMResponse(content="OpenAI API Key not configured", raw={"error": "no_api_key"})

        url = f"{self.base_url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
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
            payload["tool_choice"] = "auto"

        try:
            response = requests.post(
                url, headers=headers, json=payload, timeout=kwargs.get("timeout", 60)
            )

            if response.status_code != 200:
                logger.error(
                    f"OpenAI error: {response.status_code} - {response.text}"
                )
                return LLMResponse(
                    content=f"API Error: {response.status_code}",
                    raw={"error": response.text},
                )

            data = response.json()
            choice = data.get("choices", [{}])[0]
            message = choice.get("message", {})

            content = message.get("content")
            tool_calls = self.extract_tool_calls(message)

            return LLMResponse(
                content=content,
                tool_calls=tool_calls,
                stop_reason=choice.get("finish_reason"),
                raw=data,
            )

        except Exception as e:
            logger.error(f"OpenAI exception: {e}")
            return LLMResponse(content=str(e), raw={"error": str(e)})

    def extract_tool_calls(self, message: Dict) -> List[ToolCall]:
        """Estrae tool calls nel formato OpenAI."""
        tool_calls = []
        raw_tool_calls = message.get("tool_calls", [])

        for tc in raw_tool_calls:
            try:
                func = tc.get("function", {})
                tool_calls.append(
                    ToolCall(
                        name=func.get("name"),
                        arguments=json.loads(func.get("arguments", "{}")),
                        tool_id=tc.get("id")
                    )
                )
            except Exception:
                continue

        return tool_calls

    def format_tools(self, tools: List[Dict]) -> List[Dict]:
        from backend.modules.ai.tool_registry import tool_registry
        return tool_registry.to_openai_format(tools)


openai_adapter = OpenAIAdapter()
