"""
OpenRouter adapter - Supports many LLM models.
https://openrouter.ai/docs/api
"""

import os
import requests
import logging
from typing import Dict, List

from .base_adapter import BaseLLMAdapter
from ..domain.ports.llm_port import ChatCompletion

logger = logging.getLogger(__name__)


class OpenRouterAdapter(BaseLLMAdapter):
    """Adapter for OpenRouter API."""

    def __init__(
        self,
        api_key: str = None,
        base_url: str = "https://openrouter.ai/api/v1",
        default_model: str = "deepseek/deepseek-chat-v3-0324",
    ):
        super().__init__(api_key, default_model)
        self.api_key = api_key or os.environ.get(
            "OPENROUTER_API_KEY",
            "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",
        )
        self.base_url = base_url

    @property
    def name(self) -> str:
        return "openrouter"

    def chat(
        self,
        messages: List[Dict],
        tools: List[Dict] = None,
        model: str = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        **kwargs,
    ) -> ChatCompletion:
        url = f"{self.base_url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://flaskerp.local",
            "X-Title": "FlaskERP AI Assistant",
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

        payload.update(kwargs)

        try:
            response = requests.post(
                url, headers=headers, json=payload, timeout=kwargs.get("timeout", 60)
            )

            if response.status_code != 200:
                logger.error(
                    f"OpenRouter error: {response.status_code} - {response.text}"
                )
                return self._error_response(f"API Error: {response.status_code}")

            data = response.json()
            return self._parse_response(data)

        except requests.Timeout:
            return self._error_response("Request timeout")
        except Exception as e:
            logger.error(f"OpenRouter exception: {e}")
            return self._error_response(str(e))

    def _parse_response(self, data: Dict) -> ChatCompletion:
        try:
            choice = data.get("choices", [{}])[0]
            message = choice.get("message", {})

            content = message.get("content")
            tool_calls = self.extract_tool_calls(message)

            return ChatCompletion(
                content=content,
                tool_calls=tool_calls,
                finish_reason=choice.get("finish_reason"),
                model=data.get("model"),
                raw=data,
            )
        except (KeyError, IndexError) as e:
            logger.error(f"Error parsing response: {e}")
            return self._error_response("Error parsing response")

    def extract_tool_calls(self, response_data: Dict) -> List:
        if not isinstance(response_data, dict):
            return []

        message = response_data.get("message", {})
        raw_tool_calls = message.get("tool_calls", [])

        return self._parse_tool_calls(raw_tool_calls)

    def format_tools(self, tools: List[Dict]) -> List[Dict]:
        return tools

    def list_models(self) -> List[Dict]:
        url = f"{self.base_url}/models"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json().get("data", [])
        except Exception as e:
            logger.error(f"Error listing models: {e}")

        return []


openrouter_adapter = OpenRouterAdapter()
