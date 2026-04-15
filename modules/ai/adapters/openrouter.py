"""
OpenRouter adapter - Supporta moltissimi modelli LLM.
https://openrouter.ai/docs/api
"""

import json
import os
import requests
import logging
from typing import Dict, List, Any

from .base import LLMAdapter, LLMResponse, ToolCall

logger = logging.getLogger(__name__)


class OpenRouterAdapter(LLMAdapter):
    """
    Adapter per OpenRouter API.
    Supporta: DeepSeek, Anthropic, OpenAI, Google, e molti altri.
    """

    def __init__(
        self,
        api_key: str = None,
        base_url: str = "https://openrouter.ai/api/v1",
        default_model: str = "deepseek/deepseek-chat-v3-0324",
    ):
        self.api_key = api_key or os.environ.get(
            "OPENROUTER_API_KEY",
            "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",
        )
        self.base_url = base_url
        self.default_model = default_model

    @property
    def provider_name(self) -> str:
        return "openrouter"

    def chat(
        self,
        messages: List[Dict],
        tools: List[Dict] = None,
        model: str = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        **kwargs,
    ) -> LLMResponse:
        """Invia richiesta a OpenRouter."""
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
                return LLMResponse(
                    content=f"API Error: {response.status_code}",
                    raw={"error": response.text},
                )

            data = response.json()
            return self._parse_response(data)

        except requests.Timeout:
            return LLMResponse(content="Request timeout", raw={"error": "timeout"})
        except Exception as e:
            logger.error(f"OpenRouter exception: {e}")
            return LLMResponse(content=str(e), raw={"error": str(e)})

    def _parse_response(self, data: Dict) -> LLMResponse:
        """Parsa la risposta OpenRouter."""
        try:
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
        except (KeyError, IndexError) as e:
            logger.error(f"Error parsing OpenRouter response: {e}")
            return LLMResponse(content="Error parsing response", raw=data)

    def extract_tool_calls(self, response_data: Dict) -> List[ToolCall]:
        """Estrae tool calls dalla risposta OpenRouter."""
        tool_calls = []

        if not isinstance(response_data, dict):
            return tool_calls

        message = response_data.get("message", {})
        raw_tool_calls = message.get("tool_calls", [])

        for tc in raw_tool_calls:
            try:
                func = tc.get("function", {})
                name = func.get("name")
                arguments_str = func.get("arguments", "{}")

                if isinstance(arguments_str, str):
                    arguments = json.loads(arguments_str)
                else:
                    arguments = arguments_str

                tool_calls.append(
                    ToolCall(name=name, arguments=arguments, tool_id=tc.get("id"))
                )
            except (json.JSONDecodeError, AttributeError) as e:
                logger.warning(f"Error parsing tool call: {e}")
                continue

        return tool_calls

    def format_tools(self, tools: List[Dict]) -> List[Dict]:
        """OpenRouter usa il formato OpenAI."""
        from modules.ai.tool_registry import tool_registry

        return tool_registry.to_openai_format(tools)

    def list_models(self) -> List[Dict]:
        """Lista modelli disponibili."""
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
