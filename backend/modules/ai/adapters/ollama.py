"""
Ollama adapter - Supporto per modelli locali via Ollama API.
https://ollama.com/
"""

import json
import os
import requests
import logging
from typing import Dict, List, Any

from .base import LLMAdapter, LLMResponse, ToolCall

logger = logging.getLogger(__name__)


class OllamaAdapter(LLMAdapter):
    """
    Adapter per Ollama API locale.
    Default: http://localhost:11434
    """

    def __init__(
        self,
        base_url: str = None,
        default_model: str = "llama3",
    ):
        self.base_url = base_url or os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        self.default_model = default_model

    @property
    def provider_name(self) -> str:
        return "ollama"

    def chat(
        self,
        messages: List[Dict],
        tools: List[Dict] = None,
        model: str = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        **kwargs,
    ) -> LLMResponse:
        """Invia richiesta a Ollama."""
        url = f"{self.base_url}/api/chat"

        payload = {
            "model": model or self.default_model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }

        if tools:
            # Ollama supporta tools in versioni recenti (>= 0.1.37)
            payload["tools"] = tools

        try:
            response = requests.post(
                url, json=payload, timeout=kwargs.get("timeout", 120)
            )

            if response.status_code != 200:
                logger.error(
                    f"Ollama error: {response.status_code} - {response.text}"
                )
                return LLMResponse(
                    content=f"Ollama API Error: {response.status_code}",
                    raw={"error": response.text},
                )

            data = response.json()
            return self._parse_response(data)

        except Exception as e:
            logger.error(f"Ollama exception: {e}")
            return LLMResponse(content=str(e), raw={"error": str(e)})

    def _parse_response(self, data: Dict) -> LLMResponse:
        """Parsa la risposta Ollama."""
        try:
            message = data.get("message", {})
            content = message.get("content")

            # Ollama tool calls
            tool_calls = []
            raw_tool_calls = message.get("tool_calls", [])
            for tc in raw_tool_calls:
                func = tc.get("function", {})
                tool_calls.append(
                    ToolCall(
                        name=func.get("name"),
                        arguments=func.get("arguments", {}),
                        tool_id=None # Ollama doesn't always provide tool_id
                    )
                )

            return LLMResponse(
                content=content,
                tool_calls=tool_calls,
                stop_reason=data.get("done_reason"),
                raw=data,
            )
        except Exception as e:
            logger.error(f"Error parsing Ollama response: {e}")
            return LLMResponse(content="Error parsing response", raw=data)

    def extract_tool_calls(self, response_data: Dict) -> List[ToolCall]:
        # Implementato in _parse_response per Ollama
        return []

    def format_tools(self, tools: List[Dict]) -> List[Dict]:
        """Ollama usa il formato OpenAI per i tools."""
        from backend.modules.ai.tool_registry import tool_registry
        return tool_registry.to_openai_format(tools)


ollama_adapter = OllamaAdapter()
