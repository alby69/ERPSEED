"""
Ollama adapter - For local LLM inference.
https://github.com/ollama/ollama
"""

import requests
import logging
from typing import Dict, List

from .base_adapter import BaseLLMAdapter
from ..domain.ports.llm_port import ChatCompletion

logger = logging.getLogger(__name__)


class OllamaAdapter(BaseLLMAdapter):
    """Adapter for Ollama local API."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        default_model: str = "llama3",
    ):
        super().__init__(None, default_model)
        self.base_url = base_url

    @property
    def name(self) -> str:
        return "ollama"

    def chat(
        self,
        messages: List[Dict],
        tools: List[Dict] = None,
        model: str = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        **kwargs,
    ) -> ChatCompletion:
        url = f"{self.base_url}/api/chat"

        payload = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": temperature,
            "stream": False,
        }

        if "options" in kwargs:
            payload["options"] = kwargs["options"]

        try:
            response = requests.post(
                url, json=payload, timeout=kwargs.get("timeout", 120)
            )

            if response.status_code != 200:
                logger.error(f"Ollama error: {response.status_code} - {response.text}")
                return self._error_response(f"API Error: {response.status_code}")

            data = response.json()
            return self._parse_response(data)

        except requests.exceptions.ConnectionError:
            return self._error_response("Cannot connect to Ollama. Is it running?")
        except requests.Timeout:
            return self._error_response("Request timeout")
        except Exception as e:
            logger.error(f"Ollama exception: {e}")
            return self._error_response(str(e))

    def _parse_response(self, data: Dict) -> ChatCompletion:
        try:
            message = data.get("message", {})

            return ChatCompletion(
                content=message.get("content"),
                tool_calls=self.extract_tool_calls(message),
                finish_reason=data.get("done_reason"),
                model=data.get("model"),
                raw=data,
            )
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            return self._error_response("Error parsing response")

    def extract_tool_calls(self, response_data: Dict) -> List:
        return []

    def list_models(self) -> List[Dict]:
        url = f"{self.base_url}/api/tags"

        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json().get("models", [])
        except Exception as e:
            logger.error(f"Error listing models: {e}")

        return []


ollama_adapter = OllamaAdapter()
